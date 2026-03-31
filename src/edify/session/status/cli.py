"""CLI wiring for _status command."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import click

from edify.git import _fail, _is_dirty
from edify.planstate.inference import list_plans
from edify.session.parse import parse_session
from edify.session.status.render import (
    detect_parallel,
    render_continuation,
    render_pending,
    render_unscheduled,
    render_worktree,
)


def _check_old_section_name(content: str) -> None:
    """Reject old section name 'Pending Tasks'."""
    if re.search(r"^## Pending Tasks", content, re.MULTILINE):
        _fail(
            "**Error:** Old section name 'Pending Tasks' — rename to 'In-tree Tasks'",
            code=2,
        )


def _count_raw_tasks(content: str, section: str = "In-tree Tasks") -> int:
    """Count task-like lines in a section (lines starting with ``- [``)."""
    in_section = False
    count = 0
    for line in content.splitlines():
        if line.startswith(f"## {section}"):
            in_section = True
            continue
        if line.startswith("## ") and in_section:
            break
        if in_section and line.startswith("- ["):
            count += 1
    return count


@click.command(name="status", hidden=True)
def status_cmd() -> None:
    """Render STATUS output from session.md."""
    session_path = Path(os.environ.get("CLAUDEUTILS_SESSION_FILE", "agents/session.md"))

    try:
        content = session_path.read_text()
    except OSError:
        _fail(f"**Error:** Session file not found: {session_path}", code=2)

    _check_old_section_name(content)
    data = parse_session(session_path, content=content)

    raw_count = _count_raw_tasks(content)
    if raw_count != len(data.in_tree_tasks):
        n = raw_count - len(data.in_tree_tasks)
        _fail(
            f"**Error:** {n} task lines without required metadata (** and —)",
            code=2,
        )

    # Relative path — CLI runs from repo root (cwd assumption)
    all_plans = {p.name: p.status for p in list_plans(Path("plans"))}
    plan_states: dict[str, str] = {}
    for task in [*data.in_tree_tasks, *data.worktree_tasks]:
        if task.plan_dir:
            plan_states[task.plan_dir] = all_plans.get(task.plan_dir, "")

    sections: list[str] = []

    # Continuation header (dirty tree)
    cont = render_continuation(is_dirty=_is_dirty(), plan_states=plan_states)
    if cont:
        sections.append(cont)

    # In-tree tasks
    pending_section = render_pending(
        data.in_tree_tasks, plan_states, color=sys.stdout.isatty()
    )
    if pending_section:
        sections.append(pending_section)
    else:
        sections.append("No in-tree tasks.")

    # Worktree tasks
    wt_section = render_worktree(data.worktree_tasks)
    if wt_section:
        sections.append(wt_section)

    task_plan_dirs = {
        t.plan_dir for t in [*data.in_tree_tasks, *data.worktree_tasks] if t.plan_dir
    }
    unscheduled = render_unscheduled(all_plans, task_plan_dirs)
    if unscheduled:
        sections.append(unscheduled)

    # Parallel detection
    parallel = detect_parallel(data.in_tree_tasks, data.blockers)
    if parallel:
        names = "\n  - ".join(parallel)
        header = f"Parallel ({len(parallel)} tasks, independent):"
        sections.append(f"{header}\n  - {names}\n  `wt` to set up worktrees")

    click.echo("\n\n".join(sections))
