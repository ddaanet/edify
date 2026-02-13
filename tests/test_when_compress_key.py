"""Tests for compress key functionality."""

from pathlib import Path

from claudeutils.when.compress import (
    compress_key,
    generate_candidates,
    load_heading_corpus,
    verify_unique,
)


def test_load_heading_corpus(tmp_path: Path) -> None:
    """Load heading corpus from decision files."""
    # Create test directory with markdown files
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    # Create file with H2 and H3 headings
    file1 = decisions_dir / "test1.md"
    file1.write_text(
        """# Title (H1, should be ignored)
## Heading 2A
Some content
### Heading 3A
More content
## Heading 2B
"""
    )

    # Create another file with mixed headings
    file2 = decisions_dir / "test2.md"
    file2.write_text(
        """## Another H2
### Nested H3
## .Structural Heading (should be excluded)
### .Also Structural
## Final H2
"""
    )

    # Load headings
    headings = load_heading_corpus(decisions_dir)

    # Verify results
    assert isinstance(headings, list)
    assert len(headings) > 0
    assert "Heading 2A" in headings
    assert "Heading 3A" in headings
    assert "Heading 2B" in headings
    assert "Another H2" in headings
    assert "Nested H3" in headings
    assert "Final H2" in headings

    # Verify structural headings are excluded
    assert ".Structural Heading (should be excluded)" not in headings
    assert ".Also Structural" not in headings

    # Verify H1 is excluded
    assert "Title (H1, should be ignored)" not in headings


def test_load_heading_corpus_empty(tmp_path: Path) -> None:
    """Empty directory returns empty list."""
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    headings = load_heading_corpus(decisions_dir)

    assert headings == []


def test_generate_candidates() -> None:
    """Generate candidates from heading via word-drop algorithm."""
    candidates = generate_candidates("How to Encode Paths")

    # Must include specific combinations
    assert "how encode paths" in candidates
    assert "how encode path" in candidates
    assert "encode paths" in candidates
    assert "how paths" in candidates

    # All candidates must be lowercase
    assert all(c.islower() for c in candidates)

    # All candidates must have at least 2 words
    assert all(len(c.split()) >= 2 for c in candidates)

    # Candidates must be sorted by length (shortest first)
    word_counts = [len(c.split()) for c in candidates]
    assert word_counts == sorted(word_counts)


def test_uniqueness_verification() -> None:
    """Verify uniqueness checking via fuzzy scoring."""
    corpus = [
        "How to encode paths",
        "Path resolution in file mode",
        "Encoding strategies for URL parameters",
        "Character escaping and sanitization",
    ]

    # Specific trigger should uniquely resolve to "How to encode paths"
    assert verify_unique("how encode path", corpus) is True

    # Generic trigger matching multiple headings should return False
    assert verify_unique("encode", corpus) is False


def test_verify_unique_edge_cases() -> None:
    """Verify uniqueness edge cases."""
    # Empty corpus
    assert verify_unique("any trigger", []) is False

    # Single heading corpus
    assert verify_unique("test", ["Test Heading"]) is True


def test_suggest_minimal_trigger() -> None:
    """Suggest minimal unique trigger from heading."""
    corpus = [
        "How to encode paths",
        "Path resolution in file mode",
        "Encoding strategies for URL parameters",
        "Character escaping and sanitization",
    ]

    # Test 1: Returns shortest unique candidate
    result = compress_key("How to Encode Paths", corpus)
    assert isinstance(result, str)
    # "encode path" is shorter and unique, so it's returned
    assert verify_unique(result, corpus) is True
    # Result should be shorter than full heading
    assert len(result) < len("how to encode paths")

    # Test 2: Result is shorter than full heading for different heading
    result2 = compress_key("When Writing Mock Tests", corpus)
    assert len(result2) < len("when writing mock tests")

    # Test 3: Actually tight corpus still finds unique triggers due to fuzzy scoring
    # The implementation is smart enough to find "encode path" as unique
    tight_corpus = [
        "How to encode paths",
        "How to encode parameters",
        "How to encode strings",
    ]
    result3 = compress_key("How to Encode Paths", tight_corpus)
    # Verify it finds a unique trigger (even in tight corpus)
    assert verify_unique(result3, tight_corpus) is True
    # And it's shorter than full heading
    assert len(result3) < len("how to encode paths")
