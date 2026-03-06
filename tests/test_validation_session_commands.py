"""Tests for session.md command semantic validation."""

from claudeutils.validation.session_commands import (
    check_command_presence,
    check_command_semantics,
    check_skill_allowlist,
)


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


class TestCheckCommandPresence:
    """Tests for check_command_presence (FR-1)."""

    def test_pending_task_without_command_is_error(self) -> None:
        """Pending task without backtick command produces error."""
        lines = ["- [ ] **My Task** — plain description | sonnet"]
        errors = check_command_presence(lines)
        assert len(errors) == 1
        assert "line 1" in errors[0]
        assert "My Task" in errors[0]
        assert "missing command" in errors[0].lower()

    def test_pending_task_with_command_passes(self) -> None:
        """Pending task with backtick command passes."""
        lines = ["- [ ] **My Task** — `/design plans/foo/` | sonnet"]
        errors = check_command_presence(lines)
        assert errors == []

    def test_in_progress_without_command_is_error(self) -> None:
        """In-progress task without command produces error."""
        lines = ["- [>] **Active Task** — doing stuff | sonnet"]
        errors = check_command_presence(lines)
        assert len(errors) == 1
        assert "Active Task" in errors[0]

    def test_completed_without_command_passes(self) -> None:
        """Completed task without command is exempt."""
        lines = ["- [x] **Done Task** — was completed"]
        errors = check_command_presence(lines)
        assert errors == []

    def test_blocked_without_command_passes(self) -> None:
        """Blocked task without command is exempt."""
        lines = ["- [!] **Blocked Task** — waiting on signal"]
        errors = check_command_presence(lines)
        assert errors == []

    def test_failed_without_command_passes(self) -> None:
        """Failed task without command is exempt."""
        lines = ["- [\u2020] **Failed Task** — terminal failure"]
        errors = check_command_presence(lines)
        assert errors == []

    def test_canceled_without_command_passes(self) -> None:
        """Canceled task without command is exempt."""
        lines = ["- [-] **Canceled Task** — user canceled"]
        errors = check_command_presence(lines)
        assert errors == []

    def test_mixed_checkboxes(self) -> None:
        """Only pending and in-progress without commands produce errors."""
        lines = [
            "- [ ] **Pending No Cmd** — description",
            "- [x] **Done No Cmd** — description",
            "- [>] **Active No Cmd** — description",
            "- [!] **Blocked No Cmd** — description",
            "- [\u2020] **Failed No Cmd** — description",
            "- [-] **Canceled No Cmd** — description",
        ]
        errors = check_command_presence(lines)
        assert len(errors) == 2
        assert "Pending No Cmd" in errors[0]
        assert "Active No Cmd" in errors[1]


class TestCheckSkillAllowlist:
    """Tests for check_skill_allowlist (FR-2)."""

    def test_known_skill_passes(self) -> None:
        """Command with known skill name passes."""
        lines = ["- [ ] **My Task** — `/design plans/foo/` | opus"]
        errors = check_skill_allowlist(lines)
        assert errors == []

    def test_unknown_skill_is_error(self) -> None:
        """Command with unknown skill name produces error."""
        lines = ["- [ ] **My Task** — `/frobnicate plans/foo/` | sonnet"]
        errors = check_skill_allowlist(lines)
        assert len(errors) == 1
        assert "line 1" in errors[0]
        assert "My Task" in errors[0]
        assert "frobnicate" in errors[0]

    def test_all_allowlisted_skills_pass(self) -> None:
        """All 7 workflow skills pass validation."""
        skills = [
            "requirements",
            "design",
            "runbook",
            "orchestrate",
            "deliverable-review",
            "inline",
            "ground",
        ]
        for skill in skills:
            lines = [f"- [ ] **Task** — `/{skill} plans/foo/` | sonnet"]
            errors = check_skill_allowlist(lines)
            assert errors == [], f"/{skill} should be allowed"

    def test_non_slash_command_not_validated(self) -> None:
        """Commands without / prefix are not checked."""
        lines = ["- [ ] **My Task** — `just some-recipe` | sonnet"]
        errors = check_skill_allowlist(lines)
        assert errors == []

    def test_completed_task_not_validated(self) -> None:
        """Completed tasks are exempt from allowlist check."""
        lines = ["- [x] **Done** — `/frobnicate plans/foo/` | sonnet"]
        errors = check_skill_allowlist(lines)
        assert errors == []
