"""Validate worktree markers in session.md.

Checks that task lines with worktree markers (→ `slug`) correspond to
actual worktrees from git worktree list.
"""

import subprocess
from pathlib import Path

from claudeutils.validation.task_parsing import parse_task_line


def parse_porcelain_slugs(porcelain_output: str) -> set[str]:
    """Extract worktree slugs from git worktree list --porcelain output.

    Excludes the main working tree (always listed first in porcelain output).
    Non-main worktrees live in a sibling ``-wt`` container directory.

    Args:
        porcelain_output: Raw output from git worktree list --porcelain.

    Returns:
        Set of worktree slugs.
    """
    paths = [
        line[len("worktree ") :]
        for line in porcelain_output.splitlines()
        if line.startswith("worktree ")
    ]
    # First entry is always the main working tree (git guarantee)
    return {Path(p).name for p in paths[1:]}


def get_worktree_slugs(worktree_slugs: set[str] | None = None) -> set[str]:
    """Get slugs from git worktree list, excluding main.

    Args:
        worktree_slugs: Optional set of slugs to use (for testing).
                       If None, queries git worktree list.

    Returns:
        Set of worktree slugs (excluding main).
    """
    if worktree_slugs is not None:
        return worktree_slugs

    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return set()

    return parse_porcelain_slugs(result.stdout)


def check_worktree_markers(
    lines: list[str],
    worktree_slugs: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate worktree markers in task lines.

    Returns (errors, warnings):
    - errors: Markers pointing to non-existent worktrees
    - warnings: Worktrees not referenced by any marker

    Args:
        lines: File content as list of lines.
        worktree_slugs: Optional set of known worktree slugs (for testing).

    Returns:
        Tuple of (error_list, warning_list).
    """
    if worktree_slugs is None:
        worktree_slugs = get_worktree_slugs()

    errors = []
    referenced_slugs = set()

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        task = parse_task_line(stripped, lineno=lineno)

        if task and task.worktree_marker:
            referenced_slugs.add(task.worktree_marker)
            if task.worktree_marker not in worktree_slugs:
                errors.append(
                    f"  line {lineno}: worktree marker not found: "
                    f"{task.worktree_marker}"
                )

    unreferenced_slugs = worktree_slugs - referenced_slugs
    warnings = [
        f"  worktree not referenced by any task: {slug}"
        for slug in sorted(unreferenced_slugs)
    ]

    return errors, warnings
