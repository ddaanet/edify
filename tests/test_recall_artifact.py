"""Tests for recall artifact parsing."""

from edify.recall_cli.artifact import parse_entry_keys_section, parse_trigger


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


def test_parse_trigger_strips_annotation() -> None:
    """Annotation after em dash is stripped from entry line."""
    assert parse_trigger("when foo — some annotation") == "when foo"
    assert parse_trigger("how bar — another note") == "how bar"
    assert parse_trigger("when already prefixed") == "when already prefixed"
    assert parse_trigger("how to do something") == "how to do something"
    assert parse_trigger("no annotation") == "when no annotation"


def test_parse_trigger_detects_operator() -> None:
    """Bare trigger without operator gets prepended with 'when'."""
    assert parse_trigger("bare trigger — note") == "when bare trigger"
    assert parse_trigger("bare trigger") == "when bare trigger"
    assert parse_trigger("when foo") == "when foo"
    assert parse_trigger("how bar") == "how bar"
