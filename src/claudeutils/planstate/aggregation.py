"""Aggregation module for planstate.

Parsing and combining planning artifacts.
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

from claudeutils.planstate.inference import list_plans
from claudeutils.planstate.models import PlanState
from claudeutils.worktree.session import extract_task_blocks


class TreeInfo(NamedTuple):
    """Information about a git worktree.

    Attributes:
        path: Absolute path to worktree directory
        branch: Git branch name (refs/heads/ prefix stripped)
        is_main: True if this is the main repository (not a worktree)
        slug: Worktree slug (basename of path), None for main tree
        latest_commit_timestamp: Unix epoch timestamp (seconds) of latest commit
    """

    path: str
    branch: str
    is_main: bool
    slug: str | None
    latest_commit_timestamp: int = 0


def _parse_worktree_list(output: str) -> list[TreeInfo]:
    """Parse git worktree list --porcelain output into TreeInfo objects.

    Args:
        output: git worktree list --porcelain format output

    Returns:
        List of TreeInfo objects with path, branch, is_main, slug, and
        latest_commit_timestamp fields. Branch ref is stripped of
        "refs/heads/" prefix.
        First tree is marked as main (is_main=True, slug=None).
        Other trees have is_main=False and slug extracted from path basename.
        Latest commit timestamp is fetched for each tree.
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
        # Fetch latest commit timestamp for this tree
        _, timestamp = _latest_commit(Path(path))

        if idx == 0:
            # First tree is main
            result.append(
                TreeInfo(
                    path=path,
                    branch=branch,
                    is_main=True,
                    slug=None,
                    latest_commit_timestamp=timestamp,
                )
            )
        else:
            # Other trees have slug extracted from path basename
            slug = Path(path).name
            result.append(
                TreeInfo(
                    path=path,
                    branch=branch,
                    is_main=False,
                    slug=slug,
                    latest_commit_timestamp=timestamp,
                )
            )

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


def _task_summary(tree_path: Path) -> str | None:
    """Extract first pending task name from session.md.

    Args:
        tree_path: Path to git repository

    Returns:
        Task name (string) if pending task exists, None otherwise.
        Returns None if session.md doesn't exist or has no Pending Tasks.
    """
    session_path = tree_path / "agents" / "session.md"

    if not session_path.exists():
        return None

    content = session_path.read_text()
    blocks = extract_task_blocks(content, section="Pending Tasks")

    if not blocks:
        return None

    return blocks[0].name


@dataclass
class AggregatedStatus:
    """Aggregated status from multiple worktrees."""

    plans: list[PlanState]
    trees: list[TreeInfo] = field(default_factory=list)


def aggregate_trees(repo_root: Path) -> AggregatedStatus:
    """Discover plans across all worktrees and aggregate into a single result.

    Args:
        repo_root: Path to the main repository root

    Returns:
        AggregatedStatus with aggregated plans list (deduplicated by plan name,
        main tree plans override worktree plans on conflict) and trees list
        sorted by latest_commit_timestamp in descending order.
    """
    # Get list of all worktrees
    result = subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return AggregatedStatus(plans=[], trees=[])

    trees = _parse_worktree_list(result.stdout)

    # Sort trees by latest_commit_timestamp in descending order
    sorted_trees = sorted(trees, key=lambda t: t.latest_commit_timestamp, reverse=True)

    # Discover plans from each tree, deduplicated by plan name
    # Main tree plans override worktree plans on conflict
    plans_dict = {}

    # Collect worktree plans first
    for tree in trees:
        if tree.is_main:
            continue
        tree_path = Path(tree.path)
        plans_dir = tree_path / "plans"
        tree_plans = list_plans(plans_dir)
        for plan in tree_plans:
            plan.tree_path = tree.path
            if plan.name not in plans_dict:
                plans_dict[plan.name] = plan

    # Override with main tree plans (priority)
    for tree in trees:
        if not tree.is_main:
            continue
        tree_path = Path(tree.path)
        plans_dir = tree_path / "plans"
        tree_plans = list_plans(plans_dir)
        for plan in tree_plans:
            plan.tree_path = tree.path
            plans_dict[plan.name] = plan

    # Convert dict to sorted list
    plans = sorted(plans_dict.values(), key=lambda p: p.name)
    return AggregatedStatus(plans=plans, trees=sorted_trees)
