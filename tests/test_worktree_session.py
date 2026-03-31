"""Tests for worktree session.md parsing."""

from pathlib import Path

import pytest

from edify.worktree.cli import focus_session
from edify.worktree.session import (
    extract_task_blocks,
    find_section_bounds,
)


def test_extract_single_line_task() -> None:
    """Extract single-line task from session.md content."""
    content = """# Session

## In-tree Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Task B** — `/runbook` | haiku

## Blockers
"""
    blocks = extract_task_blocks(content)
    assert len(blocks) == 2
    assert blocks[0].name == "Task A"
    assert blocks[0].lines == ["- [ ] **Task A** — `/design` | sonnet"]
    assert blocks[0].section == "In-tree Tasks"
    assert blocks[1].name == "Task B"
    assert blocks[1].lines == ["- [ ] **Task B** — `/runbook` | haiku"]
    assert blocks[1].section == "In-tree Tasks"


def test_find_section_bounds_existing() -> None:
    """Find section bounds returns correct line numbers."""
    content = """# Session

## In-tree Tasks

- [ ] **Task A** — plan

## Blockers

- Blocker 1
"""
    bounds = find_section_bounds(content, "In-tree Tasks")
    assert bounds is not None
    start, end = bounds
    lines = content.split("\n")
    # start should be the line index of "## In-tree Tasks"
    assert lines[start] == "## In-tree Tasks"
    # end should be before "## Blockers" or EOF
    # Lines between start and end should contain the task
    section_lines = lines[start:end]
    assert any("Task A" in line for line in section_lines)


def test_find_section_bounds_not_found() -> None:
    """Find section bounds returns None when section not found."""
    content = """# Session

## In-tree Tasks

- [ ] **Task A** — plan
"""
    bounds = find_section_bounds(content, "Nonexistent Section")
    assert bounds is None


def test_extract_blocked_failed_canceled_tasks() -> None:
    """Extract tasks with [!], [†], [-] statuses."""
    content = """# Session

## In-tree Tasks

- [!] **Blocked Task** — waiting on signal
- [†] **Failed Task** — terminal failure
- [-] **Canceled Task** — user canceled

## Blockers
"""
    blocks = extract_task_blocks(content)
    assert len(blocks) == 3
    assert blocks[0].name == "Blocked Task"
    assert blocks[1].name == "Failed Task"
    assert blocks[2].name == "Canceled Task"


def test_extract_multi_line_task() -> None:
    """Extract multi-line task with continuation lines."""
    content = """# Session

## In-tree Tasks

- [ ] **Task A** — `/design plans/foo/design.md` | opus
  - Plan: foo | Status: designed
  - Notes: Complex architecture work
- [ ] **Task B** — `/runbook` | haiku

## Blockers
"""
    blocks = extract_task_blocks(content)
    assert len(blocks) == 2
    assert blocks[0].name == "Task A"
    assert len(blocks[0].lines) == 3
    assert (
        blocks[0].lines[0] == "- [ ] **Task A** — `/design plans/foo/design.md` | opus"
    )
    assert blocks[0].lines[1] == "  - Plan: foo | Status: designed"
    assert blocks[0].lines[2] == "  - Notes: Complex architecture work"
    assert blocks[1].name == "Task B"
    assert len(blocks[1].lines) == 1


def test_extract_section_filter() -> None:
    """Extract tasks filtered by section name."""
    content = """# Session

## In-tree Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Task B** — `/runbook` | haiku

## Worktree Tasks

- [ ] **Task C** → `fix-merge` — `/design` | opus
- [ ] **Task D** → `update-tests` — `/runbook` | haiku

## Blockers
"""
    # Extract only In-tree Tasks
    pending = extract_task_blocks(content, section="In-tree Tasks")
    assert len(pending) == 2
    assert pending[0].name == "Task A"
    assert pending[0].section == "In-tree Tasks"
    assert pending[1].name == "Task B"
    assert pending[1].section == "In-tree Tasks"

    # Extract only Worktree Tasks
    worktree = extract_task_blocks(content, section="Worktree Tasks")
    assert len(worktree) == 2
    assert worktree[0].name == "Task C"
    assert worktree[0].section == "Worktree Tasks"
    assert worktree[1].name == "Task D"
    assert worktree[1].section == "Worktree Tasks"

    # Extract all tasks (no filter)
    all_tasks = extract_task_blocks(content, section=None)
    assert len(all_tasks) == 4


def test_focus_session_multiline(tmp_path: Path) -> None:
    """Focus session reads from Worktree Tasks, outputs In-tree Tasks header."""
    session_content = """# Session Handoff

## Pending Tasks

- [ ] **Other task** — `/runbook plans/other/` | haiku

## Worktree Tasks

- [ ] **My task** → `my-task` — `/design plans/my-task/` | sonnet
  - Plan: my-task | Status: designed
  - Note: some detail

## Blockers / Gotchas

- Something about My task
- Something unrelated
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    result = focus_session("My task", session_path)

    # Output header should be "In-tree Tasks"
    assert "## In-tree Tasks" in result
    # Task line should NOT include → `my-task` marker
    assert "- [ ] **My task** — `/design plans/my-task/` | sonnet" in result
    assert "→ `my-task`" not in result
    # Continuation lines preserved
    assert "- Plan: my-task | Status: designed" in result
    assert "- Note: some detail" in result
    # Other task not included
    assert "Other task" not in result
    # Relevant context included
    assert "Something about My task" in result
    assert "Something unrelated" not in result


def test_focus_session_strips_slug_marker(tmp_path: Path) -> None:
    """Focused output strips the → `slug` marker from task line."""
    session_content = """# Session

## Worktree Tasks

- [ ] **My task** → `my-slug` — `/design` | sonnet
  - Plan: my-plan | Status: ready

## Blockers / Gotchas

- Nothing here
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    result = focus_session("My task", session_path)

    # Task line without slug marker
    assert "- [ ] **My task** — `/design` | sonnet" in result
    # Slug marker NOT in output
    assert "→ `my-slug`" not in result
    # Continuation lines still present
    assert "- Plan: my-plan | Status: ready" in result


def test_focus_session_worktree_only(tmp_path: Path) -> None:
    """Focus session searches Worktree Tasks only, not Pending Tasks."""
    session_content = """# Session

## Pending Tasks

- [ ] **My task** — `/design` | sonnet

## Worktree Tasks

- [ ] **Other task** → `other` — `/runbook` | haiku
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    # Task in Pending Tasks should not be found
    with pytest.raises(ValueError, match=r"My task.*not found"):
        focus_session("My task", session_path)
