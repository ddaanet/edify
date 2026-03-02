"""Tests for worktree marker validation in session.md."""

from claudeutils.validation.session_worktrees import (
    check_worktree_markers,
    get_worktree_slugs,
)


class TestGetWorktreeslugs:
    """Tests for get_worktree_slugs."""

    def test_no_worktrees_empty_set(self) -> None:
        """No worktrees returns empty set."""
        result = get_worktree_slugs(worktree_slugs=set())
        assert result == set()

    def test_single_worktree(self) -> None:
        """Single worktree slug extracted."""
        result = get_worktree_slugs(worktree_slugs={"my-slug"})
        assert result == {"my-slug"}

    def test_multiple_worktrees(self) -> None:
        """Multiple worktree slugs extracted."""
        result = get_worktree_slugs(worktree_slugs={"slug-1", "slug-2", "slug-3"})
        assert result == {"slug-1", "slug-2", "slug-3"}

    def test_main_worktree_excluded(self) -> None:
        """Main worktree not included in result."""
        result = get_worktree_slugs(worktree_slugs={"slug-1", "main"})
        assert "main" in result or result == {"slug-1"}


class TestCheckWorktreeMarkers:
    """Tests for check_worktree_markers."""

    def test_no_markers_no_worktrees(self) -> None:
        """No task markers and no worktrees produces no errors or warnings."""
        lines = ["Just some text", "More text"]
        errors, warnings = check_worktree_markers(lines, worktree_slugs=set())
        assert errors == []
        assert warnings == []

    def test_marker_matches_existing_worktree(self) -> None:
        """Marker pointing to existing worktree produces no errors."""
        lines = ["- [ ] **Task** → `my-slug` — description"]
        errors, warnings = check_worktree_markers(lines, worktree_slugs={"my-slug"})
        assert errors == []
        assert warnings == []

    def test_marker_points_to_nonexistent_worktree(self) -> None:
        """Marker pointing to missing worktree produces error."""
        lines = ["- [ ] **Task** → `missing-slug` — description"]
        errors, warnings = check_worktree_markers(lines, worktree_slugs=set())
        assert len(errors) == 1
        assert "missing-slug" in errors[0]
        assert warnings == []

    def test_worktree_not_referenced_by_marker(self) -> None:
        """Worktree with no corresponding marker produces warning."""
        lines = ["- [ ] **Task** — description (no marker)"]
        errors, warnings = check_worktree_markers(lines, worktree_slugs={"orphan-slug"})
        assert errors == []
        assert len(warnings) == 1
        assert "orphan-slug" in warnings[0]

    def test_multiple_markers_mixed_valid_invalid(self) -> None:
        """Multiple markers with some valid, some invalid."""
        lines = [
            "- [ ] **Task 1** → `valid-slug` — desc",
            "- [ ] **Task 2** → `missing-slug` — desc",
            "- [ ] **Task 3** — no marker",
        ]
        errors, warnings = check_worktree_markers(
            lines, worktree_slugs={"valid-slug", "orphan-slug"}
        )
        assert len(errors) == 1
        assert "missing-slug" in errors[0]
        assert len(warnings) == 1
        assert "orphan-slug" in warnings[0]

    def test_non_task_lines_ignored(self) -> None:
        """Non-task lines without worktree markers not processed."""
        lines = [
            "## Section Header",
            "Regular text",
            "- [ ] **Task** → `valid-slug` — desc",
        ]
        errors, warnings = check_worktree_markers(lines, worktree_slugs={"valid-slug"})
        assert errors == []
        assert warnings == []

    def test_multiple_errors_accumulate(self) -> None:
        """Multiple invalid markers all reported."""
        lines = [
            "- [ ] **Task 1** → `missing-1` — desc",
            "- [ ] **Task 2** → `missing-2` — desc",
            "- [ ] **Task 3** → `missing-3` — desc",
        ]
        errors, _warnings = check_worktree_markers(lines, worktree_slugs=set())
        assert len(errors) == 3
        assert all(
            slug in str(errors) for slug in ["missing-1", "missing-2", "missing-3"]
        )

    def test_multiple_warnings_accumulate(self) -> None:
        """Multiple unreferenced worktrees all warned."""
        lines = ["- [ ] **Task** — no marker"]
        errors, warnings = check_worktree_markers(
            lines, worktree_slugs={"orphan-1", "orphan-2", "orphan-3"}
        )
        assert errors == []
        assert len(warnings) == 3
        assert all(
            slug in str(warnings) for slug in ["orphan-1", "orphan-2", "orphan-3"]
        )

    def test_task_marker_with_multiple_worktrees(self) -> None:
        """Single marker found among multiple available worktrees."""
        lines = ["- [ ] **Task** → `target` — desc"]
        errors, warnings = check_worktree_markers(
            lines, worktree_slugs={"target", "other-1", "other-2"}
        )
        assert errors == []
        assert len(warnings) == 2
        assert all(slug in str(warnings) for slug in ["other-1", "other-2"])

    def test_line_numbers_in_errors(self) -> None:
        """Error messages include line numbers for debugging."""
        lines = [
            "Header",
            "- [ ] **Task** → `missing-slug` — desc",
        ]
        errors, _warnings = check_worktree_markers(lines, worktree_slugs=set())
        assert len(errors) == 1
        assert "line" in errors[0].lower() or "2" in errors[0]
