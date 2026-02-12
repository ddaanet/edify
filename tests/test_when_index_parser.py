"""Tests for index_parser module."""

from pathlib import Path

from claudeutils.when.index_parser import parse_index


def test_parse_when_entry_basic(tmp_path: Path) -> None:
    """Parse /when and /how format entries with triggers and extras."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## Helpers\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/how encode paths | path encoding\n"
    )

    entries = parse_index(index_file)

    # Find /when entry
    when_entry = next((e for e in entries if e.operator == "when"), None)
    assert when_entry is not None
    assert when_entry.operator == "when"
    assert when_entry.trigger == "writing mock tests"
    assert when_entry.extra_triggers == ["mock patch", "test doubles"]

    # Find /how entry
    how_entry = next((e for e in entries if e.operator == "how"), None)
    assert how_entry is not None
    assert how_entry.operator == "how"
    assert how_entry.trigger == "encode paths"
    assert how_entry.extra_triggers == ["path encoding"]


def test_operator_extraction(tmp_path: Path) -> None:
    """Only /when and /how operators are valid; all others skipped."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## Test Section\n"
        "\n"
        "/when valid operator\n"
        "/how also valid\n"
        "/what not valid\n"
        "/why not valid\n"
        "bare text ignored\n"
        "## Header ignored\n"
    )

    entries = parse_index(index_file)

    assert len(entries) == 2
    assert entries[0].operator == "when"
    assert entries[1].operator == "how"


def test_trigger_splitting(tmp_path: Path) -> None:
    """Split triggers and extras on pipe with edge case handling.

    Handles trailing pipes, empty segments, and whitespace trimming.
    """
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## Test Section\n"
        "\n"
        "/when auth fails | auth error, login failure\n"
        "/when auth fails\n"
        "/when auth | \n"
        "/when auth fails | single\n"
        "/when mock patch | test doubles\n"
    )

    entries = parse_index(index_file)

    # auth fails with multiple extras
    assert entries[0].trigger == "auth fails"
    assert entries[0].extra_triggers == ["auth error", "login failure"]

    # auth fails with no extras
    assert entries[1].trigger == "auth fails"
    assert entries[1].extra_triggers == []

    # auth with trailing pipe (empty extras filtered)
    assert entries[2].trigger == "auth"
    assert entries[2].extra_triggers == []

    # auth fails with single extra
    assert entries[3].trigger == "auth fails"
    assert entries[3].extra_triggers == ["single"]

    # extra triggers trimmed of whitespace
    assert entries[4].trigger == "mock patch"
    assert entries[4].extra_triggers == ["test doubles"]


def test_format_validation(tmp_path: Path) -> None:
    """Validate format: operator prefix, pipe separator, non-empty triggers."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## Valid Entries\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "\n"
        "## Invalid Cases\n"
        "\n"
        "/when\n"
        "/when | extras\n"
        "/when   | extras\n"
        "/when valid trigger | ,,,\n"
    )

    entries = parse_index(index_file)

    # Only valid entries should be included
    assert len(entries) == 2

    # First entry is the valid one from first section
    assert entries[0].trigger == "writing mock tests"
    assert entries[0].extra_triggers == ["mock patch", "test doubles"]
    assert entries[0].section == "Valid Entries"

    # Second entry is from third line of invalid section (the one with valid trigger)
    assert entries[1].trigger == "valid trigger"
    assert entries[1].extra_triggers == []
    assert entries[1].section == "Invalid Cases"
