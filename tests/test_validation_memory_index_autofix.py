"""Tests for memory index validator autofix functionality."""

from pathlib import Path

from claudeutils.validation.memory_index import validate


def test_exempt_sections_removed_after_migration(tmp_path: Path) -> None:
    """Test that exempt sections are removed after migration."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Test Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

/when test header
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify exempt sections are not present after migration
    content = index_file.read_text()
    assert "Behavioral Rules" not in content
    assert "Technical Decisions" not in content
    assert "/when test header" in content


def test_autofix_false_reports_all_issues(tmp_path: Path) -> None:
    """Test that autofix=False reports all issues as errors."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## First Header
Content here.

## Second Header
More content.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

/when second header
/when first header
""")

    # With autofix=False, should report errors
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert len(errors) > 0
    assert any("entries not in file order" in e for e in errors)


def test_duplicate_headers_across_files_error(tmp_path: Path) -> None:
    """Test that duplicate headers across files return error."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## Duplicate Name
Content here.
""")

    file2 = decisions_dir / "file-two.md"
    file2.write_text("""# File Two

## Duplicate Name
Different content.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

/when duplicate name

## agents/decisions/file-two.md

/when duplicate name
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert len(errors) > 0
    assert any("Duplicate header 'duplicate name'" in e for e in errors)


def test_multiple_autofix_issues_resolved_in_single_pass(tmp_path: Path) -> None:
    """Test that multiple autofix issues resolved in single pass."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## First Header
Content here.

## Second Header
More content.
""")

    file2 = decisions_dir / "file-two.md"
    file2.write_text("""# File Two

## Third Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

/when second header
/when third header
/when first header

## agents/decisions/file-two.md
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify both issues were fixed
    content = index_file.read_text()
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content

    # Verify Third Header moved to correct section
    lines = content.splitlines()
    next(i for i, line in enumerate(lines) if "agents/decisions/file-one.md" in line)
    file2_section_idx = next(
        i for i, line in enumerate(lines) if "agents/decisions/file-two.md" in line
    )
    # Third Header should be between file1 section header and file2 section header
    for i in range(file2_section_idx, len(lines)):
        if "Third Header" in lines[i]:
            assert i > file2_section_idx


def test_missing_index_file_returns_no_errors(tmp_path: Path) -> None:
    """Test graceful degradation when index file missing."""
    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_missing_decision_files_returns_no_errors(tmp_path: Path) -> None:
    """Test graceful degradation when decision files missing."""
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.parent.mkdir(parents=True)
    index_file.write_text("""# Memory Index

## agents/decisions/nonexistent.md
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_document_intro_exemption(tmp_path: Path) -> None:
    """Test that document intro content is exempt from validation."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test File

Intro content with ## that looks like header syntax
But this content should be skipped before first real header

## Real Header
Actual content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

/when real header
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_empty_index_file_no_errors(tmp_path: Path) -> None:
    """Test empty index file (graceful degradation)."""
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.parent.mkdir(parents=True)
    index_file.write_text("")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_autofix_new_format(tmp_path: Path) -> None:
    """Test that autofix handles /when format entries correctly.

    Verifies:
    - Entry in wrong file section → autofix moves to correct section
    - Entries out of file order within section → autofix reorders
    - Entry pointing to structural heading (. prefix) → autofix removes
    - After autofix: re-running validation produces zero errors
    """
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## Mock Test
Content here.

## Real Header
More content.
""")

    file2 = decisions_dir / "file-two.md"
    file2.write_text("""# File Two

## .Structural Section
This is structural.
""")

    # Index with issues:
    # 1. /when mock test in file-two section (wrong section)
    # 2. Entries out of order
    # 3. /when structural section pointing to dot-prefixed header
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-two.md

/when mock test
/when structural section

## agents/decisions/file-one.md

/when real header
""")

    # Run autofix
    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify the index was fixed:
    content = index_file.read_text()

    # Verify correct sections exist
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content

    # Verify /when format is preserved
    assert "/when mock test" in content
    assert "/when real header" in content

    # Verify structural entry was removed
    assert "/when structural section" not in content

    # Verify mock test is in file-one section (correct location)
    lines = content.splitlines()
    file1_idx = next(
        i for i, line in enumerate(lines) if "agents/decisions/file-one.md" in line
    )
    file2_idx = next(
        i for i, line in enumerate(lines) if "agents/decisions/file-two.md" in line
    )

    mock_test_idx = next(i for i, line in enumerate(lines) if "/when mock test" in line)
    assert file1_idx < mock_test_idx < file2_idx

    # Verify ordering (mock test at line 3, real header at line 6)
    real_header_idx = next(
        i for i, line in enumerate(lines) if "/when real header" in line
    )
    assert mock_test_idx < real_header_idx

    # Re-running validation should produce no errors
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert errors == []
