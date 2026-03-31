"""Tests for remove_slug_marker function."""

from pathlib import Path

from edify.worktree.session import remove_slug_marker


def test_remove_slug_marker_basic(tmp_path: Path) -> None:
    """Remove slug marker inline from task in Worktree Tasks section."""
    session_content = """# Session

## In-tree Tasks

- [ ] **Task X** — desc | sonnet

## Worktree Tasks

- [ ] **Task A** → `task-a` — desc | sonnet
- [ ] **Task B** — desc | haiku
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    remove_slug_marker(session_path, "task-a")

    result = session_path.read_text()
    # Marker should be removed, task should stay in Worktree Tasks
    assert "- [ ] **Task A** — desc | sonnet" in result
    # Marker should be gone
    assert "→ `task-a`" not in result
    # Task A still in Worktree Tasks
    assert "## Worktree Tasks" in result
    worktree_idx = result.find("## Worktree Tasks")
    next_section_idx = result.find("##", worktree_idx + 1)
    if next_section_idx == -1:
        next_section_idx = len(result)
    worktree_section = result[worktree_idx:next_section_idx]
    assert "**Task A**" in worktree_section
    # Task B unchanged
    assert "- [ ] **Task B** — desc | haiku" in result


def test_remove_slug_marker_preserves_others(tmp_path: Path) -> None:
    """Removing marker from one task preserves others with their markers."""
    session_content = """# Session

## Worktree Tasks

- [ ] **Task A** → `task-a` — desc | sonnet
- [ ] **Task B** → `task-b` — desc | haiku
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    remove_slug_marker(session_path, "task-a")

    result = session_path.read_text()
    # Task A marker removed
    assert "→ `task-a`" not in result
    # Task A still present without marker
    assert "- [ ] **Task A** — desc | sonnet" in result
    # Task B marker preserved
    assert "→ `task-b`" in result
    assert "- [ ] **Task B** → `task-b` — desc | haiku" in result


def test_remove_slug_marker_not_found(tmp_path: Path) -> None:
    """Slug not found is a no-op, no error raised."""
    session_content = """# Session

## Worktree Tasks

- [ ] **Task A** → `task-a` — desc | sonnet
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    # Slug doesn't exist - should be no-op
    remove_slug_marker(session_path, "nonexistent-slug")

    result = session_path.read_text()
    # Content unchanged
    assert "- [ ] **Task A** → `task-a` — desc | sonnet" in result


def test_remove_slug_marker_multiline(tmp_path: Path) -> None:
    """Marker removed from first line; continuation lines preserved."""
    session_content = """# Session

## Worktree Tasks

- [ ] **Task A** → `task-a` — `/design plans/foo/design.md` | opus
  - Plan: foo | Status: designed
  - Notes: Complex work
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    remove_slug_marker(session_path, "task-a")

    result = session_path.read_text()
    # Marker removed from first line
    assert "- [ ] **Task A** — `/design plans/foo/design.md` | opus" in result
    # Continuation lines preserved
    assert "  - Plan: foo | Status: designed" in result
    assert "  - Notes: Complex work" in result
    # No markers
    assert "→" not in result


def test_remove_slug_marker_only_modifies_worktree_section(tmp_path: Path) -> None:
    """Remove marker only within Worktree Tasks section."""
    session_content = """# Session

## In-tree Tasks

- [ ] **Task X** — see → `task-a` ref | sonnet

## Worktree Tasks

- [ ] **Task A** → `task-a` — desc | sonnet
"""
    session_path = tmp_path / "session.md"
    session_path.write_text(session_content)

    remove_slug_marker(session_path, "task-a")

    result = session_path.read_text()
    # Worktree Tasks marker removed
    wt_idx = result.find("## Worktree Tasks")
    worktree_section = result[wt_idx:]
    assert "→ `task-a`" not in worktree_section
    assert "- [ ] **Task A** — desc | sonnet" in worktree_section
    # In-tree Tasks content preserved (even though it contains the pattern)
    it_idx = result.find("## In-tree Tasks")
    in_tree_section = result[it_idx:wt_idx]
    assert "→ `task-a`" in in_tree_section
