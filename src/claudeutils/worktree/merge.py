"""Worktree merge operations."""

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import click

from claudeutils.planstate.inference import _parse_lifecycle_status
from claudeutils.worktree.git_ops import _git, _is_branch_merged, wt_path
from claudeutils.worktree.merge_state import (
    _detect_merge_state,
    _recover_untracked_file_collision,
)
from claudeutils.worktree.remerge import remerge_learnings_md, remerge_session_md
from claudeutils.worktree.resolve import resolve_learnings_md, resolve_session_md


def _append_lifecycle_delivered(plans_dir: Path) -> None:
    """Append delivered entry to lifecycle.md for reviewed plans."""
    if not plans_dir.exists():
        return
    today = datetime.now(UTC).date().isoformat()
    for plan_dir in sorted(plans_dir.iterdir()):
        if not plan_dir.is_dir():
            continue
        status = _parse_lifecycle_status(plan_dir)
        if status != "reviewed":
            continue
        lifecycle_file = plan_dir / "lifecycle.md"
        with lifecycle_file.open("a") as f:
            f.write(f"{today} delivered — _worktree merge\n")


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


def _format_conflict_report(conflicts: list[str], slug: str) -> str:
    """Format conflict report: status codes, diff stats, divergence, hint."""
    lines = [f"Conflicts in merge of `{slug}`:"]

    for conflict_file in conflicts:
        status = _git("status", "--short", "--", conflict_file, check=False)
        status_code = status[:2] if status else "??"
        lines.append(f"  {status_code} {conflict_file}")

    lines.append("")

    for conflict_file in conflicts:
        stat = _git(
            "diff", "--stat", "HEAD", "MERGE_HEAD", "--", conflict_file, check=False
        )
        if stat:
            lines.extend(f"  {sl}" for sl in stat.split("\n") if sl)

    lines.append("")

    ahead = _git("rev-list", "--count", f"HEAD..{slug}", check=False)
    behind = _git("rev-list", "--count", f"{slug}..HEAD", check=False)
    lines.append(
        f"Branch: {ahead} commits ahead, Main: {behind} commits ahead since merge-base"
    )

    lines.append("")
    lines.append(
        f"Resolve conflicts, git add, then re-run: claudeutils _worktree merge {slug}"
    )

    return "\n".join(lines)


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

        # Try submodule merge; if it conflicts, leave MERGE_HEAD in place and return
        merge_result = subprocess.run(
            ["git", "-C", "agent-core", "merge", "--no-edit", wt_commit],
            capture_output=True,
            check=False,
        )
        if merge_result.returncode != 0:
            return

        _git("add", "agent-core")

        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "agent-core"],
            check=False,
        )
        if result.returncode != 0:
            _git("commit", "-m", f"🔀 Merge agent-core from {slug}")


def _auto_resolve_known_conflicts(conflicts: list[str], slug: str) -> list[str]:
    """Auto-resolve known conflicts: agent-core (ours), session.md, learnings.md."""
    if "agent-core" in conflicts:
        _git("checkout", "--ours", "agent-core")
        _git("add", "agent-core")
        conflicts = [c for c in conflicts if c != "agent-core"]
    conflicts = resolve_session_md(conflicts, slug=slug)
    return resolve_learnings_md(conflicts)


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
        # Detect untracked file collision and attempt recovery
        is_untracked_error = "untracked working tree file" in stderr.lower()
        is_local_changes_error = (
            "your local changes to the following files would be overwritten by merge"
            in stderr.lower()
        )
        if is_untracked_error or is_local_changes_error:
            if not _recover_untracked_file_collision(slug, result):
                raise SystemExit(1)
            # After recovery, check if merge started
            merge_head = subprocess.run(
                ["git", "rev-parse", "--verify", "MERGE_HEAD"],
                capture_output=True,
                check=False,
            )
            if merge_head.returncode != 0:
                # Merge still failed
                click.echo(f"Merge failed: {stderr}")
                raise SystemExit(1)
        else:
            click.echo(f"Merge failed: {stderr}")
            raise SystemExit(1)

    conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split("\n")
    conflicts = [c for c in conflicts if c.strip()]
    conflicts = _auto_resolve_known_conflicts(conflicts, slug)

    if conflicts:
        click.echo(_format_conflict_report(conflicts, slug))
        raise SystemExit(3)


def _validate_merge_result(slug: str) -> None:
    """Validate merge result: verify slug is ancestor of HEAD.

    Also emits diagnostic warning if HEAD has fewer than 2 parents.
    """
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", slug, "HEAD"],
        check=False,
    )

    if result.returncode != 0:
        click.echo(f"Error: branch {slug} not fully merged")
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
        click.echo(f"Warning: merge commit has {parent_count} parent(s)")


def _phase4_merge_commit_and_precommit(slug: str) -> None:
    """Phase 4: Commit merge and run precommit validation.

    If MERGE_HEAD exists (merge in progress), always commit even if no staged
    changes (use --allow-empty). Otherwise, only commit if staged changes exist.
    """
    remerge_learnings_md()
    remerge_session_md(slug)

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
            click.echo("Error: merge state lost — MERGE_HEAD absent, branch not merged")
            raise SystemExit(2)
        _git("commit", "-m", f"🔀 Merge {slug}")
    elif not _is_branch_merged(slug):
        click.echo("Error: nothing to commit and branch not merged")
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
        click.echo(precommit_result.stdout)
        click.echo(precommit_result.stderr)
        raise SystemExit(1)

    submodule_path = Path("agent-core")
    if submodule_path.exists() and (submodule_path / ".git").exists():
        sub_merge_head = subprocess.run(
            ["git", "-C", "agent-core", "rev-parse", "--verify", "MERGE_HEAD"],
            capture_output=True,
            check=False,
        )
        if sub_merge_head.returncode == 0:
            click.echo("Submodule agent-core has unresolved merge conflict")
            click.echo("Resolve in agent-core/, then re-run merge")
            raise SystemExit(3)


def merge(slug: str) -> None:
    """Merge worktree branch: validate, resolve submodule, merge parent."""
    state = _detect_merge_state(slug)

    if state == "merged":
        _phase1_validate_clean_trees(slug)
        _phase2_resolve_submodule(slug)
        _phase4_merge_commit_and_precommit(slug)
    elif state == "parent_resolved":
        _phase4_merge_commit_and_precommit(slug)
    elif state == "parent_conflicts":
        conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split(
            "\n"
        )
        conflicts = [c for c in conflicts if c.strip()]
        conflicts = _auto_resolve_known_conflicts(conflicts, slug)
        if conflicts:
            click.echo(_format_conflict_report(conflicts, slug))
            raise SystemExit(3)
        _phase4_merge_commit_and_precommit(slug)
    elif state == "submodule_conflicts":
        _phase3_merge_parent(slug)
        _phase4_merge_commit_and_precommit(slug)
    else:  # clean
        _phase1_validate_clean_trees(slug)
        _phase2_resolve_submodule(slug)
        _phase3_merge_parent(slug)
        _phase4_merge_commit_and_precommit(slug)

    _append_lifecycle_delivered(Path("plans"))
