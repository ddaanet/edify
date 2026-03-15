"""Render STATUS output sections from parsed session data."""

from __future__ import annotations

from claudeutils.validation.task_parsing import ParsedTask


def render_next(tasks: list[ParsedTask]) -> str:
    """Render the Next: block for the first eligible pending task.

    Eligible: checkbox ``" "``, no worktree_marker.
    Skips completed (x), blocked (!), failed (†), canceled (-), and
    tasks with worktree markers.

    Returns empty string if no eligible task found.
    """
    for task in tasks:
        if task.checkbox != " ":
            continue
        if task.worktree_marker is not None:
            continue

        model = task.model or "sonnet"
        restart = "yes" if task.restart else "no"
        command = task.command or ""

        return (
            f"Next: {task.name}\n  `{command}`\n  Model: {model} | Restart: {restart}"
        )

    return ""


def render_pending(
    tasks: list[ParsedTask],
    plan_states: dict[str, str],
) -> str:
    """Render the In-tree: section listing pending tasks.

    Filters to pending (checkbox ``" "``). Non-default model shown in parens.
    Plan status shown as nested line if available.
    """
    pending = [t for t in tasks if t.checkbox == " "]
    if not pending:
        return ""

    lines = ["In-tree:"]
    for task in pending:
        model_suffix = (
            f" ({task.model})" if task.model and task.model != "sonnet" else ""
        )
        lines.append(f"- {task.name}{model_suffix}")
        if task.plan_dir and task.plan_dir in plan_states:
            lines.append(
                f"  - Plan: {task.plan_dir} | Status: {plan_states[task.plan_dir]}"
            )
    return "\n".join(lines)


def render_worktree(tasks: list[ParsedTask]) -> str:
    """Render the Worktree: section listing worktree tasks with markers."""
    if not tasks:
        return ""

    lines = ["Worktree:"]
    for task in tasks:
        marker = task.worktree_marker or ""
        model_suffix = (
            f" ({task.model})" if task.model and task.model != "sonnet" else ""
        )
        if marker:
            lines.append(f"- {task.name}{model_suffix} → {marker}")
        else:
            lines.append(f"- {task.name}{model_suffix}")
    return "\n".join(lines)


def render_unscheduled(
    all_plans: dict[str, str],
    task_plan_dirs: set[str],
) -> str:
    """Render Unscheduled Plans section.

    Excludes plans with status ``delivered`` and plans associated to tasks.
    Sorted alphabetically.
    """
    orphans = {
        name: status
        for name, status in all_plans.items()
        if name not in task_plan_dirs and status != "delivered"
    }
    if not orphans:
        return ""

    lines = ["Unscheduled Plans:"]
    lines.extend(f"- {name} — {orphans[name]}" for name in sorted(orphans))
    return "\n".join(lines)
