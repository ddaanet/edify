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

/when decision one
/when decision two
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

/when nonexistent header
/when existing header
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

/when test header
/when test header
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "duplicate index entry" in errors[0]


def test_long_entry_no_error_new_format(tmp_path: Path, decisions_dir: Path) -> None:
    """Long entries allowed in new /when format.

    Word count removed per D-9.
    """
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Short\nContent.\n\n"
        "## Long Entry With Many Words\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when short
/when long entry with many words
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_entry_without_operator_prefix_error(
    tmp_path: Path, decisions_dir: Path
) -> None:
    """Entry without /when or /how prefix returns error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Test Unique Header\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

Test Unique Header just some words without operator prefix
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)
    assert any("no operator prefix" in e for e in errors)


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

/when second header
/when first header
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

/when third header
/when first header
/when second header
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    first_pos = content.index("/when first header")
    second_pos = content.index("/when second header")
    third_pos = content.index("/when third header")
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

/when organizational section
/when real header
/when another real header
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    assert "organizational section" not in content
    assert "real header" in content


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

/when test header
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

/when second header
/when first header
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

/when duplicate name

## agents/decisions/file-two.md

/when duplicate name
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

/when second header
/when third header
/when first header

## agents/decisions/file-two.md
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content
    file2_idx = content.index("## agents/decisions/file-two.md")
    assert content.index("third header") > file2_idx


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

/when real header
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


def test_format_validation_rules(tmp_path: Path, decisions_dir: Path) -> None:
    """Format validation checks operator prefix, trigger, extras.

    Validates operator prefix, trigger non-empty, and extras format.
    """
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Valid Trigger\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when valid trigger
/when valid | extra1, extra2
/what invalid operator
/when
/when trigger | ,,,
Old em-dash format — no operator prefix
Valid Trigger — Valid entry with em-dash
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)

    # Should flag invalid operator
    assert any("/what" in e and "invalid operator" in e for e in errors)

    # Should flag empty trigger
    assert any("/when" in e and "empty trigger" in e for e in errors)

    # Valid entries should NOT be flagged
    assert not any("valid trigger" in e and "error" in e for e in errors)
    assert not any("extra1, extra2" in e and "error" in e for e in errors)

    # Should flag old em-dash format (no operator prefix)
    assert any("no operator prefix" in e for e in errors)

    # Each error should include line number and message
    assert all(
        "memory-index.md:" in e
        for e in errors
        if "error" in e.lower() or "invalid" in e.lower() or "empty" in e.lower()
    )
