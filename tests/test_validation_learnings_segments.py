"""Tests for learnings parse_segments and orphan detection."""

from pathlib import Path

from edify.validation.learnings import parse_segments, validate


def test_parse_segments_basic() -> None:
    """Test basic parsing with preamble and 2 headings."""
    content = """Preamble line 1
Preamble line 2

## First Heading
Body line 1 for first
Body line 2 for first

## Second Heading
Body line 1 for second
Body line 2 for second
"""
    result = parse_segments(content)

    assert "" in result
    assert result[""] == ["Preamble line 1", "Preamble line 2", ""]
    assert "First Heading" in result
    assert result["First Heading"] == [
        "Body line 1 for first",
        "Body line 2 for first",
        "",
    ]
    assert "Second Heading" in result
    assert result["Second Heading"] == [
        "Body line 1 for second",
        "Body line 2 for second",
    ]
    assert list(result.keys()) == ["", "First Heading", "Second Heading"]


def test_parse_segments_no_preamble() -> None:
    """Test parsing when content starts directly with a heading."""
    content = """## First Heading
Body line 1
Body line 2

## Second Heading
Body line 3
"""
    result = parse_segments(content)

    assert "" not in result or result[""] == []
    assert "First Heading" in result
    assert result["First Heading"] == ["Body line 1", "Body line 2", ""]
    assert "Second Heading" in result
    assert result["Second Heading"] == ["Body line 3"]


def test_parse_segments_empty_body() -> None:
    """Test heading with no body lines before next heading."""
    content = """Preamble

## First Heading
## Second Heading
Body content
"""
    result = parse_segments(content)

    assert "" in result
    assert "First Heading" in result
    assert result["First Heading"] == []
    assert "Second Heading" in result
    assert result["Second Heading"] == ["Body content"]


def test_parse_segments_preserves_order() -> None:
    """Test that dict preserves insertion order."""
    content = """Preamble

## Alpha
Alpha body

## Bravo
Bravo body

## Charlie
Charlie body
"""
    result = parse_segments(content)
    keys = list(result.keys())

    assert keys == ["", "Alpha", "Bravo", "Charlie"]


def test_parse_segments_blank_lines_in_body() -> None:
    """Test that blank lines in body are preserved."""
    content = """## Heading
Line 1

Line 3 (after blank)

Line 5 (after another blank)
"""
    result = parse_segments(content)

    assert "Heading" in result
    assert result["Heading"] == [
        "Line 1",
        "",
        "Line 3 (after blank)",
        "",
        "Line 5 (after another blank)",
    ]


def test_orphaned_content_after_preamble_detected(tmp_path: Path) -> None:
    """Orphaned bullets after preamble but before first heading are detected."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text(
        "# Learnings\n"
        "\n"
        "Preamble line 2\n"
        "Preamble line 3\n"
        "Preamble line 4\n"
        "Preamble line 5\n"
        "Preamble line 6\n"
        "Preamble line 7\n"
        "Preamble line 8\n"
        "---\n"
        "- orphaned bullet without heading\n"
        "- another orphaned line\n"
        "## Valid Heading\n"
        "- properly placed bullet\n"
    )
    errors = validate(Path("learnings.md"), tmp_path)
    assert any("orphan" in e.lower() for e in errors), (
        f"Expected orphan error, got: {errors}"
    )


def test_clean_learnings_file_no_orphan_errors(tmp_path: Path) -> None:
    """Clean learnings file with proper structure produces no orphan errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text(
        "# Learnings\n"
        "\n"
        "Institutional knowledge accumulated across sessions.\n"
        "\n"
        "**Soft limit: 80 lines.**\n"
        "\n"
        "---\n"
        "## When analyzing X\n"
        "- bullet A1\n"
        "- bullet A2\n"
        "\n"
        "## When selecting Y\n"
        "- bullet B1\n"
    )
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == [], f"Expected no errors for clean file, got: {errors}"
