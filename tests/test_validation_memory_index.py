"""Tests for memory index basic validation and autofixes."""

from pathlib import Path

import pytest

from edify.validation.memory_index import validate


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
        "# Test Decision\n\n## When Decision One\nContent.\n\n"
        "## When Decision Two\nMore.\n"
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
        "# Test Decision\n\n## When Existing Header\nContent.\n"
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
    assert "orphan index entry 'when nonexistent header'" in errors[0]


def test_duplicate_index_entries_error(tmp_path: Path, decisions_dir: Path) -> None:
    """Duplicate index entries return error."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## When Test Header\nContent.\n"
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
        "# Test Decision\n\n## When Short\nContent.\n\n"
        "## When Long Entry With Many Words\nContent.\n"
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
        "# File One\n\n## When First Header\nContent.\n"
    )
    (decisions_dir / "file-two.md").write_text(
        "# File Two\n\n## When Second Header\nContent.\n"
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
        "# Test Decision\n\n## When First Header\nContent.\n\n"
        "## When Second Header\nMore.\n\n## When Third Header\nEven more.\n"
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
        "## When Real Header\nSemantic.\n\n"
        "## When Another Real Header\nMore semantic.\n"
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


def test_exempt_sections_removed_after_migration(
    tmp_path: Path, decisions_dir: Path
) -> None:
    """Exempt sections removed after migration (no longer exempt)."""
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## When Test Header\nContent.\n"
    )
    index = _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when test header
""",
    )
    assert validate("agents/memory-index.md", tmp_path, autofix=True) == []

    content = index.read_text()
    # Exempt sections should not be present after migration
    assert "Behavioral Rules" not in content
    assert "Technical Decisions" not in content
    assert "/when test header" in content


def test_autofix_false_reports_all_issues(tmp_path: Path, decisions_dir: Path) -> None:
    """Autofix=False reports sorting issues as errors."""
    (decisions_dir / "file-one.md").write_text(
        "# File One\n\n## When First Header\nContent.\n\n## When Second Header\nMore.\n"
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
        "# File One\n\n## When Duplicate Name\nContent.\n"
    )
    (decisions_dir / "file-two.md").write_text(
        "# File Two\n\n## When Duplicate Name\nDifferent.\n"
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
    assert any("Duplicate header 'when duplicate name'" in e for e in errors)


def test_multiple_autofix_issues_resolved(tmp_path: Path, decisions_dir: Path) -> None:
    """Multiple autofix issues resolved in single pass."""
    (decisions_dir / "file-one.md").write_text(
        "# File One\n\n## When First Header\nContent.\n\n## When Second Header\nMore.\n"
    )
    (decisions_dir / "file-two.md").write_text(
        "# File Two\n\n## When Third Header\nContent.\n"
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
        "## When Real Header\nActual content.\n"
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
