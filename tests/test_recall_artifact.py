"""Tests for recall artifact parsing."""

from claudeutils.recall_cli.artifact import parse_entry_keys_section


def test_parse_entry_keys_section_returns_entries() -> None:
    """Parse Entry Keys section and return entry lines."""
    content = """\
# Title

Preamble

## Entry Keys

when foo — annotation
how bar
"""
    result = parse_entry_keys_section(content)
    assert result == ["when foo — annotation", "how bar"]


def test_parse_entry_keys_section_excludes_blank_lines() -> None:
    """Blank lines within section are excluded from result."""
    content = """\
## Entry Keys

when foo

how bar
"""
    result = parse_entry_keys_section(content)
    assert result == ["when foo", "how bar"]


def test_parse_entry_keys_section_not_included_before_heading() -> None:
    """Content above Entry Keys heading is not included."""
    content = """\
when should not include
how this either

## Entry Keys

when foo
how bar
"""
    result = parse_entry_keys_section(content)
    assert result == ["when foo", "how bar"]


def test_parse_entry_keys_section_returns_none_when_heading_missing() -> None:
    """Returns None if Entry Keys heading not found."""
    content = """\
# Title

Some content

More content
"""
    result = parse_entry_keys_section(content)
    assert result is None


def test_parse_entry_keys_section_missing() -> None:
    """Empty section (only blanks) returns empty list, not None."""
    content = """\
## Entry Keys


"""
    result = parse_entry_keys_section(content)
    assert result == []


def test_parse_entry_keys_skips_comments() -> None:
    """Lines starting with # within section are excluded."""
    content = """\
## Entry Keys

when foo
# this is a comment
how bar
# another comment
"""
    result = parse_entry_keys_section(content)
    assert result == ["when foo", "how bar"]
