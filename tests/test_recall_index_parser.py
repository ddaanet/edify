"""Tests for memory-index.md parser."""

from pathlib import Path

from claudeutils.recall.index_parser import IndexEntry, parse_memory_index


def test_parse_memory_index_simple_entry(tmp_path: Path) -> None:
    """Parse simple index entry with key — description."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\n"
        "TDD RED Phase — verify behavior with mocking fixtures\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 1
    assert result[0].key == "TDD RED Phase"
    assert result[0].description == "verify behavior with mocking fixtures"
    assert result[0].referenced_file == "agents/decisions/testing.md"
    assert result[0].section == "agents/decisions/testing.md"


def test_parse_memory_index_multiple_entries(tmp_path: Path) -> None:
    """Parse multiple entries from same section."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\n"
        "Entry one — first description\n"
        "Entry two — second description\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 2
    assert result[0].key == "Entry one"
    assert result[1].key == "Entry two"
    assert all(e.referenced_file == "agents/decisions/testing.md" for e in result)


def test_parse_memory_index_multiple_sections(tmp_path: Path) -> None:
    """Parse entries from multiple sections."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/file1.md\n\n"
        "Entry one — description one\n\n"
        "## agents/decisions/file2.md\n\n"
        "Entry two — description two\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 2
    assert result[0].referenced_file == "agents/decisions/file1.md"
    assert result[1].referenced_file == "agents/decisions/file2.md"


def test_parse_memory_index_skip_behavioral_rules(tmp_path: Path) -> None:
    """Skip 'Behavioral Rules' section (fragments already loaded)."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## Behavioral Rules (fragments — already loaded)\n\n"
        "This should be skipped — fragments are already loaded\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 0


def test_parse_memory_index_skip_technical_decisions(tmp_path: Path) -> None:
    """Skip 'Technical Decisions' section (mixed targets)."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## Technical Decisions (mixed — check entry for specific file)\n\n"
        "This should be skipped — no clear file target\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 0


def test_parse_memory_index_keyword_extraction(tmp_path: Path) -> None:
    """Keywords extracted from key and description."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\n"
        "TDD RED Phase — verify behavior with mocking fixtures\n"
    )

    result = parse_memory_index(index_file)
    entry = result[0]

    # Keywords should include TDD, RED, Phase, verify, behavior, mocking, fixtures
    # Stopwords like "with", "the", "and" should be excluded
    assert "tdd" in entry.keywords
    assert "red" in entry.keywords
    assert "phase" in entry.keywords
    assert "verify" in entry.keywords
    assert "behavior" in entry.keywords
    assert "mocking" in entry.keywords
    assert "fixtures" in entry.keywords
    assert "with" not in entry.keywords
    assert "the" not in entry.keywords


def test_parse_memory_index_nonexistent_file() -> None:
    """Nonexistent file returns empty list."""
    result = parse_memory_index(Path("/nonexistent/file.md"))
    assert result == []


def test_parse_memory_index_empty_file(tmp_path: Path) -> None:
    """Empty file returns empty list."""
    index_file = tmp_path / "empty.md"
    index_file.write_text("")

    result = parse_memory_index(index_file)
    assert len(result) == 0


def test_parse_memory_index_no_em_dash_lines(tmp_path: Path) -> None:
    """Lines without em-dash are skipped."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\n"
        "This line has no em-dash\n"
        "Valid entry — has em-dash\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 1
    assert result[0].key == "Valid entry"


def test_parse_memory_index_entry_model() -> None:
    """IndexEntry model validates fields."""
    entry = IndexEntry(
        key="Test key",
        description="Test description",
        referenced_file="test/file.md",
        section="Test Section",
        keywords=frozenset({"test", "key"}),
    )

    assert entry.key == "Test key"
    assert entry.referenced_file == "test/file.md"
    assert "test" in entry.keywords


def test_parse_memory_index_real_format(tmp_path: Path) -> None:
    """Parse realistic memory-index.md format."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "# Memory Index\n\n"
        "## Behavioral Rules (fragments — already loaded)\n\n"
        "Never auto-commit — commit only on explicit request\n\n"
        "## agents/decisions/implementation-notes.md\n\n"
        "@ references limitation — CLAUDE.md @ syntax only works in CLAUDE.md\n"
        "SessionStart hook limitation — output discarded for new sessions\n\n"
        "## agents/decisions/testing.md\n\n"
        "TDD RED Phase — verify behavior with mocking\n"
    )

    result = parse_memory_index(index_file)
    # Should skip Behavioral Rules section
    assert len(result) == 3
    assert all(
        e.referenced_file
        in ["agents/decisions/implementation-notes.md", "agents/decisions/testing.md"]
        for e in result
    )


