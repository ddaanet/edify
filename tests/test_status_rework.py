"""Tests for status rework (cycles 3.1-3.4)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.session.status.render import render_continuation, render_pending
from claudeutils.validation.task_parsing import ParsedTask

# Cycle 3.1: plan state discovery


def test_status_shows_plan_states(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Status output shows plan states from lifecycle.md."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    session = """\
# Session Handoff: 2026-03-20

**Status:** Working.

## Completed This Session

- Nothing

## In-tree Tasks

- [ ] **Build CLI** — `/runbook plans/cli/r.md` | sonnet
  - Plan: cli | Status: ready
"""
    (agents_dir / "session.md").write_text(session)

    plan_dir = tmp_path / "plans" / "cli"
    plan_dir.mkdir(parents=True)
    (plan_dir / "lifecycle.md").write_text("2026-03-20 review-pending — /orchestrate\n")
    (plan_dir / "brief.md").write_text("Brief.\n")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_status"],
        catch_exceptions=False,
        env={"CLAUDEUTILS_SESSION_FILE": str(agents_dir / "session.md")},
    )

    assert result.exit_code == 0
    assert "Status: review-pending" in result.output


# Cycle 3.2: continuation header


def test_render_continuation_dirty() -> None:
    """Dirty tree renders continuation header."""
    result = render_continuation(is_dirty=True, plan_states={})
    assert "Session: uncommitted changes" in result
    assert "`/handoff`" in result
    assert "`/commit`" in result


def test_render_continuation_clean() -> None:
    """Clean tree returns empty continuation."""
    assert render_continuation(is_dirty=False, plan_states={}) == ""


def test_render_continuation_review_pending() -> None:
    """Review-pending plan appends deliverable-review."""
    result = render_continuation(is_dirty=True, plan_states={"foo": "review-pending"})
    assert "`/deliverable-review plans/foo`" in result


# Cycle 3.3: merged next format


def test_status_format_merged_next() -> None:
    """First pending task in In-tree list gets ▶ prefix."""
    tasks = [
        ParsedTask(
            name="First",
            checkbox=" ",
            full_line="- [ ] **First** — `/runbook plans/a/r.md` | sonnet",
            command="/runbook plans/a/r.md",
            model="sonnet",
            restart=False,
            plan_dir="a",
        ),
        ParsedTask(
            name="Second",
            checkbox=" ",
            full_line="- [ ] **Second** — `just fix` | haiku",
            command="just fix",
            model="haiku",
            restart=False,
            plan_dir=None,
        ),
    ]
    result = render_pending(tasks, {})
    assert "▶ First" in result
    assert "`/runbook plans/a/r.md`" in result
    lines = result.split("\n")
    second_line = next(ln for ln in lines if "Second" in ln)
    assert "▶" not in second_line
    assert "just fix" not in second_line
    assert second_line.startswith("- ")


# Cycle 3.4: old format enforcement


def test_status_rejects_old_format(tmp_path: Path) -> None:
    """Old-format tasks (no metadata) exit 2."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    old_format = """\
# Session Handoff: 2026-03-20

**Status:** Working.

## Completed This Session

- Nothing

## In-tree Tasks

- [ ] Just a task name without metadata
"""
    (agents_dir / "session.md").write_text(old_format)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_status"],
        env={"CLAUDEUTILS_SESSION_FILE": str(agents_dir / "session.md")},
    )
    assert result.exit_code == 2
    assert "old-format" in result.output.lower()
    assert "metadata" in result.output.lower()


# Cycle 3.2: worktree marker skips next


def test_render_pending_skips_worktree_marked() -> None:
    """▶ marker appears on first unassigned pending task."""
    tasks = [
        ParsedTask(
            name="First",
            checkbox=" ",
            full_line="- [ ] **First** — `/cmd` | sonnet → wt-slug",
            command="/cmd",
            model="sonnet",
            restart=False,
            plan_dir=None,
            worktree_marker="wt-slug",
        ),
        ParsedTask(
            name="Second",
            checkbox=" ",
            full_line="- [ ] **Second** — `/cmd2` | sonnet",
            command="/cmd2",
            model="sonnet",
            restart=False,
            plan_dir=None,
            worktree_marker=None,
        ),
    ]
    result = render_pending(tasks, {})
    assert "▶ Second" in result
    lines = result.split("\n")
    first_line = next(ln for ln in lines if "First" in ln)
    assert "▶" not in first_line
    assert first_line.startswith("- First")


# Cycle 3.1: old section name detected


def test_status_rejects_pending_tasks_section(tmp_path: Path) -> None:
    """Old section name 'Pending Tasks' is rejected with exit 2."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    old_section_name = """\
# Session Handoff: 2026-03-20

**Status:** Working.

## Completed This Session

- Nothing

## Pending Tasks

- [ ] **Task** — `/cmd` | sonnet
"""
    (agents_dir / "session.md").write_text(old_section_name)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_status"],
        env={"CLAUDEUTILS_SESSION_FILE": str(agents_dir / "session.md")},
    )
    assert result.exit_code == 2
    assert "pending tasks" in result.output.lower()


# Cycle 1.2: blockers wired to detect_parallel


def test_status_parallel_uses_blockers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Blocker dependencies prevent parallel detection."""
    monkeypatch.chdir(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    session = """\
# Session Handoff: 2026-03-23

**Status:** Working.

## Completed This Session

- Nothing

## In-tree Tasks

- [ ] **Task A** — `/runbook plans/task-a/r.md` | sonnet
  - Plan: task-a
- [ ] **Task B** — `/runbook plans/task-b/r.md` | sonnet
  - Plan: task-b

## Blockers / Gotchas

- Task B depends on Task A for completion.
"""
    (agents_dir / "session.md").write_text(session)

    plan_a = tmp_path / "plans" / "task-a"
    plan_a.mkdir(parents=True)
    (plan_a / "lifecycle.md").write_text("2026-03-23 ready\n")
    (plan_a / "brief.md").write_text("Brief A.\n")

    plan_b = tmp_path / "plans" / "task-b"
    plan_b.mkdir(parents=True)
    (plan_b / "lifecycle.md").write_text("2026-03-23 ready\n")
    (plan_b / "brief.md").write_text("Brief B.\n")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_status"],
        catch_exceptions=False,
        env={"CLAUDEUTILS_SESSION_FILE": str(agents_dir / "session.md")},
    )

    assert result.exit_code == 0
    assert "Parallel" not in result.output
