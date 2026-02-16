"""Aggregation module for planstate.

Parsing and combining planning artifacts.
"""

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
