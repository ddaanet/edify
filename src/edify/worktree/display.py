"""Worktree display formatting for rich ls output."""

from pathlib import Path

from edify.planstate.aggregation import TreeInfo, aggregate_trees


def _format_tree_line(tree: TreeInfo, display_name: str) -> str:
    """Format a single tree header line."""
    branch = tree.branch
    dirty_indicator = "●" if tree.is_dirty else "○"
    commits = tree.commits_since_handoff
    commit_status = f"{commits} commits since handoff" if commits > 0 else "clean"
    return f"{display_name} ({branch})  {dirty_indicator}  {commit_status}"


def format_rich_ls(main_path: str, _porcelain_output: str) -> str:
    """Format rich ls output with headers for all trees and their plans."""
    aggregated = aggregate_trees(Path(main_path))

    lines: list[str] = []

    for tree in aggregated.trees:
        display_name = "main" if tree.is_main else (tree.slug or Path(tree.path).name)
        lines.append(_format_tree_line(tree, display_name))

        for plan in aggregated.plans:
            if plan.tree_path == tree.path:
                lines.append(
                    f"  Plan: {plan.name} [{plan.status}] → {plan.next_action}"
                )
                if plan.gate:
                    lines.append(f"  Gate: {plan.gate}")

    return "\n".join(lines)
