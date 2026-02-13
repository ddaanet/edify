"""Tests for resolver module."""

from pathlib import Path

import pytest

from claudeutils.when.resolver import ResolveError, _extract_section_content, resolve


def test_mode_detection(tmp_path: Path) -> None:
    """Mode detection routes query to correct resolution mode."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest content.\n")

    section = resolve("when", ".Test Section", str(index_file), str(decisions_dir))
    assert "## Test Section" in section
    assert "Test content." in section

    file_mode = resolve("when", "..testing.md", str(index_file), str(decisions_dir))
    assert "## Test Section" in file_mode
    assert "Test content." in file_mode


def test_section_mode_resolves(tmp_path: Path) -> None:
    """Section mode resolves headings case-insensitively."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

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

    result = resolve("when", ".Mock Patching Pattern", str(index_file), str(decisions_dir))
    assert "## Mock Patching Pattern" in result
    assert "Use exact match for restoration operations" in result
    assert "Prevents exploitation via command continuation" in result
    assert "## Next Section" not in result

    result = resolve("when", ".mock patching pattern", str(index_file), str(decisions_dir))
    assert "## Mock Patching Pattern" in result


def test_file_mode_resolves(tmp_path: Path) -> None:
    """File mode resolves filename to file content."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest file content.\n")

    result = resolve("when", "..testing.md", str(index_file), str(decisions_dir))
    assert "## Test Section" in result
    assert "Test file content." in result

    with pytest.raises(ResolveError):
        resolve("when", "..nonexistent.md", str(index_file), str(decisions_dir))


def test_trigger_mode_resolves(tmp_path: Path) -> None:
    """Trigger mode resolves query via fuzzy matching."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/when error handling | exceptions, debugging\n"
    )

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

    result = resolve("when", "writing mock tests", str(index_file), str(decisions_dir))
    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result

    result = resolve("when", "mock test", str(index_file), str(decisions_dir))
    assert "# When Writing Mock Tests" in result


def test_resolve_output_format(tmp_path: Path) -> None:
    """Output formatting combines content and navigation links."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/when mock patching | patch object, patching\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

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

    result = resolve("when", "writing mock tests", str(index_file), str(decisions_dir))

    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result
    assert "Use test doubles for external dependencies" in result
    assert "Broader:" in result
    assert "/when ..testing.md" in result
    assert "Related:" in result or "/when mock patching" in result


def test_trigger_not_found_suggests_matches(tmp_path: Path) -> None:
    """No match error includes up to 3 fuzzy suggestions."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/when error handling | exceptions, debugging\n"
        "/when mock patching | patch object, patching\n"
        "/when debugging tests | print, inspect\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "## When Writing Mock Tests\n"
        "\n"
        "Mock tests prevent side effects.\n"
        "\n"
        "## Error Handling\n"
        "\n"
        "Handle errors gracefully.\n"
        "\n"
        "## When Mock Patching\n"
        "\n"
        "Patch where object is used.\n"
        "\n"
        "## When Debugging Tests\n"
        "\n"
        "Debugging strategies.\n"
    )

    with pytest.raises(ResolveError) as exc_info:
        resolve("when", "nonexistent topic xyz", str(index_file), str(decisions_dir))

    error_msg = str(exc_info.value)
    assert "No match for" in error_msg
    assert "nonexistent topic xyz" in error_msg
    assert "Did you mean:" in error_msg
    assert "/when " in error_msg
    suggestion_count = error_msg.count("/when ")
    assert suggestion_count >= 1
    assert suggestion_count <= 3


def test_trigger_suggestions_limited_to_three(tmp_path: Path) -> None:
    """Verify exactly 3 suggestions when 10+ candidates exist."""
    index_file = tmp_path / "test_index.md"
    index_entries = [
        "/when topic one | first\n",
        "/when topic two | second\n",
        "/when topic three | third\n",
        "/when topic four | fourth\n",
        "/when topic five | fifth\n",
        "/when topic six | sixth\n",
        "/when topic seven | seventh\n",
        "/when topic eight | eighth\n",
        "/when topic nine | ninth\n",
        "/when topic ten | tenth\n",
        "/when topic eleven | eleventh\n",
        "/when topic twelve | twelfth\n",
    ]
    index_file.write_text("## testing\n\n" + "".join(index_entries))

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "## When Topic One\n\nContent.\n\n"
        "## When Topic Two\n\nContent.\n\n"
        "## When Topic Three\n\nContent.\n\n"
        "## When Topic Four\n\nContent.\n\n"
        "## When Topic Five\n\nContent.\n\n"
        "## When Topic Six\n\nContent.\n\n"
        "## When Topic Seven\n\nContent.\n\n"
        "## When Topic Eight\n\nContent.\n\n"
        "## When Topic Nine\n\nContent.\n\n"
        "## When Topic Ten\n\nContent.\n\n"
        "## When Topic Eleven\n\nContent.\n\n"
        "## When Topic Twelve\n\nContent.\n\n"
    )

    with pytest.raises(ResolveError) as exc_info:
        resolve("when", "nonmatching query xyz", str(index_file), str(decisions_dir))

    error_msg = str(exc_info.value)
    suggestion_count = error_msg.count("/when ")
    assert suggestion_count == 3


