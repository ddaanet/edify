"""Worktree merge operations."""

import subprocess
from pathlib import Path

import click

from claudeutils.worktree.resolve import (
    resolve_learnings_md,
    resolve_session_md,
)
from claudeutils.worktree.utils import _git, _is_branch_merged, wt_path


def _format_git_error(e: subprocess.CalledProcessError) -> str:
    """Format git error with command, exit code, and stderr."""
    cmd_str = " ".join(str(arg) for arg in e.cmd)
    stderr = e.stderr.rstrip("\n") if e.stderr else "(no error output)"
    return (
        f"Git command failed: {cmd_str}\n"
        f"Exit code: {e.returncode}\n"
        f"{stderr}\n\n"
        f"Resolve the issue and retry the merge."
    )


def _check_clean_for_merge(
    path: Path | None = None,
    exempt_paths: set[str] | None = None,
    label: str = "main",
) -> None:
    """Verify clean tree for merge."""
    parent_cmd = ["-C", str(path)] if path else []
    parent_cmd.extend(["status", "--porcelain", "--untracked-files=no"])
    parent = _git(*parent_cmd, check=False)

    if exempt_paths:
        dirty = [
            line
            for line in parent.split("\n")
            if line and not any(p in line for p in exempt_paths)
        ]
    else:
        dirty = [line for line in parent.split("\n") if line.strip()]

    if dirty:
        suffix = ": uncommitted changes would be lost" if not exempt_paths else ""
        click.echo(f"Clean tree required for merge ({label}{suffix})")
        raise SystemExit(1)

    submodule_path = (path / "agent-core") if path else Path("agent-core")
    if not (submodule_path.exists() and (submodule_path / ".git").exists()):
        return
    submodule = _git(
        "-C",
        str(submodule_path),
        "status",
        "--porcelain",
        "--untracked-files=no",
        check=False,
    )
    if submodule.strip():
        click.echo(f"Clean tree required for merge ({label} submodule)")
        raise SystemExit(1)


def _phase1_validate_clean_trees(slug: str) -> None:
    """Phase 1: Verify branch exists and clean trees (OURS and THEIRS)."""
    r = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        click.echo(f"Branch {slug} not found")
        raise SystemExit(2)

    worktree_dir = wt_path(slug)
    if not worktree_dir.exists():
        click.echo("Worktree directory not found, merging branch only")

    _check_clean_for_merge(
        exempt_paths={
            "agents/session.md",
            "agents/learnings.md",
            "agent-core",
        }
    )
    _check_clean_for_merge(path=wt_path(slug), label="worktree")


def _phase2_resolve_submodule(slug: str) -> None:
    """Phase 2: Resolve submodule if worktree commit differs from local."""
    wt_ls_output = _git("ls-tree", slug, "--", "agent-core", check=False)
    if not wt_ls_output:
        return

    wt_commit = wt_ls_output.split()[2]
    local_commit = _git("-C", "agent-core", "rev-parse", "HEAD", check=False)

    if wt_commit == local_commit:
        return

    result = subprocess.run(
        [
            "git",
            "-C",
            "agent-core",
            "merge-base",
            "--is-ancestor",
            wt_commit,
            local_commit,
        ],
        check=False,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "-C", "agent-core", "cat-file", "-e", wt_commit],
            check=False,
        )
        if result.returncode != 0:
            wt_agent_core = wt_path(slug) / "agent-core"
            _git("-C", "agent-core", "fetch", str(wt_agent_core), "HEAD")

        _git("-C", "agent-core", "merge", "--no-edit", wt_commit)
        _git("add", "agent-core")

        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "agent-core"],
            check=False,
        )
        if result.returncode != 0:
            _git("commit", "-m", f"🔀 Merge agent-core from {slug}")


def _phase3_merge_parent(slug: str) -> None:
    """Phase 3: Initiate parent merge and auto-resolve known conflicts."""
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return

    # Distinguish merge conflict (MERGE_HEAD exists) from merge abort
    merge_head = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )
    if merge_head.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "unknown error"
        click.echo(f"Merge failed: {stderr}", err=True)
        raise SystemExit(1)

    conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split("\n")
    conflicts = [c for c in conflicts if c.strip()]

    if "agent-core" in conflicts:
        _git("checkout", "--ours", "agent-core")
        _git("add", "agent-core")
        conflicts = [c for c in conflicts if c != "agent-core"]

    conflicts = resolve_session_md(conflicts, slug=slug)
    conflicts = resolve_learnings_md(conflicts)

    if conflicts:
        _git("merge", "--abort")
        _git("clean", "-fd")
        conflict_list = ", ".join(conflicts)
        click.echo(f"Merge aborted: conflicts in {conflict_list}")
        raise SystemExit(1)


def _validate_merge_result(slug: str) -> None:
    """Validate merge result: verify slug is ancestor of HEAD.

    Also emits diagnostic warning if HEAD has fewer than 2 parents.
    """
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", slug, "HEAD"],
        check=False,
    )

    if result.returncode != 0:
        click.echo(f"Error: branch {slug} not fully merged", err=True)
        raise SystemExit(2)

    parent_output = subprocess.run(
        ["git", "cat-file", "-p", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    parent_count = len(
        [line for line in parent_output.split("\n") if line.startswith("parent ")]
    )
    if parent_count < 2:
        click.echo(f"Warning: merge commit has {parent_count} parent(s)", err=True)


def _phase4_merge_commit_and_precommit(slug: str) -> None:
    """Phase 4: Commit merge and run precommit validation.

    If MERGE_HEAD exists (merge in progress), always commit even if no staged
    changes (use --allow-empty). Otherwise, only commit if staged changes exist.
    """
    merge_in_progress = (
        subprocess.run(
            ["git", "rev-parse", "--verify", "MERGE_HEAD"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )

    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
    )

    if merge_in_progress:
        _git("commit", "--allow-empty", "-m", f"🔀 Merge {slug}")
    elif staged_check.returncode != 0:
        if not _is_branch_merged(slug):
            click.echo(
                "Error: merge state lost — MERGE_HEAD absent, branch not merged",
                err=True,
            )
            raise SystemExit(2)
        _git("commit", "-m", f"🔀 Merge {slug}")
    elif not _is_branch_merged(slug):
        click.echo("Error: nothing to commit and branch not merged", err=True)
        raise SystemExit(2)

    _validate_merge_result(slug)

    precommit_result = subprocess.run(
        ["just", "precommit"],
        capture_output=True,
        text=True,
        check=False,
    )

    if precommit_result.returncode == 0:
        click.echo("Precommit passed")
    else:
        click.echo("Precommit failed after merge")
        click.echo(precommit_result.stderr)
        raise SystemExit(1)


def merge(slug: str) -> None:
    """Merge worktree branch: validate, resolve submodule, merge parent."""
    _phase1_validate_clean_trees(slug)
    _phase2_resolve_submodule(slug)
    _phase3_merge_parent(slug)
    _phase4_merge_commit_and_precommit(slug)
