"""Aggregation module for planstate.

Parsing and combining planning artifacts.
"""

import subprocess
from pathlib import Path
from typing import NamedTuple


class TreeInfo(NamedTuple):
    """Information about a git worktree."""

    path: str
    branch: str
    is_main: bool
    slug: str | None


def _parse_worktree_list(output: str) -> list[TreeInfo]:
    """Parse git worktree list --porcelain output into TreeInfo objects.

    Args:
        output: git worktree list --porcelain format output

    Returns:
        List of TreeInfo objects with path, branch, is_main, and slug fields.
        Branch ref is stripped of "refs/heads/" prefix.
        First tree is marked as main (is_main=True, slug=None).
        Other trees have is_main=False and slug extracted from path basename.
    """
    trees = []
    lines = output.split("\n")

    current_path = None
    current_branch = None

    for line in lines:
        if line.startswith("worktree "):
            current_path = line[len("worktree ") :]
        elif line.startswith("branch "):
            ref = line[len("branch ") :]
            # Strip "refs/heads/" prefix
            if ref.startswith("refs/heads/"):
                current_branch = ref[len("refs/heads/") :]
            else:
                current_branch = ref
        elif line == "" and current_path is not None and current_branch is not None:
            trees.append((current_path, current_branch))
            current_path = None
            current_branch = None

    result = []
    for idx, (path, branch) in enumerate(trees):
        if idx == 0:
            # First tree is main
            result.append(TreeInfo(path=path, branch=branch, is_main=True, slug=None))
        else:
            # Other trees have slug extracted from path basename
            slug = Path(path).name
            result.append(TreeInfo(path=path, branch=branch, is_main=False, slug=slug))

    return result


def _commits_since_handoff(tree_path: Path) -> int:
    """Count commits since session.md was last committed.

    Args:
        tree_path: Path to git repository

    Returns:
        Number of commits after session.md anchor, or 0 if not found or on HEAD
    """
    # Find the latest commit that touched agents/session.md
    result = subprocess.run(
        [
            "git",
            "-C",
            str(tree_path),
            "log",
            "-1",
            "--format=%H",
            "--",
            "agents/session.md",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not result.stdout.strip():
        # No session.md in history
        return 0

    anchor = result.stdout.strip()

    # Count commits from anchor to HEAD
    result = subprocess.run(
        ["git", "-C", str(tree_path), "rev-list", f"{anchor}..HEAD", "--count"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 0

    try:
        return int(result.stdout.strip())
    except (ValueError, AttributeError):
        return 0


def _latest_commit(tree_path: Path) -> tuple[str, int]:
    """Get the latest commit subject and timestamp.

    Args:
        tree_path: Path to git repository

    Returns:
        Tuple of (commit subject, Unix timestamp as int)
    """
    # Get latest commit subject and timestamp
    result = subprocess.run(
        ["git", "-C", str(tree_path), "log", "-1", "--format=%s%n%ct"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return ("", 0)

    lines = result.stdout.strip().split("\n")
    if len(lines) < 2:
        return ("", 0)

    subject = lines[0]
    try:
        timestamp = int(lines[1])
    except (ValueError, IndexError):
        timestamp = 0

    return (subject, timestamp)


def _is_dirty(tree_path: Path) -> bool:
    """Check if git worktree has uncommitted changes.

    Args:
        tree_path: Path to git repository

    Returns:
        True if there are uncommitted changes (modified tracked files), False otherwise.
        Untracked files are ignored.
    """
    result = subprocess.run(
        [
            "git",
            "-C",
            str(tree_path),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return False

    return bool(result.stdout.strip())
