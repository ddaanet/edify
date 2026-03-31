"""Tests for session_refs validator."""

from pathlib import Path

from edify.validation.session_refs import check_tmp_references, validate


class TestCheckTmpReferences:
    """Tests for check_tmp_references."""

    def test_no_tmp_refs(self) -> None:
        """Lines without tmp/ references return empty."""
        lines = ["# Session\n", "- plans/report.md\n", "Some text\n"]
        assert check_tmp_references(lines) == []

    def test_backtick_wrapped_tmp_ref(self) -> None:
        """Backtick-wrapped tmp/ path detected."""
        lines = ["Report at `tmp/consolidation-report.md`\n"]
        hits = check_tmp_references(lines)
        assert len(hits) == 1
        assert hits[0] == (1, "tmp/consolidation-report.md")

    def test_bare_tmp_ref(self) -> None:
        """Bare tmp/ path detected."""
        lines = ["Report: tmp/output.md\n"]
        hits = check_tmp_references(lines)
        assert len(hits) == 1
        assert hits[0] == (1, "tmp/output.md")

    def test_system_tmp_caught(self) -> None:
        """System /tmp/ paths also caught via word boundary."""
        lines = ["File at /tmp/claude/file.txt\n"]
        hits = check_tmp_references(lines)
        assert len(hits) == 1
        assert "tmp/claude/file.txt" in hits[0][1]

    def test_prose_mention_not_caught(self) -> None:
        """Prose 'tmp/ directory' not matched (space after /)."""
        lines = ["Use tmp/ directory for scratch\n"]
        assert check_tmp_references(lines) == []

    def test_bare_tmp_slash_not_caught(self) -> None:
        """Bare 'tmp/' without path content not matched."""
        lines = ["Files go to tmp/ during execution\n"]
        assert check_tmp_references(lines) == []

    def test_sentence_ending_period_not_caught(self) -> None:
        """Sentence-ending 'tmp/.' not matched (period not alphanumeric)."""
        lines = ["scratch computation goes to tmp/.\n"]
        assert check_tmp_references(lines) == []

    def test_multiple_refs_one_line(self) -> None:
        """Multiple tmp/ refs on one line all detected."""
        lines = ["See tmp/a.md and tmp/b.md\n"]
        assert len(check_tmp_references(lines)) == 2

    def test_nested_tmp_path(self) -> None:
        """Nested tmp/ paths detected."""
        lines = ["Located at tmp/claude/deep/file.txt\n"]
        hits = check_tmp_references(lines)
        assert len(hits) == 1
        assert hits[0][1] == "tmp/claude/deep/file.txt"

    def test_line_numbers_correct(self) -> None:
        """Line numbers reported accurately."""
        lines = ["clean line\n", "also clean\n", "bad tmp/report.md\n"]
        hits = check_tmp_references(lines)
        assert hits[0][0] == 3


class TestValidate:
    """Tests for validate function."""

    def _make_agents_dir(self, tmp_path: Path) -> Path:
        agents = tmp_path / "agents"
        agents.mkdir()
        return agents

    def test_clean_session_no_errors(self, tmp_path: Path) -> None:
        """Clean session files produce no errors."""
        agents = self._make_agents_dir(tmp_path)
        (agents / "session.md").write_text("# Session\n\n## Pending Tasks\n")
        (agents / "learnings.md").write_text("# Learnings\n")
        assert validate(tmp_path) == []

    def test_tmp_ref_in_session(self, tmp_path: Path) -> None:
        """Tmp/ reference in session.md detected."""
        agents = self._make_agents_dir(tmp_path)
        (agents / "session.md").write_text(
            "# Session\n\n## Reference Files\n\n"
            "- `tmp/report.md` \u2014 Bad reference\n"
        )
        errors = validate(tmp_path)
        assert len(errors) == 1
        assert "tmp/" in errors[0]
        assert "session.md" in errors[0]

    def test_tmp_ref_in_learnings(self, tmp_path: Path) -> None:
        """Tmp/ reference in learnings.md detected."""
        agents = self._make_agents_dir(tmp_path)
        (agents / "learnings.md").write_text(
            "# Learnings\n\nSee tmp/analysis.md for details\n"
        )
        errors = validate(tmp_path)
        assert len(errors) == 1
        assert "learnings.md" in errors[0]

    def test_missing_files_no_error(self, tmp_path: Path) -> None:
        """Missing session files produce no errors."""
        assert validate(tmp_path) == []

    def test_multiple_files_multiple_errors(self, tmp_path: Path) -> None:
        """Errors from multiple files all reported."""
        agents = self._make_agents_dir(tmp_path)
        (agents / "session.md").write_text("Ref: tmp/a.md\n")
        (agents / "learnings.md").write_text("Ref: tmp/b.md\n")
        errors = validate(tmp_path)
        assert len(errors) == 2

    def test_versioned_path_ok(self, tmp_path: Path) -> None:
        """Non-tmp/ paths produce no errors."""
        agents = self._make_agents_dir(tmp_path)
        (agents / "session.md").write_text(
            "- `plans/reports/analysis.md` \u2014 Good reference\n"
        )
        assert validate(tmp_path) == []
