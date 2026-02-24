"""Tests for resolver mode detection and basic resolution."""

from pathlib import Path

import pytest

from claudeutils.when.resolver import ResolveError, resolve


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

    result = resolve(
        "when", ".Mock Patching Pattern", str(index_file), str(decisions_dir)
    )
    assert "## Mock Patching Pattern" in result
    assert "Use exact match for restoration operations" in result
    assert "Prevents exploitation via command continuation" in result
    assert "## Next Section" not in result

    result = resolve(
        "when", ".mock patching pattern", str(index_file), str(decisions_dir)
    )
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


def test_trigger_fuzzy_heading_match(tmp_path: Path) -> None:
    """Fuzzy fallback resolves heading with missing articles."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## workflow-planning\n"
        "\n"
        "/when adding a new variant to enumerated system | grep downstream\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "workflow-planning.md"
    decision_file.write_text(
        "# Workflow Planning\n"
        "\n"
        "## Some Other Section\n"
        "\n"
        "Other content.\n"
        "\n"
        "### When Adding A New Variant To An Enumerated System\n"
        "\n"
        "Grep downstream enumeration sites.\n"
        "\n"
        "Check all switch/match statements.\n"
        "\n"
        "### Another Section\n"
        "\n"
        "More content.\n"
    )

    # _build_heading produces "When Adding A New Variant To Enumerated System"
    # Actual heading has "An" that trigger omits
    # Fuzzy fallback should find the correct heading
    result = resolve(
        "when",
        "adding a new variant to enumerated system",
        str(index_file),
        str(decisions_dir),
    )
    assert "Grep downstream enumeration sites" in result
    assert "Check all switch/match statements" in result


def test_trigger_fuzzy_heading_match_how_operator(tmp_path: Path) -> None:
    """Fuzzy fallback works for /how operator with abbreviated trigger."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## procedures\n\n/how configure script entry points | pyproject scripts\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "procedures.md"
    decision_file.write_text(
        "# Procedures\n"
        "\n"
        "## How to Configure the Script Entry Points\n"
        "\n"
        "Add project.scripts to pyproject.toml.\n"
        "\n"
        "## Other Section\n"
        "\n"
        "Other content.\n"
    )

    result = resolve(
        "how",
        "configure script entry points",
        str(index_file),
        str(decisions_dir),
    )
    assert "Add project.scripts to pyproject.toml" in result


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
