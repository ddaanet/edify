"""Tests for worktree session.md parsing."""

from pathlib import Path

from claudeutils.worktree.cli import focus_session
from claudeutils.worktree.session import extract_task_blocks, find_section_bounds


def test_extract_single_line_task() -> None:
    """Extract single-line task from session.md content."""
    content = """# Session

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Task B** — `/runbook` | haiku

## Blockers
"""
    blocks = extract_task_blocks(content)
    assert len(blocks) == 2
    assert blocks[0].name == "Task A"
    assert blocks[0].lines == ["- [ ] **Task A** — `/design` | sonnet"]
    assert blocks[0].section == "Pending Tasks"
    assert blocks[1].name == "Task B"
    assert blocks[1].lines == ["- [ ] **Task B** — `/runbook` | haiku"]
    assert blocks[1].section == "Pending Tasks"


def test_find_section_bounds_existing() -> None:
    """Find section bounds returns correct line numbers."""
    content = """# Session

## Pending Tasks

- [ ] **Task A** — plan

## Blockers

- Blocker 1
"""
    bounds = find_section_bounds(content, "Pending Tasks")
    assert bounds is not None
    start, end = bounds
    lines = content.split("\n")
    # start should be the line index of "## Pending Tasks"
    assert lines[start] == "## Pending Tasks"
    # end should be before "## Blockers" or EOF
    # Lines between start and end should contain the task
    section_lines = lines[start:end]
    assert any("Task A" in line for line in section_lines)


def test_find_section_bounds_not_found() -> None:
    """Find section bounds returns None when section not found."""
    content = """# Session

## Pending Tasks

- [ ] **Task A** — plan
"""
    bounds = find_section_bounds(content, "Nonexistent Section")
    assert bounds is None


def test_extract_multi_line_task() -> None:
    """Extract multi-line task with continuation lines."""
    content = """# Session

## Pending Tasks

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

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Task B** — `/runbook` | haiku

## Worktree Tasks

- [ ] **Task C** → `fix-merge` — `/design` | opus
- [ ] **Task D** → `update-tests` — `/runbook` | haiku

## Blockers
"""
    # Extract only Pending Tasks
    pending = extract_task_blocks(content, section="Pending Tasks")
    assert len(pending) == 2
    assert pending[0].name == "Task A"
    assert pending[0].section == "Pending Tasks"
    assert pending[1].name == "Task B"
    assert pending[1].section == "Pending Tasks"

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
    """Focus session preserves continuation lines from task block."""
    session_content = """# Session Handoff

## Pending Tasks

- [ ] **My task** — `/design plans/my-task/` | sonnet
  - Plan: my-task | Status: designed
  - Note: some detail

- [ ] **Other task** — `/runbook plans/other/` | haiku

## Blockers / Gotchas

- Something about My task
- Something unrelated
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    result = focus_session("My task", session_path)

    assert "- [ ] **My task** — `/design plans/my-task/` | sonnet" in result
    assert "- Plan: my-task | Status: designed" in result
    assert "- Note: some detail" in result
    assert "Other task" not in result
    assert "Something about My task" in result
    assert "Something unrelated" not in result
