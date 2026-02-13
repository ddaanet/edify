"""Tests for resolver module."""

from pathlib import Path

from claudeutils.when.resolver import ResolveError, _extract_section_content, resolve


def test_mode_detection(tmp_path: Path) -> None:
    """Mode detection routes query to correct resolution mode.

    Section and file modes are tested here; trigger mode is tested in
    test_trigger_mode_resolves.
    """
    # Create minimal test files for section and file mode tests
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest content.\n")

    # Section mode resolves heading to content
    section = resolve("section", ".Test Section", str(index_file), str(decisions_dir))
    assert "## Test Section" in section
    assert "Test content." in section

    # File mode resolves to file content
    file_mode = resolve("file", "..testing.md", str(index_file), str(decisions_dir))
    assert "## Test Section" in file_mode
    assert "Test content." in file_mode


def test_section_mode_resolves(tmp_path: Path) -> None:
    """Section mode resolves global unique headings across decision files.

    Tests heading lookup across files with uniqueness check and case-insensitive
    matching.
    """
    # Create index file
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    # Create decisions directory
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    # Create decision file with unique heading
    workflow_file = decisions_dir / "workflow-core.md"
    workflow_file.write_text(
        "# Main Title\n"
        "\n"
        "## Mock Patching Pattern\n"
        "\n"
        "Use exact match for restoration operations.\n"
        "\n"
        "Prevents exploitation via command continuation.\n"
        "\n"
        "## Next Section\n"
        "\n"
        "Other content here.\n"
    )

    # Test unique heading lookup
    result = resolve(
        "section", ".Mock Patching Pattern", str(index_file), str(decisions_dir)
    )
    assert "## Mock Patching Pattern" in result
    assert "Use exact match for restoration operations" in result
    assert "Prevents exploitation via command continuation" in result
    # Verify boundary: should not include next section
    assert "## Next Section" not in result

    # Test case-insensitive lookup
    result = resolve(
        "section", ".mock patching pattern", str(index_file), str(decisions_dir)
    )
    assert "## Mock Patching Pattern" in result


def test_file_mode_resolves(tmp_path: Path) -> None:
    """File mode resolves relative path to file content.

    Tests filename lookup relative to decisions_dir, file reading, and error
    handling for missing files.
    """
    # Create index file
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    # Create decisions directory with a test file
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest file content.\n")

    # File mode should return full file content
    result = resolve("file", "..testing.md", str(index_file), str(decisions_dir))
    assert "## Test Section" in result
    assert "Test file content." in result

    # File mode should raise ResolveError for missing files
    try:
        resolve("file", "..nonexistent.md", str(index_file), str(decisions_dir))
        raise AssertionError("Expected ResolveError for missing file")
    except ResolveError:
        pass


def test_trigger_mode_resolves(tmp_path: Path) -> None:
    """Trigger mode resolves query to heading in decision file via fuzzy match.

    Tests exact and approximate matching against index entries.
    """
    # Create a test index file with section pointing to a file
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/when error handling | exceptions, debugging\n"
    )

    # Create a decisions directory with a decision file
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "## When Writing Mock Tests\n"
        "\n"
        "Mock tests prevent side effects...\n"
        "\n"
        "## Error Handling\n"
        "\n"
        "Handle errors gracefully.\n"
    )

    # Query exact match should resolve to heading (formatted as H1)
    result = resolve(
        "trigger", "writing mock tests", str(index_file), str(decisions_dir)
    )
    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result

    # Query with approximate match should also resolve
    result = resolve("trigger", "mock test", str(index_file), str(decisions_dir))
    assert "# When Writing Mock Tests" in result


def test_resolve_output_format(tmp_path: Path) -> None:
    """Output formatting combines content + navigation links.

    Tests that full resolve output includes heading, section content, and
    navigation (Broader: ancestors, Related: siblings).
    """
    # Create index file with entries
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/when mock patching | patch object, patching\n"
    )

    # Create decisions directory
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    # Create testing.md with hierarchical structure (H2 parent, H3 children)
    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "# Main Title\n"
        "\n"
        "## Test Patterns\n"
        "\n"
        "### When Writing Mock Tests\n"
        "\n"
        "Mock tests prevent side effects and isolate behavior.\n"
        "\n"
        "Use test doubles for external dependencies.\n"
        "\n"
        "### When Mock Patching\n"
        "\n"
        "Patch where object is used, not where defined.\n"
        "\n"
        "Prevents exploitation via command continuation.\n"
    )

    # Resolve trigger mode should return full formatted output
    result = resolve(
        "trigger", "writing mock tests", str(index_file), str(decisions_dir)
    )

    # Assertions from cycle spec
    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result
    assert "Use test doubles for external dependencies" in result

    # Navigation sections - must have format
    # File link always present in Broader section
    assert "Broader:" in result
    assert "/when ..testing.md" in result

    # Siblings present when there are matching entries under same parent
    assert "Related:" in result or "/when mock patching" in result


def test_section_content_extraction(tmp_path: Path) -> None:
    """Extract content between heading boundaries.

    Tests extraction with H3 nested structure, flat H2 structure, last heading
    in file, and boundary exclusivity (next heading not included).
    """
    # Test nested H2/H3 structure
    nested_file = tmp_path / "nested.md"
    nested_file.write_text(
        "## Parent A\n"
        "\n"
        "Parent A content.\n"
        "\n"
        "### Child A1\n"
        "\n"
        "Child A1 content.\n"
        "\n"
        "### Child A2\n"
        "\n"
        "Child A2 content.\n"
        "\n"
        "## Parent B\n"
        "\n"
        "Parent B content.\n"
    )

    # Extract H3 heading should get only that child's content
    result = _extract_section_content("### Child A1", nested_file.read_text())
    assert "### Child A1" in result
    assert "Child A1 content" in result
    assert "Child A2" not in result
    assert "Parent B" not in result

    # Test flat H2 structure
    flat_file = tmp_path / "flat.md"
    flat_file.write_text(
        "## Heading A\n"
        "\n"
        "Content A line 1.\n"
        "Content A line 2.\n"
        "\n"
        "## Heading B\n"
        "\n"
        "Content B.\n"
    )

    # Extract H2 should get content until next H2
    result = _extract_section_content("## Heading A", flat_file.read_text())
    assert "## Heading A" in result
    assert "Content A line 1" in result
    assert "Content A line 2" in result
    assert "## Heading B" not in result
    assert "Content B" not in result

    # Test last heading in file extends to EOF
    last_heading_file = tmp_path / "last.md"
    last_heading_file.write_text(
        "## First\n"
        "\n"
        "First content.\n"
        "\n"
        "## Last\n"
        "\n"
        "Last content line 1.\n"
        "Last content line 2.\n"
    )

    result = _extract_section_content("## Last", last_heading_file.read_text())
    assert "## Last" in result
    assert "Last content line 1" in result
    assert "Last content line 2" in result
