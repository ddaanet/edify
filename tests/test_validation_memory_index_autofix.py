"""Tests for memory index validator autofix functionality."""

from pathlib import Path

from claudeutils.validation.memory_index import validate


def test_exempt_sections_preserved_as_is(tmp_path: Path) -> None:
    """Test that exempt sections are preserved as-is."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Test Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## Behavioral Rules (fragments — already loaded)

Some custom rule — description that shows em-dash format here
Another rule — another entry with proper em-dash separator today

## Technical Decisions (mixed — check entry for specific file)

Technical note — entry with em-dash in technical section here
Another item — another entry with proper format today now

## agents/decisions/test-decision.md

/when test header
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify exempt sections preserved
    content = index_file.read_text()
    assert "Some custom rule — description that shows em-dash format here" in content
    assert "Another rule — another entry with proper em-dash separator today" in content
    assert "Technical note — entry with em-dash in technical section here" in content


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
