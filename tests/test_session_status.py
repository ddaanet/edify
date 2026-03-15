"""Tests for session status rendering (Phase 3)."""

from __future__ import annotations

import pytest

from claudeutils.session.status.render import (
    render_next,
    render_pending,
    render_unscheduled,
    render_worktree,
)
from claudeutils.validation.task_parsing import ParsedTask


def _task(name: str, **kwargs: object) -> ParsedTask:
    """Build a ParsedTask for testing with sensible defaults."""
    defaults: dict[str, object] = {
        "checkbox": " ",
        "command": "/runbook plans/test/r.md",
        "model": "sonnet",
        "worktree_marker": None,
        "restart": False,
    }
    defaults.update(kwargs)
    return ParsedTask(
        name=name,
        checkbox=str(defaults["checkbox"]),
        full_line=f"- [{defaults['checkbox']}] **{name}**",
        command=defaults.get("command"),  # type: ignore[arg-type]
        model=defaults.get("model"),  # type: ignore[arg-type]
        worktree_marker=defaults.get("worktree_marker"),  # type: ignore[arg-type]
        restart=bool(defaults["restart"]),
    )


# --- Cycle 3.1: render_next ---


def test_render_next_task() -> None:
    """First pending task without worktree marker renders as Next block."""
    tasks = [
        _task("Build parser", command="/runbook plans/parser/design.md"),
    ]
    result = render_next(tasks)
    assert "Next: Build parser" in result
    assert "`/runbook plans/parser/design.md`" in result
    assert "Model: sonnet" in result
    assert "Restart: no" in result


def test_render_next_skips_worktree_markers() -> None:
    """Tasks with worktree markers are skipped; first plain pending wins."""
    tasks = [
        _task("Slugged", worktree_marker="my-slug"),
        _task("WT marked", worktree_marker="wt"),
        _task("Plain pending", command="/design plans/p/b.md"),
    ]
    result = render_next(tasks)
    assert "Next: Plain pending" in result
    assert "Slugged" not in result
    assert "WT marked" not in result


def test_render_next_no_pending() -> None:
    """Empty task list returns empty string."""
    assert render_next([]) == ""


def test_render_next_skips_completed() -> None:
    """Tasks with checkbox x are skipped."""
    tasks = [_task("Done", checkbox="x")]
    assert render_next(tasks) == ""


def test_render_next_skips_blocked() -> None:
    """Tasks with blocked checkbox are skipped."""
    tasks = [_task("Blocked", checkbox="!")]
    assert render_next(tasks) == ""


def test_render_next_skips_failed() -> None:
    """Tasks with checkbox † are skipped."""
    tasks = [_task("Failed", checkbox="†")]
    assert render_next(tasks) == ""


def test_render_next_skips_canceled() -> None:
    """Tasks with checkbox - are skipped."""
    tasks = [_task("Canceled", checkbox="-")]
    assert render_next(tasks) == ""


def test_render_next_restart_yes() -> None:
    """Restart flag renders as 'yes'."""
    tasks = [_task("Heavy", restart=True, model="opus")]
    result = render_next(tasks)
    assert "Restart: yes" in result
    assert "Model: opus" in result


def test_render_next_model_defaults() -> None:
    """None model defaults to 'sonnet' in output."""
    tasks = [_task("No model", model=None)]
    result = render_next(tasks)
    assert "Model: sonnet" in result


# --- Cycle 3.2: render_pending, render_worktree, render_unscheduled ---


@pytest.mark.parametrize(
    "section",
    ["pending", "worktree", "unscheduled"],
)
def test_render_section(section: str) -> None:
    """Non-empty inputs produce expected section output."""
    if section == "pending":
        t1 = _task(
            "Build parser",
            command="/runbook plans/parser/design.md",
            model="sonnet",
        )
        t1.plan_dir = "parser"
        tasks = [
            t1,
            _task("Fix bug", command="just fix-bug", model="haiku"),
        ]
        plan_states = {"parser": "outlined"}
        result = render_pending(tasks, plan_states)
        # Section header
        assert result.startswith("In-tree:")
        # First task — sonnet is default, omitted
        assert "Build parser" in result
        assert "(sonnet)" not in result
        # Plan status line
        assert "Plan: parser" in result
        assert "outlined" in result
        # Second task — haiku is non-default, shown
        assert "Fix bug (haiku)" in result

    elif section == "worktree":
        tasks = [
            _task("Parallel work", worktree_marker="my-slug"),
            _task("Future work", worktree_marker="wt"),
        ]
        result = render_worktree(tasks)
        assert result.startswith("Worktree:")
        assert "Parallel work" in result
        assert "→ my-slug" in result
        assert "Future work" in result

    elif section == "unscheduled":
        all_plans = {"orphan-plan": "designed", "done": "delivered"}
        task_plan_dirs: set[str] = set()
        result = render_unscheduled(all_plans, task_plan_dirs)
        assert "Unscheduled Plans:" in result
        assert "orphan-plan" in result
        assert "designed" in result
        assert "done" not in result


@pytest.mark.parametrize(
    "section",
    ["pending", "worktree", "unscheduled"],
)
def test_render_empty_section(section: str) -> None:
    """Empty inputs produce empty string."""
    if section == "pending":
        assert render_pending([], {}) == ""
    elif section == "worktree":
        assert render_worktree([]) == ""
    elif section == "unscheduled":
        assert render_unscheduled({}, set()) == ""


def test_render_pending_excludes_completed() -> None:
    """Completed tasks (checkbox x) excluded from pending section."""
    tasks = [
        _task("Done", checkbox="x"),
        _task("Active"),
    ]
    result = render_pending(tasks, {})
    assert "Done" not in result
    assert "Active" in result


def test_render_unscheduled_sorted() -> None:
    """Unscheduled plans sorted alphabetically."""
    plans = {"z-plan": "briefed", "a-plan": "designed"}
    result = render_unscheduled(plans, set())
    z_pos = result.index("z-plan")
    a_pos = result.index("a-plan")
    assert a_pos < z_pos


def test_render_unscheduled_excludes_task_plans() -> None:
    """Plans associated to tasks excluded from unscheduled."""
    plans = {"active": "ready", "orphan": "designed"}
    result = render_unscheduled(plans, {"active"})
    assert "active" not in result
    assert "orphan" in result
