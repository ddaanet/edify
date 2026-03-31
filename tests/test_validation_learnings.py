"""Tests for learnings validator."""

from pathlib import Path

from edify.validation.learnings import validate


def test_valid_learnings_file_returns_no_errors(tmp_path: Path) -> None:
    """Test that valid learnings file returns no errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Institutional knowledge accumulated across sessions.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate.

---
## When learning one
Content here.

## When learning two
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

---
## When this title has way too many words for the validator
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "title has 11 words (max 7)" in errors[0]
    assert "line 4" in errors[0]


def test_duplicate_titles_detected_case_insensitive(tmp_path: Path) -> None:
    """Test that duplicate titles are detected (case-insensitive)."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## When first learning title
Content here.

## When first learning title
Different content but same title.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "duplicate title" in errors[0]
    assert "line 7" in errors[0]
    assert "first at line 4" in errors[0]


def test_preamble_bounded_by_first_heading(tmp_path: Path) -> None:
    """Test that preamble ends at first ## heading when no --- present."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings
Line 2
Line 3
## When valid title here
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_preamble_bounded_by_hr_beyond_10_lines(tmp_path: Path) -> None:
    """Test that --- as structural boundary works beyond 10 lines."""
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
Line 11
---
## When valid title here
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_orphaned_content_between_hr_and_heading(tmp_path: Path) -> None:
    """Test that content between --- and first ## heading is orphaned."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble text.

---
This line is orphaned.
## When valid title here
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "orphaned content" in errors[0]
    assert "line 6" in errors[0]


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


def test_title_without_prefix_returns_error(tmp_path: Path) -> None:
    """Test that title without When/How to prefix returns an error."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## Bad Title
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "prefix" in errors[0].lower()
    assert "line 4" in errors[0]


def test_insufficient_content_words_returns_error(tmp_path: Path) -> None:
    """Test title with fewer than 2 content words after prefix returns error."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## When testing
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "content word" in errors[0].lower()
    assert "line 4" in errors[0]


def test_how_to_prefix_insufficient_content_words_returns_error(
    tmp_path: Path,
) -> None:
    """Test that 'How to' prefix path also enforces min 2 content words."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## How to configure
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "content word" in errors[0].lower()
    assert "line 4" in errors[0]


def test_how_to_prefix_accepted(tmp_path: Path) -> None:
    """Test that 'How to' prefix with 2 content words returns no errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## How to encode paths
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_how_without_to_rejected(tmp_path: Path) -> None:
    """Test that 'How encode' (missing 'to') is rejected as invalid prefix."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## How encode
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "prefix" in errors[0].lower()
    assert "line 4" in errors[0]


def test_combined_errors_reported(tmp_path: Path) -> None:
    """Test that prefix error and content word error are both reported."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## When testing
Content here.

## Bad
More content.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 2
    assert any("content word" in e.lower() for e in errors)
    assert any("prefix" in e.lower() for e in errors)


def test_multiple_errors_reported(tmp_path: Path) -> None:
    """Test that multiple errors are all reported."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

---
## When first title word count too long here
Content here.

## When second title word count too long here
Different content.

## When duplicate title word
Another content.

## When duplicate title word
Final content.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 3
    assert sum(1 for e in errors if "title has 8 words" in e) == 2
    assert any("duplicate title" in e for e in errors)
