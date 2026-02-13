"""Tests for resolver module."""

from pathlib import Path

from claudeutils.when.resolver import resolve


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

    # File mode detection (returns "file" mode identifier for now)
    # Note: Full file mode implementation is in a later cycle
    file_mode = resolve("file", "..testing.md", str(index_file), str(decisions_dir))
    assert file_mode == "file"


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

    # Query exact match should resolve to heading
    result = resolve(
        "trigger", "writing mock tests", str(index_file), str(decisions_dir)
    )
    assert "## When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result

    # Query with approximate match should also resolve
    result = resolve("trigger", "mock test", str(index_file), str(decisions_dir))
    assert "## When Writing Mock Tests" in result
