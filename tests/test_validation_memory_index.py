"""Tests for memory index validator."""

from pathlib import Path

import pytest

from claudeutils.validation.memory_index import extract_index_entries, validate


@pytest.fixture
def decisions_dir(tmp_path: Path) -> Path:
    """Create agents/decisions directory structure."""
    d = tmp_path / "agents" / "decisions"
    d.mkdir(parents=True)
    return d


def _write_index(tmp_path: Path, content: str) -> Path:
    """Write memory-index.md and return path."""
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_file.write_text(content)
    return index_file


def test_valid_index_with_matching_headers(tmp_path: Path, decisions_dir: Path) -> None:
    """Valid index with matching headers returns no errors."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Decision One\nContent.\n\n## Decision Two\nMore.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Decision One — First important decision with content here okay
Decision Two — Second important decision with more content great
""",
    )
    assert validate("agents/memory-index.md", tmp_path) == []


def test_orphan_semantic_header_error(tmp_path: Path, decisions_dir: Path) -> None:
    """Orphan semantic header (not in index) returns error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Missing from Index\nContent.\n"
    )
    _write_index(tmp_path, "# Memory Index\n\n## agents/decisions/test-decision.md\n")

    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "orphan semantic header 'missing from index'" in errors[0]


def test_orphan_index_entry_error(tmp_path: Path, decisions_dir: Path) -> None:
    """Orphan index entry (no matching header) returns error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Existing Header\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Nonexistent Header — Entry pointing to header that does not exist here
Existing Header — Entry that matches a real semantic header now
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "orphan index entry 'nonexistent header'" in errors[0]


def test_duplicate_index_entries_error(tmp_path: Path, decisions_dir: Path) -> None:
    """Duplicate index entries return error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Test Header\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Test Header — First entry matching the semantic header
Test Header — Second entry with the same key appearing again here
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "duplicate index entry" in errors[0]


def test_word_count_violation_error(tmp_path: Path, decisions_dir: Path) -> None:
    """Word count outside 8-15 range returns error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Short Entry\nContent.\n\n## Long Title Entry\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Short Entry — Too
Long Title Entry — This is way too many words in entry for validation purposes here
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 2
    assert any("has 4 words" in e for e in errors)
    assert any("has 16 words" in e for e in errors)


def test_missing_em_dash_separator_error(tmp_path: Path, decisions_dir: Path) -> None:
    """Missing em-dash separator returns error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Test Unique Header\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Test Unique Header just some words without em-dash separator
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert any("entry lacks em-dash separator (D-3)" in e for e in errors)


def test_entry_in_wrong_section_autofixed(tmp_path: Path, decisions_dir: Path) -> None:
    """Entry in wrong section is autofixed (no error with autofix=True)."""
    (decisions_dir / "file-one.md").write_text(
        "# File One\n\n## First Header\nContent.\n"
    )
    (decisions_dir / "file-two.md").write_text(
        "# File Two\n\n## Second Header\nContent.\n"
    )
    index = _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/file-one.md

Second Header — Entry wrongly placed in file one section here
First Header — Entry correctly in file one section here now
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content


def test_entries_out_of_order_autofixed(tmp_path: Path, decisions_dir: Path) -> None:
    """Out-of-order entries are autofixed to match source file order."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## First Header\nContent.\n\n"
        "## Second Header\nMore.\n\n## Third Header\nEven more.\n"
    )
    index = _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Third Header — Entry in wrong order but has valid content text here
First Header — Entry that should come first in section order now
Second Header — Entry in middle position with valid content today
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    first_pos = content.index("First Header")
    second_pos = content.index("Second Header")
    third_pos = content.index("Third Header")
    assert first_pos < second_pos < third_pos


