"""Worktree display formatting for rich ls output."""

import subprocess
from pathlib import Path

from claudeutils.planstate.aggregation import aggregate_trees


def format_tree_header(
    display_name: str, branch: str, path: str, _main_path: str
) -> str:
    """Format tree header with slug/branch, dirty indicator, commit status."""
    clean_branch = branch.replace("refs/heads/", "") if branch else "main"

    # Dirty detection
    result = subprocess.run(
        ["git", "-C", path, "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    is_dirty = bool(result.stdout.strip())
    dirty_indicator = "●" if is_dirty else "○"

    # Commits since handoff
    session_path = Path(path) / "session.md"
    commits_count = 0
    if session_path.exists():
        result = subprocess.run(
            [
                "git",
                "-C",
                path,
                "log",
                "--oneline",
                "--follow",
                "session.md",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        if lines:
            oldest_commit = lines[-1].split()[0]
            count_result = subprocess.run(
                [
                    "git",
                    "-C",
                    path,
                    "rev-list",
                    "--count",
                    f"{oldest_commit}~1..HEAD",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if count_result.returncode == 0 and count_result.stdout.strip():
                commits_count = int(count_result.stdout.strip())

    commit_status = (
        f"{commits_count} commits since handoff" if commits_count > 0 else "clean"
    )
    return f"{display_name} ({clean_branch})  {dirty_indicator}  {commit_status}"


def _parse_worktree_entries(
    porcelain: str, main_path: str
) -> list[tuple[str, str, str]]:
    """Parse worktree list, return (slug, branch, path) excluding main."""
    if not porcelain:
        return []
    lines, entries, i = porcelain.split("\n"), [], 0
    while i < len(lines):
        if not lines[i].startswith("worktree "):
            i += 1
            continue
        path, branch, i = lines[i].split(maxsplit=1)[1], "", i + 1
        while i < len(lines) and lines[i]:
            if lines[i].startswith("branch "):
                branch = lines[i].split(maxsplit=1)[1]
            i += 1
        i += 1
        if path != main_path:
            entries.append((Path(path).name, branch, path))
    return entries


def format_rich_ls(main_path: str, porcelain_output: str) -> str:
    """Format rich ls output with headers for all trees and their plans."""
    result = subprocess.run(
        ["git", "-C", main_path, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    main_branch = result.stdout.strip() if result.returncode == 0 else "main"

    # Aggregate plans across all trees
    aggregated = aggregate_trees(Path(main_path))

    lines = [format_tree_header("main", main_branch, main_path, main_path)]

    # Add plans and gates for main tree
    for plan in aggregated.plans:
        if plan.tree_path == main_path:
            lines.append(f"  Plan: {plan.name} [{plan.status}] → {plan.next_action}")
            if plan.gate:
                lines.append(f"  Gate: {plan.gate}")

    for slug, branch, path in _parse_worktree_entries(porcelain_output, main_path):
        lines.append(format_tree_header(slug, branch, path, main_path))

        # Add plans and gates for this worktree
        for plan in aggregated.plans:
            if plan.tree_path == path:
                lines.append(
                    f"  Plan: {plan.name} [{plan.status}] → {plan.next_action}"
                )
                if plan.gate:
                    lines.append(f"  Gate: {plan.gate}")

    return "\n".join(lines)
