"""Tests for shared task-line parsing module."""

from edify.validation.task_parsing import VALID_CHECKBOXES, parse_task_line


class TestParseTaskLine:
    """Tests for parse_task_line."""

    def test_basic_pending_task(self) -> None:
        """Parse basic pending task with name and description."""
        result = parse_task_line("- [ ] **My Task** — some description")
        assert result is not None
        assert result.name == "My Task"
        assert result.checkbox == " "

    def test_completed_task(self) -> None:
        """Parse completed task."""
        result = parse_task_line("- [x] **Done Task** — finished")
        assert result is not None
        assert result.name == "Done Task"
        assert result.checkbox == "x"

    def test_in_progress_task(self) -> None:
        """Parse in-progress task."""
        result = parse_task_line("- [>] **Active Task** — working")
        assert result is not None
        assert result.checkbox == ">"

    def test_blocked_task(self) -> None:
        """Parse blocked task."""
        result = parse_task_line("- [!] **Blocked Task** — waiting")
        assert result is not None
        assert result.checkbox == "!"

    def test_failed_task(self) -> None:
        """Parse failed task (\u2020 dagger)."""
        result = parse_task_line("- [\u2020] **Failed Task** \u2014 terminal")
        assert result is not None
        assert result.checkbox == "\u2020"

    def test_canceled_task(self) -> None:
        """Parse canceled task (hyphen)."""
        result = parse_task_line("- [-] **Canceled Task** \u2014 absorbed")
        assert result is not None
        assert result.checkbox == "-"

    def test_non_task_line_returns_none(self) -> None:
        """Non-task lines return None."""
        assert parse_task_line("Just some text") is None
        assert parse_task_line("## Section Header") is None
        assert parse_task_line("  - indented sub-item") is None
        assert parse_task_line("") is None

    def test_command_extraction(self) -> None:
        """Extract backtick-wrapped command after em dash."""
        result = parse_task_line(
            "- [ ] **My Task** — `/design plans/foo/requirements.md` | sonnet"
        )
        assert result is not None
        assert result.command == "/design plans/foo/requirements.md"

    def test_no_command(self) -> None:
        """Task without backtick command has None command."""
        result = parse_task_line("- [ ] **My Task** — plain description")
        assert result is not None
        assert result.command is None

    def test_model_extraction(self) -> None:
        """Extract model tier from pipe-separated metadata."""
        result = parse_task_line("- [ ] **My Task** — desc | opus")
        assert result is not None
        assert result.model == "opus"

    def test_model_with_command(self) -> None:
        """Extract model when command also present."""
        result = parse_task_line("- [ ] **My Task** — `/runbook plans/x` | haiku")
        assert result is not None
        assert result.model == "haiku"
        assert result.command == "/runbook plans/x"

    def test_no_model(self) -> None:
        """Task without model tier has None model."""
        result = parse_task_line("- [ ] **My Task** — just a description")
        assert result is not None
        assert result.model is None

    def test_invalid_model_not_extracted(self) -> None:
        """Non-standard model names not extracted as model."""
        result = parse_task_line("- [ ] **My Task** — desc | gpt4")
        assert result is not None
        assert result.model is None

    def test_worktree_marker(self) -> None:
        """Extract worktree slug marker."""
        result = parse_task_line("- [ ] **My Task** → `my-slug` — desc | sonnet")
        assert result is not None
        assert result.worktree_marker == "my-slug"
        assert result.name == "My Task"

    def test_no_worktree_marker(self) -> None:
        """Task without worktree marker has None."""
        result = parse_task_line("- [ ] **My Task** — desc")
        assert result is not None
        assert result.worktree_marker is None

    def test_full_task_line(self) -> None:
        """Parse fully-specified task line with all fields."""
        line = (
            "- [ ] **Session.md validator** \u2192 `session-md-val`"
            " \u2014 `/design plans/session-validator/requirements.md`"
            " | sonnet"
        )
        result = parse_task_line(line)
        assert result is not None
        assert result.name == "Session.md validator"
        assert result.checkbox == " "
        assert result.command == "/design plans/session-validator/requirements.md"
        assert result.model == "sonnet"
        assert result.worktree_marker == "session-md-val"
        assert result.full_line == line

    def test_line_number_preserved(self) -> None:
        """Line number passed through to result."""
        result = parse_task_line("- [ ] **Task** — desc", lineno=42)
        assert result is not None
        assert result.line_number == 42

    def test_line_number_default_zero(self) -> None:
        """Default line number is 0."""
        result = parse_task_line("- [ ] **Task** — desc")
        assert result is not None
        assert result.line_number == 0

    def test_restart_flag(self) -> None:
        """Extract restart flag from metadata."""
        result = parse_task_line("- [ ] **My Task** — desc | opus | restart")
        assert result is not None
        assert result.restart is True

    def test_no_restart_flag(self) -> None:
        """Task without restart flag defaults to False."""
        result = parse_task_line("- [ ] **My Task** — desc | sonnet")
        assert result is not None
        assert result.restart is False

    def test_priority_extraction(self) -> None:
        """Extract numeric priority from metadata."""
        result = parse_task_line("- [ ] **My Task** — desc | sonnet | 2.4")
        assert result is not None
        assert result.priority == "2.4"

    def test_no_priority(self) -> None:
        """Task without priority has None."""
        result = parse_task_line("- [ ] **My Task** — desc | sonnet")
        assert result is not None
        assert result.priority is None

    def test_old_ballot_x_parsed_but_invalid(self) -> None:
        """Old [✗] marker is parsed (not silently dropped) but invalid."""
        result = parse_task_line("- [\u2717] **Old Task** \u2014 terminal")
        assert result is not None
        assert result.name == "Old Task"
        assert result.checkbox == "\u2717"
        assert result.checkbox not in VALID_CHECKBOXES

    def test_old_en_dash_parsed_but_invalid(self) -> None:
        """Old en-dash marker is parsed (not silently dropped) but invalid."""
        result = parse_task_line("- [\u2013] **Old Task** \u2014 canceled")
        assert result is not None
        assert result.name == "Old Task"
        assert result.checkbox == "\u2013"
        assert result.checkbox not in VALID_CHECKBOXES

    def test_arbitrary_checkbox_parsed(self) -> None:
        """Any single char in checkbox position is parsed."""
        result = parse_task_line("- [?] **Weird Task** \u2014 unknown")
        assert result is not None
        assert result.checkbox == "?"
        assert result.checkbox not in VALID_CHECKBOXES
