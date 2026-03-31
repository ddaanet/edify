"""Tests for backtick path validation in session.md task metadata."""

from pathlib import Path

from edify.validation.session_paths import (
    check_task_paths,
    extract_paths_from_line,
)


class TestExtractPathsFromLine:
    """Tests for extract_paths_from_line."""

    def test_standalone_path(self) -> None:
        """Standalone backtick-wrapped path extracted."""
        line = "- [ ] **Task** — `plans/foo/design.md` | sonnet"
        assert extract_paths_from_line(line) == ["plans/foo/design.md"]

    def test_skill_command_with_path(self) -> None:
        """Skill command path argument extracted."""
        line = "- [ ] **Task** — `/design plans/foo/requirements.md` | opus"
        assert extract_paths_from_line(line) == ["plans/foo/requirements.md"]

    def test_runbook_command_with_path(self) -> None:
        """Runbook skill command path extracted."""
        line = "- [ ] **Task** — `/runbook plans/foo/outline.md` | sonnet"
        assert extract_paths_from_line(line) == ["plans/foo/outline.md"]

    def test_inline_command_with_execute(self) -> None:
        """Inline command extracts path, drops execute token."""
        line = "- [ ] **Task** — `/inline plans/foo execute` | sonnet"
        assert extract_paths_from_line(line) == ["plans/foo"]

    def test_cli_tool_name_skipped(self) -> None:
        """CLI tool names starting with _ are skipped."""
        line = "- [ ] **Task** — `_worktree ls` stuff"
        assert extract_paths_from_line(line) == []

    def test_flags_skipped(self) -> None:
        """Flags starting with -- are skipped."""
        line = "- [ ] **Task** — `--force` flag"
        assert extract_paths_from_line(line) == []

    def test_code_reference_skipped(self) -> None:
        """Code references without / are skipped."""
        line = "- [ ] **Task** — `_merge_session_contents` update"
        assert extract_paths_from_line(line) == []

    def test_glob_pattern_skipped(self) -> None:
        """Glob patterns with * are skipped."""
        line = "- [ ] **Task** — block `cd * && *` pattern"
        assert extract_paths_from_line(line) == []

    def test_multiple_paths(self) -> None:
        """Multiple backtick paths extracted."""
        line = (
            "- [ ] **Task** — `/design plans/foo/req.md` (brief: `plans/foo/brief.md`)"
        )
        result = extract_paths_from_line(line)
        assert "plans/foo/req.md" in result
        assert "plans/foo/brief.md" in result

    def test_deliverable_review_command(self) -> None:
        """Deliverable-review command path extracted."""
        line = "- [ ] **Review** — `/deliverable-review plans/foo` | opus"
        assert extract_paths_from_line(line) == ["plans/foo"]

    def test_no_backticks_returns_empty(self) -> None:
        """Line without backticks returns empty list."""
        line = "- [ ] **Task** — plain description | sonnet"
        assert extract_paths_from_line(line) == []

    def test_orchestrate_command_without_path(self) -> None:
        """Orchestrate with slug (no /) returns empty."""
        line = "- [ ] **Task** — `/orchestrate my-slug` | sonnet"
        assert extract_paths_from_line(line) == []

    def test_bare_skill_commands_skipped(self) -> None:
        """Bare skill commands like /when, /how, /recall are not paths."""
        line = (
            "- [ ] **Task** — phase out `/when` and `/how` as separate skills, "
            "ensure `/recall` covers reactive lookups"
        )
        assert extract_paths_from_line(line) == []

    def test_bare_skill_with_path_not_skipped(self) -> None:
        """Skill command with path argument is still extracted."""
        line = "- [ ] **Task** — `/design plans/foo/req.md` | opus"
        assert extract_paths_from_line(line) == ["plans/foo/req.md"]


class TestCheckTaskPaths:
    """Tests for check_task_paths."""

    def test_existing_path_no_error(self, tmp_path: Path) -> None:
        """Task with path pointing to existing file produces no error."""
        plans = tmp_path / "plans" / "foo"
        plans.mkdir(parents=True)
        (plans / "design.md").write_text("# Design")
        lines = ["- [ ] **Task** — `plans/foo/design.md` | sonnet"]
        errors = check_task_paths(lines, tmp_path)
        assert errors == []

    def test_missing_path_error(self, tmp_path: Path) -> None:
        """Task with path pointing to missing file produces error."""
        lines = ["- [ ] **Task** — `plans/nonexistent/design.md` | sonnet"]
        errors = check_task_paths(lines, tmp_path)
        assert len(errors) == 1
        assert "path not found" in errors[0]
        assert "plans/nonexistent/design.md" in errors[0]

    def test_tmp_path_error(self, tmp_path: Path) -> None:
        """Task with tmp/ path produces error."""
        lines = ["- [ ] **Task** — `tmp/score.py` | sonnet"]
        errors = check_task_paths(lines, tmp_path)
        assert len(errors) == 1
        assert "tmp/ path" in errors[0]

    def test_plans_claude_error(self, tmp_path: Path) -> None:
        """Task with plans/claude reference produces error."""
        lines = ["- [ ] **Task** — `plans/claude/something` | sonnet"]
        errors = check_task_paths(lines, tmp_path)
        assert len(errors) == 1
        assert "plans/claude" in errors[0]

    def test_absolute_path_error(self, tmp_path: Path) -> None:
        """Task with absolute path produces error."""
        lines = ["- [ ] **Task** — `/Users/david/code/file.py` | sonnet"]
        errors = check_task_paths(lines, tmp_path)
        assert len(errors) == 1
        assert "absolute path" in errors[0]

    def test_non_task_lines_skipped(self, tmp_path: Path) -> None:
        """Non-task lines are not checked for paths."""
        lines = [
            "## Reference Files",
            "- `plans/nonexistent.md` — this is a ref, not a task",
        ]
        errors = check_task_paths(lines, tmp_path)
        assert errors == []

    def test_skill_command_path_validated(self, tmp_path: Path) -> None:
        """Path inside skill command is validated for existence."""
        lines = ["- [ ] **Task** — `/design plans/missing/requirements.md` | opus"]
        errors = check_task_paths(lines, tmp_path)
        assert len(errors) == 1
        assert "path not found" in errors[0]
        assert "plans/missing/requirements.md" in errors[0]

    def test_skill_command_existing_path_ok(self, tmp_path: Path) -> None:
        """Skill command with existing path produces no error."""
        plans = tmp_path / "plans" / "my-job"
        plans.mkdir(parents=True)
        (plans / "requirements.md").write_text("# Req")
        lines = ["- [ ] **Task** — `/design plans/my-job/requirements.md` | opus"]
        errors = check_task_paths(lines, tmp_path)
        assert errors == []

    def test_multiple_errors_accumulated(self, tmp_path: Path) -> None:
        """Multiple path issues in different tasks all reported."""
        lines = [
            "- [ ] **A** — `tmp/bad.py` | sonnet",
            "- [ ] **B** — `plans/missing/x.md` | opus",
            "- [ ] **C** — `/absolute/path` | haiku",
        ]
        errors = check_task_paths(lines, tmp_path)
        assert len(errors) == 3
