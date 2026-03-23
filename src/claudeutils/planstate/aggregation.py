"""Aggregation module for planstate.

Parsing and combining planning artifacts.
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

from claudeutils.planstate.inference import list_plans
from claudeutils.planstate.models import PlanState
from claudeutils.worktree.session import extract_plan_order, extract_task_blocks


class TreeInfo(NamedTuple):
    """Information about a git worktree."""

    path: str
    branch: str
    is_main: bool
    slug: str | None
    latest_commit_timestamp: int = 0
    latest_commit_subject: str = ""
    commits_since_handoff: int = 0
    is_dirty: bool = False
    task_summary: str | None = None


def _parse_worktree_list(output: str) -> list[TreeInfo]:
    """Parse git worktree list --porcelain output into TreeInfo objects."""
    trees = []
    lines = output.split("\n")

    current_path = None
    current_branch = None

    for line in lines:
        if line.startswith("worktree "):
            current_path = line[len("worktree ") :]
        elif line.startswith("branch "):
            ref = line[len("branch ") :]
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
        tree_path = Path(path)
        subject, timestamp = _latest_commit(tree_path)
        commits = _commits_since_handoff(tree_path)
        dirty = _is_dirty(tree_path)
        task = _task_summary(tree_path)

        result.append(
            TreeInfo(
                path=path,
                branch=branch,
                is_main=(idx == 0),
                slug=None if idx == 0 else tree_path.name,
                latest_commit_timestamp=timestamp,
                latest_commit_subject=subject,
                commits_since_handoff=commits,
                is_dirty=dirty,
                task_summary=task,
            )
        )

    return result


def _commits_since_handoff(tree_path: Path) -> int:
    """Count commits since the last agents/session.md commit; 0 if no anchor."""
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
        return 0

    anchor = result.stdout.strip()

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
    """Return (subject, unix_timestamp) of HEAD commit."""
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
    """Check for uncommitted tracked changes; untracked files ignored."""
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
    """Return the first pending task name from agents/session.md, or None."""
    session_path = tree_path / "agents" / "session.md"

    if not session_path.exists():
        return None

    content = session_path.read_text()
    blocks = extract_task_blocks(content, section="In-tree Tasks")

    if not blocks:
        return None

    return blocks[0].name


@dataclass
class AggregatedStatus:
    """Aggregated status from multiple worktrees."""

    plans: list[PlanState]
    trees: list[TreeInfo] = field(default_factory=list)


def aggregate_trees(repo_root: Path) -> AggregatedStatus:
    """Aggregate plans across all worktrees; each tree shows its own plan."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return AggregatedStatus(plans=[], trees=[])

    trees = _parse_worktree_list(result.stdout)
    sorted_trees = sorted(trees, key=lambda t: t.latest_commit_timestamp, reverse=True)

    plans: list[PlanState] = []

    for tree in trees:
        tree_plans = list_plans(Path(tree.path) / "plans")
        for plan in tree_plans:
            plan.tree_path = tree.path
            plans.append(plan)

    # Sort by session.md task order; unmatched plans alphabetically at end
    plan_order = _read_plan_order(trees)
    max_pos = len(plan_order)
    sorted_plans = sorted(
        plans,
        key=lambda p: (plan_order.get(p.name, max_pos), p.name),
    )
    return AggregatedStatus(plans=sorted_plans, trees=sorted_trees)


def _read_plan_order(trees: list[TreeInfo]) -> dict[str, int]:
    """Read plan ordering from main tree's session.md."""
    main_tree = next((t for t in trees if t.is_main), None)
    if not main_tree:
        return {}
    session_path = Path(main_tree.path) / "agents" / "session.md"
    if not session_path.exists():
        return {}
    return extract_plan_order(session_path.read_text())
