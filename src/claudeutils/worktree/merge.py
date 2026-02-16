"""Worktree merge operations."""

import subprocess
from pathlib import Path

import click

from claudeutils.worktree.session import extract_task_blocks, find_section_bounds
from claudeutils.worktree.utils import _git, _is_branch_merged, wt_path


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

    # Extract task blocks from both sides (all pending tasks)
    # Handles both modern (with "## Pending Tasks") and legacy (tasks at root)
    ours_blocks = extract_task_blocks(ours_content)
    theirs_blocks = extract_task_blocks(theirs_content)

    # Compare by task name to find new tasks
    ours_names = {b.name for b in ours_blocks}
    new_blocks = [b for b in theirs_blocks if b.name not in ours_names]

    if new_blocks:
        bounds = find_section_bounds(ours_content, "Pending Tasks")
        ours_lines = ours_content.split("\n")

        if bounds is not None:
            # Insert full task blocks (all lines) before next section
            insertion_point = bounds[1]
            new_task_lines = []
            for block in sorted(new_blocks, key=lambda b: b.name):
                new_task_lines.extend(block.lines)

            # Ensure blank line separation before next section header.
            # Add blank line after new tasks if:
            # - next line exists and is not already blank, AND
            # - new tasks don't already end with blank line
            if (
                insertion_point < len(ours_lines)
                and ours_lines[insertion_point] != ""
                and (not new_task_lines or new_task_lines[-1] != "")
            ):
                new_task_lines.append("")

            ours_lines[insertion_point:insertion_point] = new_task_lines
        else:
            # Create Pending Tasks section if missing
            new_task_lines = []
            for block in sorted(new_blocks, key=lambda b: b.name):
                new_task_lines.extend(block.lines)
            ours_lines.extend(["", "## Pending Tasks", "", *new_task_lines])
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

    If MERGE_HEAD exists (merge in progress), always commit even if no staged
    changes (use --allow-empty). Otherwise, only commit if staged changes exist.
    Then run `just precommit` and handle exit code appropriately.
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
            import sys

            sys.stderr.write(
                "Error: merge state lost — MERGE_HEAD absent, branch not merged\n"
            )
            raise SystemExit(2)
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
