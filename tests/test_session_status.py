"""Tests for session status rendering (Phase 3)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.session.status.render import (
    detect_parallel,
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
        # First task — ▶ format always shows model
        assert "Build parser" in result
        assert "▶ Build parser (sonnet)" in result
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


def test_render_pending_next_task_format() -> None:
    """First pending task uses design spec two-line format."""
    task = _task(
        "Build widget",
        command="/design plans/w/brief.md",
        model="sonnet",
        restart=True,
    )
    result = render_pending([task], {})
    lines = result.split("\n")
    # ▶ line: name, model in parens, Restart capitalized
    arrow_line = next(ln for ln in lines if "▶" in ln)
    assert arrow_line == "▶ Build widget (sonnet) | Restart: Yes"
    # Command on separate indented line
    cmd_line = next(ln for ln in lines if "/design plans/w/brief.md" in ln)
    assert cmd_line == "  `/design plans/w/brief.md`"


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


# --- Cycle 3.3: detect_parallel ---


def _task_with_plan(name: str, plan: str) -> ParsedTask:
    """Build a task with plan_dir set."""
    t = _task(name)
    t.plan_dir = plan
    return t


def test_detect_parallel_group() -> None:
    """Three tasks with different plan_dirs form a parallel group."""
    tasks = [
        _task_with_plan("A", "plan-a"),
        _task_with_plan("B", "plan-b"),
        _task_with_plan("C", "plan-c"),
    ]
    result = detect_parallel(tasks, [])
    assert result is not None
    assert set(result) == {"A", "B", "C"}


def test_detect_parallel_no_group() -> None:
    """Single task returns None."""
    tasks = [_task_with_plan("Solo", "plan-solo")]
    assert detect_parallel(tasks, []) is None


def test_detect_parallel_shared_plan() -> None:
    """Two tasks sharing plan_dir returns None."""
    tasks = [
        _task_with_plan("X", "parser"),
        _task_with_plan("Y", "parser"),
    ]
    assert detect_parallel(tasks, []) is None


def test_detect_parallel_mixed() -> None:
    """Four tasks, 2 sharing plan → largest consecutive independent subset."""
    tasks = [
        _task_with_plan("Dep1", "shared"),
        _task_with_plan("Dep2", "shared"),
        _task_with_plan("Ind1", "plan-1"),
        _task_with_plan("Ind2", "plan-2"),
    ]
    result = detect_parallel(tasks, [])
    assert result is not None
    # Dep1 and Dep2 share a plan — they are never both in the same group.
    # Largest consecutive independent window: Dep2 + Ind1 + Ind2 (positions 1-3).
    assert "Dep1" not in result or "Dep2" not in result
    assert len(result) >= 2


def test_detect_parallel_caps_at_five() -> None:
    """Seven independent tasks return exactly 5 (ST-1 cap)."""
    tasks = [_task_with_plan(f"Task{i}", f"plan-{i}") for i in range(7)]
    result = detect_parallel(tasks, [])
    assert result is not None
    assert len(result) == 5


def test_detect_parallel_blocker_excludes() -> None:
    """Blocker referencing task name creates dependency."""
    tasks = [
        _task_with_plan("Alpha", "plan-a"),
        _task_with_plan("Beta", "plan-b"),
    ]
    blockers = [["Blocker: Alpha blocks Beta"]]
    result = detect_parallel(tasks, blockers)
    assert result is None


# --- Cycle 3.4: CLI wiring ---


def test_session_status_cli(tmp_path: Path) -> None:
    """_status with real session.md produces output with exit 0."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text(SESSION_FIXTURE)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_status"],
        catch_exceptions=False,
        env={"CLAUDEUTILS_SESSION_FILE": str(agents_dir / "session.md")},
    )
    assert result.exit_code == 0
    assert "Next:" in result.output or "In-tree:" in result.output


def test_session_status_missing_session(tmp_path: Path) -> None:
    """_status without session.md exits 2 with error message."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_status"],
        env={
            "CLAUDEUTILS_SESSION_FILE": str(tmp_path / "agents" / "session.md"),
        },
    )
    assert result.exit_code == 2
    assert "Error" in result.output


SESSION_FIXTURE = """\
# Session Handoff: 2026-03-15

**Status:** Phase 3 in progress.

## Completed This Session

- Built parser

## In-tree Tasks

- [ ] **Build CLI** — `/runbook plans/cli/r.md` | sonnet
  - Plan: cli | Status: ready
- [ ] **Fix tests** — `just fix` | haiku

## Worktree Tasks

- [ ] **Remote work** → `wt` — `/design plans/remote/b.md` | sonnet
"""