def test_section_not_found_lists_headings(tmp_path: Path) -> None:
    """Section error lists available headings (up to 10)."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    file1 = decisions_dir / "workflow.md"
    file1.write_text(
        "## When Writing Tests\n\nTest content.\n\n"
        "## When Mocking Objects\n\nMock content.\n\n"
        "## When Debugging\n\nDebug content.\n"
    )

    file2 = decisions_dir / "patterns.md"
    file2.write_text(
        "## When Refactoring\n\nRefactor content.\n\n"
        "## When Optimizing\n\nOptimize content.\n"
    )

    with pytest.raises(ResolveError) as exc_info:
        resolve("when", ".Nonexistent Section", str(index_file), str(decisions_dir))

    error_msg = str(exc_info.value)
    assert "Section 'Nonexistent Section' not found." in error_msg
    assert "Available:" in error_msg
    assert ".When Writing Tests" in error_msg
    assert ".When Mocking Objects" in error_msg
    assert ".When Debugging" in error_msg
    assert ".When Refactoring" in error_msg
    assert ".When Optimizing" in error_msg


def test_section_content_extraction(tmp_path: Path) -> None:
    """Extract content between heading boundaries."""
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

    result = _extract_section_content("### Child A1", nested_file.read_text())
    assert "### Child A1" in result
    assert "Child A1 content" in result
    assert "Child A2" not in result
    assert "Parent B" not in result

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

    result = _extract_section_content("## Heading A", flat_file.read_text())
    assert "## Heading A" in result
    assert "Content A line 1" in result
    assert "Content A line 2" in result
    assert "## Heading B" not in result
    assert "Content B" not in result

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


def test_file_not_found_lists_files(tmp_path: Path) -> None:
    """File error lists available files sorted alphabetically."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    (decisions_dir / "cli.md").write_text("## CLI Section\n\nCLI content.\n")
    (decisions_dir / "testing.md").write_text(
        "## Testing Section\n\nTesting content.\n"
    )
    (decisions_dir / "architecture.md").write_text(
        "## Architecture Section\n\nArchitecture content.\n"
    )

    with pytest.raises(ResolveError) as exc_info:
        resolve("when", "..nonexistent.md", str(index_file), str(decisions_dir))

    error_msg = str(exc_info.value)
    assert "File 'nonexistent.md' not found in decision files." in error_msg
    assert "Available:" in error_msg
    assert "..architecture.md" in error_msg
    assert "..cli.md" in error_msg
    assert "..testing.md" in error_msg
    arch_idx = error_msg.index("..architecture.md")
    cli_idx = error_msg.index("..cli.md")
    test_idx = error_msg.index("..testing.md")
    assert arch_idx < cli_idx < test_idx


def test_operator_parameter_disambiguates(tmp_path: Path) -> None:
    """Operator parameter distinguishes /when vs /how entries with same trigger.

    When two entries have same trigger but different operators, the operator
    parameter selects the correct one.
    """
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n\n"
        "/when mock testing | behavioral\n"
        "/how mock testing | procedural\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text(
        "# Testing\n\n"
        "## When Mock Testing\n\n"
        "Behavioral guidance here.\n\n"
        "## How to Mock Testing\n\n"
        "Procedural steps here.\n"
    )

    # /when should resolve to "When Mock Testing"
    when_result = resolve("when", "mock testing", str(index_file), str(decisions_dir))
    assert "When Mock Testing" in when_result
    assert "Behavioral guidance" in when_result
    assert "Procedural steps" not in when_result

    # /how should resolve to "How to Mock Testing"
    how_result = resolve("how", "mock testing", str(index_file), str(decisions_dir))
    assert "How to Mock Testing" in how_result
    assert "Procedural steps" in how_result
    assert "Behavioral guidance" not in how_result
