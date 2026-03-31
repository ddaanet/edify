"""Tests for resolver mode detection and basic resolution."""

from pathlib import Path

import pytest

from edify.when.resolver import ResolveError, resolve


def test_mode_detection(tmp_path: Path) -> None:
    """Mode detection routes query to correct resolution mode."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest content.\n")

    section = resolve(".Test Section", str(index_file), str(decisions_dir))
    assert "## Test Section" in section
    assert "Test content." in section

    file_mode = resolve("..testing.md", str(index_file), str(decisions_dir))
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

    result = resolve(".Mock Patching Pattern", str(index_file), str(decisions_dir))
    assert "## Mock Patching Pattern" in result
    assert "Use exact match for restoration operations" in result
    assert "Prevents exploitation via command continuation" in result
    assert "## Next Section" not in result

    result = resolve(".mock patching pattern", str(index_file), str(decisions_dir))
    assert "## Mock Patching Pattern" in result


def test_file_mode_resolves(tmp_path: Path) -> None:
    """File mode resolves filename to file content."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest file content.\n")

    result = resolve("..testing.md", str(index_file), str(decisions_dir))
    assert "## Test Section" in result
    assert "Test file content." in result

    with pytest.raises(ResolveError):
        resolve("..nonexistent.md", str(index_file), str(decisions_dir))


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

    result = resolve("writing mock tests", str(index_file), str(decisions_dir))
    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result

    result = resolve("mock test", str(index_file), str(decisions_dir))
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
        "configure script entry points",
        str(index_file),
        str(decisions_dir),
    )
    assert "Add project.scripts to pyproject.toml" in result


def test_resolve_output_format(tmp_path: Path) -> None:
    """Output formatting combines content with source reference."""
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

    result = resolve("writing mock tests", str(index_file), str(decisions_dir))

    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result
    assert "Use test doubles for external dependencies" in result
    assert "Source: agents/decisions/testing.md" in result
    assert "Broader:" not in result
    assert "Related:" not in result


def test_how_to_prefix_not_doubled(tmp_path: Path) -> None:
    """Calling with 'how to X' doesn't double the 'to' prefix."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## implementation\n"
        "\n"
        "/how prevent skill steps from being skipped | prose gates D+B\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "implementation.md"
    decision_file.write_text(
        "# Implementation Notes\n"
        "\n"
        "## How to Prevent Skill Steps From Being Skipped\n"
        "\n"
        "Use D+B hybrid anchoring.\n"
        "\n"
        "## Other Section\n"
        "\n"
        "Other content.\n"
    )

    # Simulates cli.py passing "to X" after stripping "how" from "how to X".
    # resolver.py strips leading "to " so fuzzy match hits the bare trigger.
    result = resolve(
        "to prevent skill steps from being skipped",
        str(index_file),
        str(decisions_dir),
    )
    assert "D+B hybrid anchoring" in result


def test_cross_operator_matching(tmp_path: Path) -> None:
    """Entry under /how resolves when called with 'when' operator."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## implementation\n"
        "\n"
        "/how prevent skill steps from being skipped | prose gates D+B\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "implementation.md"
    decision_file.write_text(
        "# Implementation Notes\n"
        "\n"
        "## How to Prevent Skill Steps From Being Skipped\n"
        "\n"
        "Use D+B hybrid anchoring.\n"
        "\n"
        "## Other Section\n"
        "\n"
        "Other content.\n"
    )

    # Caller uses "when" prefix but entry is /how — should still match
    result = resolve(
        "prevent skill steps from being skipped",
        str(index_file),
        str(decisions_dir),
    )
    assert "D+B hybrid anchoring" in result


def test_bare_trigger_no_operator(tmp_path: Path) -> None:
    """Bare trigger query (no operator) resolves to matching entry."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/how configure script entry points | pyproject scripts\n"
    )

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "# Testing\n"
        "\n"
        "## When Writing Mock Tests\n"
        "\n"
        "Mock tests prevent side effects.\n"
        "\n"
        "## How to Configure Script Entry Points\n"
        "\n"
        "Add project.scripts to pyproject.toml.\n"
    )

    # No operator — bare trigger resolves /when entry
    result = resolve(
        "writing mock tests",
        str(index_file),
        str(decisions_dir),
    )
    assert "Mock tests prevent side effects" in result

    # No operator — bare trigger resolves /how entry
    result = resolve(
        "configure script entry points",
        str(index_file),
        str(decisions_dir),
    )
    assert "Add project.scripts to pyproject.toml" in result
