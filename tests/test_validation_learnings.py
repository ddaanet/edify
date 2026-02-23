"""Tests for learnings validator."""

from pathlib import Path

from claudeutils.validation.learnings import parse_segments, validate


def test_valid_learnings_file_returns_no_errors(tmp_path: Path) -> None:
    """Test that valid learnings file returns no errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Institutional knowledge accumulated across sessions.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate.

---
## Learning One
Content here.

## Learning Two
More content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_title_exceeding_max_word_count_returns_error(
    tmp_path: Path,
) -> None:
    """Test that title exceeding max word count returns error."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble line 2
Preamble line 3
Preamble line 4
Preamble line 5
Preamble line 6
Preamble line 7
Preamble line 8
Preamble line 9
Preamble line 10
## This is a title with way too many words for the validator
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "title has 12 words (max 5)" in errors[0]
    assert "line 12" in errors[0]


def test_duplicate_titles_detected_case_insensitive(tmp_path: Path) -> None:
    """Test that duplicate titles are detected (case-insensitive)."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble line 2
Preamble line 3
Preamble line 4
Preamble line 5
Preamble line 6
Preamble line 7
Preamble line 8
Preamble line 9
Preamble line 10
## First Learning Title
Content here.

## First learning title
Different content but same title.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "duplicate title" in errors[0]
    assert "line 15" in errors[0]
    assert "first at line 12" in errors[0]


def test_preamble_first_10_lines_skipped(tmp_path: Path) -> None:
    """Test that preamble (first 10 lines) is skipped."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9
Line 10
## First Valid Title
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_empty_file_returns_no_errors(tmp_path: Path) -> None:
    """Test that empty file returns no errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_missing_file_returns_no_errors(tmp_path: Path) -> None:
    """Test that missing file returns no errors (graceful degradation)."""
    errors = validate(Path("nonexistent.md"), tmp_path)
    assert errors == []


def test_multiple_errors_reported(tmp_path: Path) -> None:
    """Test that multiple errors are all reported."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble line 2
Preamble line 3
Preamble line 4
Preamble line 5
Preamble line 6
Preamble line 7
Preamble line 8
Preamble line 9
Preamble line 10
## First Title Word Count Too Long Here Now
Content here.

## Second Title Word Count Too Long Here Now
Different content.

## Duplicate Title
Another content.

## duplicate title
Final content.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 3
    assert any("title has 8 words" in e for e in errors)
    assert any("title has 8 words" in e for e in errors)
    assert any("duplicate title" in e for e in errors)


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
