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
