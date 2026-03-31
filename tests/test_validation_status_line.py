"""Tests for check_status_line validation."""

from edify.validation.session_structure import check_status_line


class TestCheckStatusLine:
    """Tests for check_status_line."""

    def test_valid_h1_and_status(self) -> None:
        """Valid H1 + blank line + status produces no errors."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
            "\n",
            "**Status:** Session.md validator — shared parsing landed\n",
        ]

        assert check_status_line(lines) == []

    def test_missing_h1(self) -> None:
        """File starting without H1 produces error."""
        lines = [
            "Some content\n",
            "\n",
            "**Status:** Something\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1
        assert "H1" in errors[0] or "Session Handoff" in errors[0]

    def test_h1_wrong_format(self) -> None:
        """H1 not matching 'Session Handoff: YYYY-MM-DD' produces error."""
        lines = [
            "# Session: 2026-03-02\n",
            "\n",
            "**Status:** Something\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1
        assert "Session Handoff" in errors[0]

    def test_h1_missing_date(self) -> None:
        """H1 'Session Handoff:' without date produces error."""
        lines = [
            "# Session Handoff:\n",
            "\n",
            "**Status:** Something\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1
        assert "YYYY-MM-DD" in errors[0] or "date" in errors[0].lower()

    def test_h1_invalid_date_format(self) -> None:
        """H1 with non-YYYY-MM-DD date produces error."""
        lines = [
            "# Session Handoff: 03-02-2026\n",
            "\n",
            "**Status:** Something\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1

    def test_missing_blank_line_after_h1(self) -> None:
        """Status line directly after H1 (no blank line 2) produces error."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
            "**Status:** Something\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) >= 1
        assert any("blank" in e.lower() for e in errors)

    def test_missing_status_line(self) -> None:
        """File without status line produces error."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
            "\n",
            "Some content\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1
        assert "Status" in errors[0]

    def test_status_line_not_bold(self) -> None:
        """Status line without bold formatting produces error."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
            "\n",
            "Status: Something\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1
        assert "bold" in errors[0].lower() or "**Status:**" in errors[0]

    def test_empty_status_text(self) -> None:
        """Status line with empty text after **Status:** produces error."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
            "\n",
            "**Status:**\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1
        assert "empty" in errors[0].lower()

    def test_status_text_only_whitespace(self) -> None:
        """Status line with only whitespace after **Status:** produces error."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
            "\n",
            "**Status:**   \n",
        ]

        errors = check_status_line(lines)
        assert len(errors) == 1

    def test_file_too_short(self) -> None:
        """File with fewer than 3 lines produces errors."""
        lines = [
            "# Session Handoff: 2026-03-02\n",
        ]

        errors = check_status_line(lines)
        assert len(errors) >= 1
