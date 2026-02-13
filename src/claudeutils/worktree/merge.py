"""Worktree merge operations."""

import subprocess
from pathlib import Path

import click

from claudeutils.worktree.utils import _git, wt_path


def _check_clean_for_merge(
    path: Path | None = None,
    exempt_paths: set[str] | None = None,
    label: str = "main",
) -> None:
    """Verify clean tree for merge.

    Args:
        path: Directory to check (None = current directory)
        exempt_paths: Paths to exempt from dirty check (None = strict mode)
        label: Location label for error messages
    """
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


def _resolve_session_md_conflict(conflicts: list[str]) -> list[str]:
    """Resolve agents/session.md conflict.

    Keep ours and extract new tasks from theirs. Returns updated conflict list
    with session.md removed if present.
    """
    if "agents/session.md" not in conflicts:
        return conflicts

    ours_content = _git("show", ":2:agents/session.md", check=False)
    theirs_content = _git("show", ":3:agents/session.md", check=False)

    ours_tasks = {
        line
        for line in ours_content.split("\n")
        if line.strip().startswith("- [ ] **") and "**" in line
    }
    theirs_tasks = {
        line
        for line in theirs_content.split("\n")
        if line.strip().startswith("- [ ] **") and "**" in line
    }

    new_tasks = theirs_tasks - ours_tasks

    if new_tasks:
        ours_lines = ours_content.split("\n")
        pending_idx = next(
            (i for i, line in enumerate(ours_lines) if "## Pending Tasks" in line), None
        )
        if pending_idx is not None:
            next_section_idx = next(
                (
                    i
                    for i in range(pending_idx + 1, len(ours_lines))
                    if ours_lines[i].startswith("## ")
                ),
                len(ours_lines),
            )
            ours_lines[next_section_idx:next_section_idx] = ["", *sorted(new_tasks)]
        else:
            ours_lines.extend(["", "## Pending Tasks", "", *sorted(new_tasks)])
        ours_content = "\n".join(ours_lines)

    Path("agents/session.md").write_text(ours_content)
    _git("add", "agents/session.md")

    return [c for c in conflicts if c != "agents/session.md"]


def _resolve_learnings_md_conflict(conflicts: list[str]) -> list[str]:
    """Resolve agents/learnings.md conflict.

    Keep ours and append theirs-only content. Returns updated conflict list with
    learnings.md removed if present.
    """
    if "agents/learnings.md" not in conflicts:
        return conflicts

    ours_content = _git("show", ":2:agents/learnings.md", check=False)
    theirs_content = _git("show", ":3:agents/learnings.md", check=False)

    ours_lines = set(ours_content.split("\n"))
    theirs_lines = theirs_content.split("\n")

    theirs_only = [line for line in theirs_lines if line not in ours_lines]

    merged = ours_content
    if theirs_only:
        merged += "\n" + "\n".join(theirs_only)

    Path("agents/learnings.md").write_text(merged)
    _git("add", "agents/learnings.md")

    return [c for c in conflicts if c != "agents/learnings.md"]


def _resolve_jobs_md_conflict(conflicts: list[str]) -> list[str]:
    """Resolve agents/jobs.md conflict.

    Keep ours (local plan status is authoritative). Returns updated conflict
    list with jobs.md removed if present.
    """
    if "agents/jobs.md" not in conflicts:
        return conflicts

    _git("checkout", "--ours", "agents/jobs.md")
    _git("add", "agents/jobs.md")
    click.echo("jobs.md conflict: kept ours (local plan status)")

    return [c for c in conflicts if c != "agents/jobs.md"]


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
            "agents/jobs.md",
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

    conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split("\n")
    conflicts = [c for c in conflicts if c.strip()]

    if "agent-core" in conflicts:
        _git("checkout", "--ours", "agent-core")
        _git("add", "agent-core")
        conflicts = [c for c in conflicts if c != "agent-core"]

    conflicts = _resolve_session_md_conflict(conflicts)
    conflicts = _resolve_learnings_md_conflict(conflicts)
    conflicts = _resolve_jobs_md_conflict(conflicts)

    if conflicts:
        _git("merge", "--abort")
        _git("clean", "-fd")
        conflict_list = ", ".join(conflicts)
        click.echo(f"Merge aborted: conflicts in {conflict_list}")
        raise SystemExit(1)


def _phase4_merge_commit_and_precommit(slug: str) -> None:
    """Phase 4: Commit merge and run precommit validation.

    If staged changes exist after merge, commit with message "🔀 Merge <slug>".
    Then run `just precommit` and handle exit code appropriately.
    """
    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
    )

    if staged_check.returncode != 0:
        _git("commit", "-m", f"🔀 Merge {slug}")

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
