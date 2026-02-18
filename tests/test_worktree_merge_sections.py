"""Tests for find_section_bounds() section identification."""

from claudeutils.worktree.session import find_section_bounds


class TestSectionIdentification:
    """Tests for find_section_bounds() function."""

    def test_pending_tasks_section(self) -> None:
        """Pending Tasks section finds correct start and end."""
        content = """# Session Handoff
Some intro text
## Pending Tasks
- Task 1
- Task 2
- Task 3
- Task 4
- Task 5
## Next Section
More content
"""
        result = find_section_bounds(content, "Pending Tasks")
        assert result == (2, 8), f"Expected (2, 8), got {result}"

    def test_worktree_tasks_section(self) -> None:
        """Worktree Tasks section finds correct bounds."""
        content = """# Session Handoff
Some intro
## Pending Tasks
- Item 1
- Item 2
- Item 3
- Item 4
- Item 5
## Worktree Tasks
- WT1 task
- WT2 task
- WT3 task
- WT4 task
## Blockers
Text
"""
        result = find_section_bounds(content, "Worktree Tasks")
        assert result == (8, 13), f"Expected (8, 13), got {result}"

    def test_section_with_slash(self) -> None:
        """Section with slash character in name works correctly."""
        content = """# Session Handoff
Text
## Pending Tasks
- Item
## Blockers / Gotchas
Text line 1
Text line 2
Text line 3
Text line 4
Text line 5
## Next Section
More
"""
        result = find_section_bounds(content, "Blockers / Gotchas")
        assert result == (4, 10), f"Expected (4, 10), got {result}"

    def test_nonexistent_section(self) -> None:
        """Nonexistent section returns None."""
        content = """# Session Handoff
Text
## Pending Tasks
- Item
"""
        result = find_section_bounds(content, "Nonexistent")
        assert result is None, f"Expected None, got {result}"

    def test_section_at_eof(self) -> None:
        """Section at end of file returns len(lines) as end index."""
        content = """# Session Handoff
Text
## Pending Tasks
- Item 1
- Item 2
- Item 3
- Item 4
## Blockers / Gotchas
Last section line 1
Last section line 2
"""
        result = find_section_bounds(content, "Blockers / Gotchas")
        lines = content.split("\n")
        assert result == (7, len(lines)), f"Expected (7, {len(lines)}), got {result}"

    def test_empty_section(self) -> None:
        """Section with no content between it and next section."""
        content = """# Header
## First Section
## Second Section
Content below
"""
        result = find_section_bounds(content, "First Section")
        assert result == (1, 2), f"Expected (1, 2), got {result}"

    def test_consecutive_sections(self) -> None:
        """Multiple sections in sequence verify proper boundary detection."""
        content = """# Header
## Section A
Content A
## Section B
Content B
## Section C
Content C
"""
        result_a = find_section_bounds(content, "Section A")
        result_b = find_section_bounds(content, "Section B")
        result_c = find_section_bounds(content, "Section C")
        assert result_a == (1, 3)
        assert result_b == (3, 5)
        lines = content.split("\n")
        assert result_c == (5, len(lines))

    def test_completed_tasks_section(self) -> None:
        """Completed Tasks section with checkbox items."""
        content = """# Session
## Completed Tasks
- [x] Task 1
- [x] Task 2
## Next
More
"""
        result = find_section_bounds(content, "Completed Tasks")
        assert result == (1, 4)

    def test_all_d5_section_names(self) -> None:
        """All section names from D-5 table work correctly."""
        section_names = [
            "Pending Tasks",
            "Worktree Tasks",
            "Completed Tasks",
            "Blockers / Gotchas",
            "Next Steps",
        ]
        for name in section_names:
            content = f"""# Header
## {name}
Content
## Another
More
"""
            result = find_section_bounds(content, name)
            assert result is not None, f"Section '{name}' not found"
            assert result == (1, 3), f"Section '{name}' bounds incorrect: {result}"
