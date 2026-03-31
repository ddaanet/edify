"""Tests for add_slug_marker function."""

from pathlib import Path

import pytest

from edify.worktree.session import add_slug_marker


def test_add_slug_marker_basic(tmp_path: Path) -> None:
    """Add slug marker inline to task in Worktree Tasks section."""
    session_content = """# Session

## In-tree Tasks

- [ ] **Task X** — desc | sonnet

## Worktree Tasks

- [ ] **Task A** — desc | sonnet
- [ ] **Task B** — desc | haiku
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    add_slug_marker(session_path, "Task A", "task-a")

    result = session_path.read_text()
    # Task A should have marker added inline
    assert "- [ ] **Task A** → `task-a` — desc | sonnet" in result
    # Task A should still be in Worktree Tasks
    assert "## Worktree Tasks" in result
    worktree_idx = result.find("## Worktree Tasks")
    next_section_idx = result.find("##", worktree_idx + 1)
    if next_section_idx == -1:
        next_section_idx = len(result)
    worktree_section = result[worktree_idx:next_section_idx]
    assert "**Task A**" in worktree_section
    # Task B unchanged
    assert "- [ ] **Task B** — desc | haiku" in result


def test_add_slug_marker_preserves_other_tasks(tmp_path: Path) -> None:
    """Adding marker to one task preserves other tasks in both sections."""
    session_content = """# Session

## In-tree Tasks

- [ ] **Task X** — desc | sonnet
- [ ] **Task Y** — desc | haiku

## Worktree Tasks

- [ ] **Task A** — desc | sonnet
- [ ] **Task B** — desc | haiku
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    add_slug_marker(session_path, "Task A", "task-a")

    result = session_path.read_text()
    # All tasks preserved
    assert "**Task X**" in result
    assert "**Task Y**" in result
    assert "**Task B**" in result
    # Only Task A has marker
    assert "- [ ] **Task A** → `task-a`" in result
    assert "- [ ] **Task X** —" in result
    assert "- [ ] **Task Y** —" in result
    assert "- [ ] **Task B** —" in result
    # No other markers
    assert result.count("→") == 1


def test_add_slug_marker_not_found(tmp_path: Path) -> None:
    """Raises ValueError if task not found in Worktree Tasks."""
    session_content = """# Session

## In-tree Tasks

- [ ] **Task A** — desc | sonnet

## Worktree Tasks

- [ ] **Task B** — desc | haiku
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    # Task A is in In-tree Tasks, not Worktree Tasks
    with pytest.raises(ValueError, match="Task 'Task A' not found in Worktree Tasks"):
        add_slug_marker(session_path, "Task A", "task-a")

    # Nonexistent task
    with pytest.raises(ValueError, match="Nonexistent"):
        add_slug_marker(session_path, "Nonexistent", "slug")


def test_add_slug_marker_multiline(tmp_path: Path) -> None:
    """Marker added to first line only; continuation lines preserved."""
    session_content = """# Session

## Worktree Tasks

- [ ] **Task A** — `/design plans/foo/design.md` | opus
  - Plan: foo | Status: designed
  - Notes: Complex work
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    add_slug_marker(session_path, "Task A", "task-a")

    result = session_path.read_text()
    # Marker on first line only
    assert (
        "- [ ] **Task A** → `task-a` — `/design plans/foo/design.md` | opus" in result
    )
    # Continuation lines preserved
    assert "  - Plan: foo | Status: designed" in result
    assert "  - Notes: Complex work" in result
    # Only one marker
    assert result.count("→") == 1


def test_add_slug_marker_identical_task_both_sections(tmp_path: Path) -> None:
    """Modify only Worktree Tasks entry when same task in both sections."""
    session_content = """# Session

## In-tree Tasks

- [ ] **Deploy service** — `just deploy` | sonnet

## Worktree Tasks

- [ ] **Deploy service** — `just deploy` | sonnet
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    add_slug_marker(session_path, "Deploy service", "deploy-svc")

    result = session_path.read_text()
    # In-tree Tasks entry should NOT have marker
    it_idx = result.find("## In-tree Tasks")
    wt_idx = result.find("## Worktree Tasks")
    in_tree_section = result[it_idx:wt_idx]
    assert "→" not in in_tree_section
    # Worktree Tasks entry should have marker
    worktree_section = result[wt_idx:]
    assert "→ `deploy-svc`" in worktree_section