def test_recall_parser_when_format(tmp_path: Path) -> None:
    """Parse /when and /how format entries in memory index."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "# Memory Index\n\n"
        "## agents/decisions/testing.md\n\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/how structure test fixtures | setup, teardown, fixtures\n"
        "Old em-dash format — should be parsed too\n\n"
        "## agents/decisions/implementation-notes.md\n\n"
        "/when refactoring code | duplication, extraction, abstraction\n"
    )

    result = parse_memory_index(index_file)

    # Should have 3 new format + 1 old format = 4 entries total
    assert len(result) == 4

    # Check first entry (/when writing mock tests)
    when_entry = next(e for e in result if e.key == "writing mock tests")
    assert when_entry.referenced_file == "agents/decisions/testing.md"
    assert "writing" in when_entry.keywords
    assert "mock" in when_entry.keywords
    assert "tests" in when_entry.keywords
    assert "patch" in when_entry.keywords
    assert "test" in when_entry.keywords
    assert "doubles" in when_entry.keywords

    # Check second entry (/how structure)
    how_entry = next(e for e in result if e.key == "structure test fixtures")
    assert how_entry.referenced_file == "agents/decisions/testing.md"
    assert "structure" in how_entry.keywords
    assert "fixtures" in how_entry.keywords

    # Check third entry (/when refactoring)
    refactor_entry = next(e for e in result if e.key == "refactoring code")
    assert refactor_entry.referenced_file == "agents/decisions/implementation-notes.md"
    assert "refactoring" in refactor_entry.keywords
    assert "code" in refactor_entry.keywords

    # Check fourth entry (old format)
    old_format_entry = next(e for e in result if e.key == "Old em-dash format")
    assert old_format_entry.referenced_file == "agents/decisions/testing.md"
    assert old_format_entry.description == "should be parsed too"


def test_keyword_extraction_from_triggers(tmp_path: Path) -> None:
    """Keywords extracted from trigger + extras in /when and /how format."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "# Memory Index\n\n"
        "## agents/decisions/testing.md\n\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/how encode paths | path encoding, URL encoding\n"
    )

    result = parse_memory_index(index_file)

    # Check /when entry — keywords from trigger + extras
    when_entry = next(e for e in result if e.key == "writing mock tests")
    # Trigger: "writing mock tests" + Extras: "mock patch, test doubles"
    # Should include: writing, mock, tests, patch, doubles
    # Should exclude: when (operator word), commas stripped
    assert "writing" in when_entry.keywords
    assert "mock" in when_entry.keywords
    assert "tests" in when_entry.keywords
    assert "patch" in when_entry.keywords
    assert "test" in when_entry.keywords
    assert "doubles" in when_entry.keywords
    assert "when" not in when_entry.keywords

    # Check /how entry — keywords from trigger + extras
    how_entry = next(e for e in result if e.key == "encode paths")
    # Trigger: "encode paths" + Extras: "path encoding, URL encoding"
    # Should include: encode, paths, path, encoding, url
    # Should exclude: how (operator word)
    assert "encode" in how_entry.keywords
    assert "paths" in how_entry.keywords
    assert "path" in how_entry.keywords
    assert "encoding" in how_entry.keywords
    assert "url" in how_entry.keywords
    assert "how" not in how_entry.keywords
