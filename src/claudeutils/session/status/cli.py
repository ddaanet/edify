"""CLI wiring for _status command."""

from __future__ import annotations

import os
from pathlib import Path

import click

from claudeutils.git import _fail
from claudeutils.session.parse import SessionFileError, parse_session
from claudeutils.session.status.render import (
    detect_parallel,
    render_next,
    render_pending,
    render_unscheduled,
    render_worktree,
)


@click.command(name="status", hidden=True)
def status_cmd() -> None:
    """Render STATUS output from session.md."""
    session_path = Path(os.environ.get("CLAUDEUTILS_SESSION_FILE", "agents/session.md"))

    try:
        data = parse_session(session_path)
    except SessionFileError:
        _fail(f"**Error:** Session file not found: {session_path}", code=2)

    plan_states: dict[str, str] = {}
    for task in [*data.in_tree_tasks, *data.worktree_tasks]:
        if task.plan_dir:
            plan_states.setdefault(task.plan_dir, "")

    sections: list[str] = []

    # Next task
    next_section = render_next(data.in_tree_tasks)
    if next_section:
        sections.append(next_section)

    # In-tree tasks
    pending_section = render_pending(data.in_tree_tasks, plan_states)
    if pending_section:
        sections.append(pending_section)
    else:
        sections.append("No in-tree tasks.")

    # Worktree tasks
    wt_section = render_worktree(data.worktree_tasks)
    if wt_section:
        sections.append(wt_section)

    # Unscheduled plans (placeholder — no plan discovery yet)
    task_plan_dirs = {
        t.plan_dir for t in [*data.in_tree_tasks, *data.worktree_tasks] if t.plan_dir
    }
    # Plan discovery deferred to Phase 4+
    unscheduled = render_unscheduled({}, task_plan_dirs)
    if unscheduled:
        sections.append(unscheduled)

    # Parallel detection
    parallel = detect_parallel(data.in_tree_tasks, [])
    if parallel:
        names = "\n  - ".join(parallel)
        sections.append(f"Parallel ({len(parallel)} tasks, independent):\n  - {names}")

    click.echo("\n\n".join(sections))
