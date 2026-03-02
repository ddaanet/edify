"""Tests for session.md command semantic validation."""

from claudeutils.validation.session_commands import check_command_semantics


class TestCheckCommandSemantics:
    """Tests for check_command_semantics."""

    def test_task_with_no_command(self) -> None:
        """Task with no command produces no errors."""
        lines = ["- [ ] **My Task** — plain description"]
        errors = check_command_semantics(lines)
        assert errors == []

    def test_task_with_valid_command(self) -> None:
        """Task with valid command produces no errors."""
        lines = ["- [ ] **My Task** — `/design plans/foo/requirements.md` | opus"]
        errors = check_command_semantics(lines)
        assert errors == []

    def test_inline_plans_execute_pattern(self) -> None:
        """Task with /inline plans/.* execute flagged as error."""
        lines = ["- [ ] **Bad Task** — `/inline plans/foo execute` | sonnet"]
        errors = check_command_semantics(lines)
        assert len(errors) == 1
        assert "line 1" in errors[0]
        assert "Bad Task" in errors[0]
        assert "bypasses Phase 2 recall" in errors[0]

    def test_inline_plans_with_subpath_execute(self) -> None:
        """Subpath with execute is flagged as error."""
        lines = [
            "- [ ] **Bad Task** — `/inline plans/some-plan/design.md execute` | opus"
        ]
        errors = check_command_semantics(lines)
        assert len(errors) == 1
        assert "line 1" in errors[0]

    def test_multiple_tasks_one_with_anti_pattern(self) -> None:
        """Multiple tasks, one with anti-pattern produces one error."""
        lines = [
            "- [ ] **Good Task 1** — `/design plans/foo` | opus",
            "- [ ] **Bad Task** — `/inline plans/bar execute` | sonnet",
            "- [ ] **Good Task 2** — plain description",
        ]
        errors = check_command_semantics(lines)
        assert len(errors) == 1
        assert "line 2" in errors[0]
        assert "Bad Task" in errors[0]

    def test_inline_plans_without_execute(self) -> None:
        """Inline plans without execute is not an anti-pattern."""
        lines = ["- [ ] **Task** — `/inline plans/foo/design.md` | sonnet"]
        errors = check_command_semantics(lines)
        assert errors == []

    def test_non_task_lines_ignored(self) -> None:
        """Non-task lines are ignored."""
        lines = [
            "## Some Section",
            "- Regular list item",
            "  - Indented item",
            "Some plain text",
            "- [ ] **Task** — `/inline plans/foo execute`",
        ]
        errors = check_command_semantics(lines)
        assert len(errors) == 1
        assert "line 5" in errors[0]

    def test_empty_lines_ignored(self) -> None:
        """Empty lines are ignored."""
        lines = [
            "",
            "- [ ] **Task 1** — `/design foo`",
            "",
            "- [ ] **Task 2** — `/inline plans/bar execute`",
            "",
        ]
        errors = check_command_semantics(lines)
        assert len(errors) == 1
        assert "line 4" in errors[0]
