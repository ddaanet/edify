"""Tests for task name format validation."""

from pathlib import Path

from edify.validation.tasks import validate, validate_task_name_format


class TestValidateTaskNameFormat:
    """Tests for validate_task_name_format function."""

    def test_validate_task_name_format_valid(self) -> None:
        """Valid task names return empty list."""
        assert validate_task_name_format("Build docs") == []
        assert validate_task_name_format("Fix bug-123") == []
        assert validate_task_name_format("Add v2.0 support") == []
        assert validate_task_name_format("a") == []
        assert validate_task_name_format("12345678901234567890ABCDE") == []

    def test_validate_task_name_format_invalid_chars(self) -> None:
        """Invalid characters are rejected."""
        errors = validate_task_name_format("task_name")
        assert len(errors) > 0
        assert any("forbidden character '_'" in e for e in errors)

        errors = validate_task_name_format("task@host")
        assert len(errors) > 0
        assert any("forbidden character '@'" in e for e in errors)

        errors = validate_task_name_format("task/path")
        assert len(errors) > 0
        assert any("forbidden character '/'" in e for e in errors)

        errors = validate_task_name_format("task:colon")
        assert len(errors) > 0
        assert any("forbidden character ':'" in e for e in errors)

    def test_validate_task_name_format_length(self) -> None:
        """Length and empty name constraints."""
        # Exactly 26 chars - exceeds limit
        errors = validate_task_name_format("12345678901234567890ABCDEF")
        assert len(errors) > 0
        assert any("exceeds 25 character limit (26 chars)" in e for e in errors)

        # 29 chars - exceeds limit
        errors = validate_task_name_format("This is a very long task name")
        assert len(errors) > 0
        assert any("exceeds 25 character limit (29 chars)" in e for e in errors)

        # Empty string
        errors = validate_task_name_format("")
        assert len(errors) > 0
        assert any("empty or whitespace-only" in e for e in errors)

        # Whitespace only
        errors = validate_task_name_format("   ")
        assert len(errors) > 0
        assert any("empty or whitespace-only" in e for e in errors)


class TestValidateTaskNameFormatIntegration:
    """Tests for format validation integration in validate() function."""

    def test_validate_task_name_format_integration(self, tmp_path: Path) -> None:
        """Format validation is integrated into validate() function."""
        (tmp_path / "agents").mkdir()
        (tmp_path / "agents" / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **Fix_bug** — details\n"
        )
        (tmp_path / "agents" / "learnings.md").write_text("# Learnings\n")

        errors = validate("agents/session.md", "agents/learnings.md", tmp_path)
        assert len(errors) > 0
        assert any("Fix_bug" in e and "forbidden character '_'" in e for e in errors)

        # Create session.md with 26-character task name
        (tmp_path / "agents" / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n"
            "- [ ] **12345678901234567890ABCDEF** — details\n"
        )
        errors = validate("agents/session.md", "agents/learnings.md", tmp_path)
        assert len(errors) > 0
        assert any("exceeds 25 character limit" in e for e in errors)
