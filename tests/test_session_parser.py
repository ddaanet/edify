"""Tests for session.md parser."""

from pathlib import Path

import pytest

from claudeutils.session.parse import (
    ParsedTask,
    SessionData,
    SessionFileError,
    parse_completed_section,
    parse_session,
    parse_status_line,
    parse_tasks,
)

SESSION_MD_FIXTURE = """\
# Session Handoff: 2026-03-07

**Status:** Phase 1 complete — infrastructure ready.

## Completed This Session

**Phase 1 infrastructure:**
- Extracted git helpers
- Created package structure

## In-tree Tasks

- [ ] **Build parser** — `/runbook plans/parser/design.md` | sonnet
  - Plan: parser | Status: outlined
- [ ] **Fix bug** — `just fix-bug` | haiku
- [x] **Done task** — `/commit` | sonnet

## Worktree Tasks

- [ ] **Parallel work** → `my-slug` — `/design plans/par/p.md` | opus | restart
- [ ] **Future work** → `wt` — `/design plans/future/problem.md` | sonnet
"""


@pytest.mark.parametrize(
    "section_key",
    ["status_line", "completed", "in_tree_tasks", "worktree_tasks"],
    ids=["status_line", "completed", "in_tree_tasks", "worktree_tasks"],
)
def test_parse_session_sections(section_key: str) -> None:
    """Parse all session.md sections with parametrized tests."""
    if section_key == "status_line":
        result = parse_status_line(SESSION_MD_FIXTURE)
        assert result is not None
        assert "Phase 1 complete" in result

    elif section_key == "completed":
        lines = parse_completed_section(SESSION_MD_FIXTURE)
        assert isinstance(lines, list)
        assert len(lines) > 0
        assert any("Extracted git helpers" in line for line in lines)

    elif section_key == "in_tree_tasks":
        tasks = parse_tasks(SESSION_MD_FIXTURE, section="In-tree Tasks")
        assert len(tasks) == 3
        assert isinstance(tasks[0], ParsedTask)
        # Build parser task
        assert tasks[0].model == "sonnet"
        assert tasks[0].command is not None
        assert "/runbook" in tasks[0].command
        assert tasks[0].restart is False
        assert tasks[0].plan_dir == "parser"
        # Fix bug task
        assert tasks[1].model == "haiku"
        assert tasks[1].command == "just fix-bug"
        # Done task
        assert tasks[2].model == "sonnet"

    elif section_key == "worktree_tasks":
        tasks = parse_tasks(SESSION_MD_FIXTURE, section="Worktree Tasks")
        assert len(tasks) == 2
        assert isinstance(tasks[0], ParsedTask)
        # Parallel work with slug
        assert tasks[0].model == "opus"
        assert tasks[0].restart is True
        assert tasks[0].worktree_marker == "my-slug"
        # Future work with wt
        assert tasks[1].worktree_marker == "wt"


def test_parse_status_line_missing() -> None:
    """Content without # Session Handoff: returns None."""
    content = "## Some Other Heading\n\nSome content.\n"
    assert parse_status_line(content) is None


def test_parse_tasks_old_format() -> None:
    """Task line without pipe-separated metadata returns defaults."""
    content = """\
## In-tree Tasks

- [ ] **Old task** — `some-command`
"""
    tasks = parse_tasks(content, section="In-tree Tasks")
    assert len(tasks) == 1
    assert tasks[0].model is None
    assert tasks[0].restart is False


def test_parse_tasks_empty_section() -> None:
    """Section heading present but no tasks returns []."""
    content = """\
## In-tree Tasks

## Next Section
"""
    tasks = parse_tasks(content, section="In-tree Tasks")
    assert tasks == []


def test_parse_completed_section_empty() -> None:
    """Heading present, no content returns []."""
    content = """\
## Completed This Session

## Next Section
"""
    lines = parse_completed_section(content)
    assert lines == []


def test_parse_session(tmp_path: Path) -> None:
    """parse_session() returns SessionData with all fields populated."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_MD_FIXTURE)

    data = parse_session(session_file)
    assert isinstance(data, SessionData)
    assert data.date == "2026-03-07"
    assert data.status_line is not None
    assert "Phase 1 complete" in data.status_line
    assert len(data.completed) > 0
    assert data.in_tree_tasks[0].name == "Build parser"
    assert data.in_tree_tasks[0].plan_dir == "parser"
    assert data.worktree_tasks[0].worktree_marker == "my-slug"


def test_parse_session_missing_file(tmp_path: Path) -> None:
    """parse_session() raises SessionFileError for nonexistent file."""
    with pytest.raises(SessionFileError):
        parse_session(tmp_path / "nonexistent.md")


def test_parse_session_old_format(tmp_path: Path) -> None:
    """Session with old format tasks returns ParsedTask with defaults."""
    content = """\
# Session Handoff: 2026-01-01

**Status:** Old format session.

## In-tree Tasks

- [ ] **Old task** — `some-command`
"""
    session_file = tmp_path / "session.md"
    session_file.write_text(content)

    data = parse_session(session_file)
    assert len(data.in_tree_tasks) == 1
    assert data.in_tree_tasks[0].model is None
    assert data.in_tree_tasks[0].restart is False


def test_parse_session_extracts_blockers(tmp_path: Path) -> None:
    """parse_session() extracts Blockers / Gotchas section."""
    content = """\
# Session Handoff: 2026-03-15

**Status:** Testing blockers extraction.

## In-tree Tasks

- [ ] **Task 1** — `/design`

## Blockers / Gotchas

- Item depends on external API availability
- Concurrent execution cap is 5 unblocked tasks
"""
    session_file = tmp_path / "session.md"
    session_file.write_text(content)

    data = parse_session(session_file)
    assert len(data.blockers) == 2
    assert "Item depends on external API availability" in data.blockers[0][0]
    assert "Concurrent execution cap" in data.blockers[1][0]