def test_structural_header_entries_removed_by_autofix(
    tmp_path: Path, decisions_dir: Path
) -> None:
    """Structural header entries removed by autofix."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## .Organizational Section\nStructural.\n\n"
        "## Real Header\nSemantic.\n\n## Another Real Header\nMore semantic.\n"
    )
    index = _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Organizational Section — Entry pointing to structural section should be removed
Real Header — Entry for semantic header with content here today
Another Real Header — Another entry for second semantic header here now
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    assert "Organizational Section" not in content
    assert "Real Header" in content


def test_exempt_sections_preserved_as_is(tmp_path: Path, decisions_dir: Path) -> None:
    """Exempt sections preserved as-is during autofix."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Test Header\nContent.\n"
    )
    index = _write_index(
        tmp_path,
        """# Memory Index

## Behavioral Rules (fragments — already loaded)

Some custom rule — description that shows em-dash format here
Another rule — another entry with proper em-dash separator today

## Technical Decisions (mixed — check entry for specific file)

Technical note — entry with em-dash in technical section here
Another item — another entry with proper format today now

## agents/decisions/test-decision.md

Test Header — Entry for semantic header with content here
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    assert "Some custom rule" in content
    assert "Another rule" in content
    assert "Technical note" in content


def test_autofix_false_reports_all_issues(tmp_path: Path, decisions_dir: Path) -> None:
    """Autofix=False reports sorting issues as errors."""
    (decisions_dir / "file-one.md").write_text(
        "# File One\n\n## First Header\nContent.\n\n## Second Header\nMore.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/file-one.md

Second Header — Entry in wrong order here today ok
First Header — Entry that should come first now
""",
    )
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert len(errors) > 0
    assert any("entries not in file order" in e for e in errors)


def test_duplicate_headers_across_files_error(
    tmp_path: Path, decisions_dir: Path
) -> None:
    """Duplicate headers across files return error."""
    (decisions_dir / "file-one.md").write_text(
        "# File One\n\n## Duplicate Name\nContent.\n"
    )
    (decisions_dir / "file-two.md").write_text(
        "# File Two\n\n## Duplicate Name\nDifferent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/file-one.md

Duplicate Name — Entry for duplicate header found multiple places now

## agents/decisions/file-two.md

Duplicate Name — Another entry for same duplicate header here too
""",
    )
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert any("Duplicate header 'duplicate name'" in e for e in errors)


def test_multiple_autofix_issues_resolved(tmp_path: Path, decisions_dir: Path) -> None:
    """Multiple autofix issues resolved in single pass."""
    (decisions_dir / "file-one.md").write_text(
        "# File One\n\n## First Header\nContent.\n\n## Second Header\nMore.\n"
    )
    (decisions_dir / "file-two.md").write_text(
        "# File Two\n\n## Third Header\nContent.\n"
    )
    index = _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/file-one.md

Second Header — Entry in wrong section and wrong order fix this now
Third Header — Entry in wrong section entirely different place today
First Header — Entry in wrong order here too needs reordering now

## agents/decisions/file-two.md
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content
    file2_idx = content.index("## agents/decisions/file-two.md")
    assert content.index("Third Header") > file2_idx


def test_missing_index_file_returns_no_errors(tmp_path: Path) -> None:
    """Graceful degradation when index file missing."""
    assert validate("agents/memory-index.md", tmp_path) == []


def test_missing_decision_files_returns_no_errors(tmp_path: Path) -> None:
    """Graceful degradation when decision files missing."""
    _write_index(tmp_path, "# Memory Index\n\n## agents/decisions/nonexistent.md\n")
    assert validate("agents/memory-index.md", tmp_path) == []


def test_document_intro_exemption(tmp_path: Path, decisions_dir: Path) -> None:
    """Document intro content exempt from validation."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test File\n\nIntro content before first real header\n\n"
        "## Real Header\nActual content.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Real Header — Semantic header after intro content here
""",
    )
    assert validate("agents/memory-index.md", tmp_path) == []


def test_empty_index_file_no_errors(tmp_path: Path) -> None:
    """Empty index file returns no errors."""
    _write_index(tmp_path, "")
    assert validate("agents/memory-index.md", tmp_path) == []


def test_validator_parses_when_format(tmp_path: Path) -> None:
    """Validator parses /when and /how format entries correctly."""
    index_with_when_format = """# Memory Index

## Testing Decisions

/when writing mock tests | mock patch
/how to structure fixtures | test fixtures
/when mocking subprocess | error injection

## Implementation Notes

/when choosing between approaches | design trade-offs
"""
    _write_index(tmp_path, index_with_when_format)

    entries = extract_index_entries("agents/memory-index.md", tmp_path)

    # Entry keyed by trigger text (lowercase)
    assert "writing mock tests" in entries
    assert entries["writing mock tests"][2] == "Testing Decisions"

    # /how entries also parsed
    assert "to structure fixtures" in entries
    assert entries["to structure fixtures"][2] == "Testing Decisions"

    # All /when and /how lines captured
    assert "mocking subprocess" in entries
    assert "choosing between approaches" in entries

    # Old em-dash format not parsed (should be empty for that line)
    entry_count = len(entries)
    assert entry_count == 4  # Exactly 4 /when or /how entries
