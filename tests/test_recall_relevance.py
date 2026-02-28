"""Tests for relevance scoring."""

from pathlib import Path

import pytest

from claudeutils.recall.index_parser import IndexEntry
from claudeutils.recall.relevance import find_relevant_entries, score_relevance


def test_score_relevance_exact_match() -> None:
    """Perfect keyword match scores 1.0."""
    entry = IndexEntry(
        key="test entry",
        description="for testing",
        referenced_file="test.md",
        section="Test Section",
        keywords=frozenset({"test", "entry"}),
    )

    session_keywords = {"test", "entry", "other"}
    score = score_relevance("session1", session_keywords, entry, threshold=0.3)

    assert score.score == 1.0
    assert score.is_relevant is True


def test_score_relevance_partial_match() -> None:
    """Partial keyword match scores between 0 and 1."""
    entry = IndexEntry(
        key="test entry data",
        description="for testing",
        referenced_file="test.md",
        section="Test Section",
        keywords=frozenset({"test", "entry", "data"}),
    )

    # Only 2 of 3 keywords match
    session_keywords = {"test", "entry", "other"}
    score = score_relevance("session1", session_keywords, entry, threshold=0.3)

    assert score.score == pytest.approx(2.0 / 3.0)
    assert score.is_relevant is True


def test_score_relevance_no_match() -> None:
    """No keyword match scores 0.0."""
    entry = IndexEntry(
        key="test entry",
        description="for testing",
        referenced_file="test.md",
        section="Test Section",
        keywords=frozenset({"test", "entry"}),
    )

    session_keywords = {"other", "keywords"}
    score = score_relevance("session1", session_keywords, entry, threshold=0.3)

    assert score.score == 0.0
    assert score.is_relevant is False


def test_score_relevance_threshold(tmp_path: Path) -> None:
    """Score above threshold is relevant."""
    entry = IndexEntry(
        key="test entry data",
        description="description",
        referenced_file="test.md",
        section="Test Section",
        keywords=frozenset({"test", "entry", "data"}),
    )

    # 1 of 3 keywords match: 33%
    session_keywords = {"test", "other"}

    # Below threshold (0.3)
    score1 = score_relevance("session1", session_keywords, entry, threshold=0.4)
    assert score1.is_relevant is False

    # Above threshold (0.3)
    score2 = score_relevance("session1", session_keywords, entry, threshold=0.3)
    assert score2.is_relevant is True


def test_score_relevance_matched_keywords() -> None:
    """Matched keywords are recorded."""
    entry = IndexEntry(
        key="test entry data",
        description="description",
        referenced_file="test.md",
        section="Test Section",
        keywords=frozenset({"test", "entry", "data"}),
    )

    session_keywords = {"test", "other", "entry"}
    score = score_relevance("session1", session_keywords, entry, threshold=0.3)

    assert score.matched_keywords == {"test", "entry"}


def test_find_relevant_entries_single_relevant() -> None:
    """Find single relevant entry from list."""
    entries = [
        IndexEntry(
            key="relevant entry",
            description="matches session",
            referenced_file="match.md",
            section="Section 1",
            keywords=frozenset({"relevant", "entry"}),
        ),
        IndexEntry(
            key="irrelevant entry",
            description="does not match",
            referenced_file="nomatch.md",
            section="Section 2",
            keywords=frozenset({"irrelevant", "unrelated"}),
        ),
    ]

    session_keywords = {"relevant", "entry"}
    relevant = find_relevant_entries(
        "session1", session_keywords, entries, threshold=0.3
    )

    assert len(relevant) == 1
    assert relevant[0].entry_key == "relevant entry"


def test_find_relevant_entries_multiple_relevant() -> None:
    """Find multiple relevant entries."""
    entries = [
        IndexEntry(
            key="testing features",
            description="test-related",
            referenced_file="test.md",
            section="Section 1",
            keywords=frozenset({"testing", "features"}),
        ),
        IndexEntry(
            key="refactor code",
            description="code refactoring",
            referenced_file="refactor.md",
            section="Section 2",
            keywords=frozenset({"refactor", "code"}),
        ),
    ]

    session_keywords = {"testing", "refactor", "code"}
    relevant = find_relevant_entries(
        "session1", session_keywords, entries, threshold=0.5
    )

    assert len(relevant) == 2


def test_find_relevant_entries_sorted_by_score() -> None:
    """Results sorted by score descending."""
    entries = [
        IndexEntry(
            key="entry a",
            description="keywords",
            referenced_file="a.md",
            section="Section",
            keywords=frozenset({"alpha"}),
        ),
        IndexEntry(
            key="entry b",
            description="keywords",
            referenced_file="b.md",
            section="Section",
            keywords=frozenset({"beta", "gamma"}),
        ),
    ]

    # alpha matches 1/1 (100%), beta and gamma match 2/2 (100%)
    session_keywords = {"alpha", "beta", "gamma"}
    relevant = find_relevant_entries(
        "session1", session_keywords, entries, threshold=0.0
    )

    # Both are 100%, but they may be in definition order
    assert len(relevant) == 2


def test_find_relevant_entries_empty_session_keywords() -> None:
    """Empty session keywords returns no relevant entries."""
    entries = [
        IndexEntry(
            key="entry",
            description="description",
            referenced_file="test.md",
            section="Section",
            keywords=frozenset({"test"}),
        ),
    ]

    session_keywords: set[str] = set()
    relevant = find_relevant_entries(
        "session1", session_keywords, entries, threshold=0.3
    )

    assert len(relevant) == 0


def test_find_relevant_entries_no_entries() -> None:
    """No entries returns empty list."""
    session_keywords = {"test", "keywords"}
    relevant = find_relevant_entries("session1", session_keywords, [], threshold=0.3)

    assert relevant == []
