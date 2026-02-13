"""Tests for resolver module."""

from claudeutils.when.resolver import resolve


def test_mode_detection() -> None:
    """Mode detection routes query to correct resolution mode."""
    # Query without prefix: trigger mode
    trigger = resolve("trigger", "writing mock tests", "", "")
    assert trigger == "trigger"

    # Single dot prefix: section mode
    section = resolve("section", ".Mock Patching", "", "")
    assert section == "section"

    # Double dot prefix: file mode
    file_mode = resolve("file", "..testing.md", "", "")
    assert file_mode == "file"

    # Single dot only (edge case): section mode
    section_only = resolve("section", ".", "", "")
    assert section_only == "section"

    # Double dot only (edge case): file mode
    file_only = resolve("file", "..", "", "")
    assert file_only == "file"
