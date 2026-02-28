"""Tests for topic matching and inverted index construction."""

from pathlib import Path

import pytest

from claudeutils.recall.index_parser import IndexEntry
from claudeutils.recall.relevance import RelevanceScore
from claudeutils.recall.topic_matcher import (
    build_inverted_index,
    get_candidates,
    resolve_entries,
    score_and_rank,
)


def test_build_inverted_index_maps_keywords_to_entries() -> None:
    """build_inverted_index should map each keyword to entries containing it."""
    entry_a = IndexEntry(
        key="test_a",
        description="description_a",
        referenced_file="file_a.md",
        section="Section A",
        keywords=frozenset({"recall", "system", "effectiveness"}),
    )
    entry_b = IndexEntry(
        key="test_b",
        description="description_b",
        referenced_file="file_b.md",
        section="Section B",
        keywords=frozenset({"recall", "hook", "injection"}),
    )
    entry_c = IndexEntry(
        key="test_c",
        description="description_c",
        referenced_file="file_c.md",
        section="Section C",
        keywords=frozenset({"commit", "message", "format"}),
    )

    index = build_inverted_index([entry_a, entry_b, entry_c])

    assert isinstance(index, dict)
    assert "recall" in index
    assert len(index["recall"]) == 2
    assert entry_a in index["recall"]
    assert entry_b in index["recall"]

    assert "hook" in index
    assert len(index["hook"]) == 1
    assert entry_b in index["hook"]

    assert "commit" in index
    assert len(index["commit"]) == 1
    assert entry_c in index["commit"]

    expected_keys = {
        "recall",
        "system",
        "effectiveness",
        "hook",
        "injection",
        "commit",
        "message",
        "format",
    }
    assert set(index.keys()) == expected_keys


def test_match_prompt_returns_candidates_with_overlap() -> None:
    """get_candidates should return entries matching prompt keywords."""
    entry_a = IndexEntry(
        key="test_a",
        description="description_a",
        referenced_file="file_a.md",
        section="Section A",
        keywords=frozenset({"recall", "system", "effectiveness"}),
    )
    entry_b = IndexEntry(
        key="test_b",
        description="description_b",
        referenced_file="file_b.md",
        section="Section B",
        keywords=frozenset({"recall", "hook", "injection"}),
    )
    entry_c = IndexEntry(
        key="test_c",
        description="description_c",
        referenced_file="file_c.md",
        section="Section C",
        keywords=frozenset({"commit", "message", "format"}),
    )

    inverted_index = build_inverted_index([entry_a, entry_b, entry_c])

    candidates = get_candidates("how does the recall system work", inverted_index)

    assert isinstance(candidates, set)
    assert entry_a in candidates
    assert entry_b in candidates
    assert entry_c not in candidates
    assert len(candidates) == 2


@pytest.mark.parametrize(
    ("threshold", "max_entries"),
    [(0.3, None), (0.3, 2)],
)
def test_score_candidates_ranks_by_relevance_and_filters(
    threshold: float, max_entries: int | None
) -> None:
    """score_and_rank should rank by relevance and apply threshold/cap."""
    entry_high = IndexEntry(
        key="high_match",
        description="test entry",
        referenced_file="file_a.md",
        section="Section A",
        keywords=frozenset({"recall", "system", "matching"}),
    )
    entry_mid = IndexEntry(
        key="mid_match",
        description="test entry",
        referenced_file="file_b.md",
        section="Section B",
        keywords=frozenset({"recall", "matching"}),
    )
    entry_low = IndexEntry(
        key="low_match",
        description="test entry",
        referenced_file="file_c.md",
        section="Section C",
        keywords=frozenset(
            {
                "other",
                "unrelated",
                "keywords",
                "none",
                "match",
                "here",
                "at",
                "all",
                "in",
            }
        ),
    )
    entry_cap1 = IndexEntry(
        key="cap1",
        description="test entry",
        referenced_file="file_d.md",
        section="Section D",
        keywords=frozenset({"recall", "test"}),
    )
    entry_cap2 = IndexEntry(
        key="cap2",
        description="test entry",
        referenced_file="file_e.md",
        section="Section E",
        keywords=frozenset({"system"}),
    )

    prompt_keywords = {"recall", "system", "matching"}
    candidates = {entry_high, entry_mid, entry_low, entry_cap1, entry_cap2}

    result = score_and_rank(
        prompt_keywords, candidates, threshold=threshold, max_entries=max_entries
    )

    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
    assert all(isinstance(item[1], RelevanceScore) for item in result)
    assert all(item[1].score >= threshold for item in result)

    if max_entries:
        assert len(result) <= max_entries

    if len(result) > 1:
        scores = [item[1].score for item in result]
        assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize(
    "setup_case",
    ["happy_path", "missing_file", "missing_section"],
)
def test_resolve_entries(tmp_path: Path, setup_case: str) -> None:
    """resolve_entries should extract sections and handle error cases.

    Test cases: happy path (file + section exists), missing file, missing section.
    """
    if setup_case == "happy_path":
        decision_file = tmp_path / "agents" / "decisions" / "test.md"
        decision_file.parent.mkdir(parents=True, exist_ok=True)
        decision_file.write_text(
            "# Test Decisions\n\n"
            "## When Evaluating Recall System Effectiveness\n\n"
            "Anti-pattern: Measuring without proper baseline\n\n"
            "## Other Section\n\n"
            "Other content here\n"
        )

        entry = IndexEntry(
            key="evaluating recall system effectiveness",
            description="test entry",
            referenced_file="agents/decisions/test.md",
            section="Test",
            keywords=frozenset({"recall", "effectiveness"}),
        )
        score = RelevanceScore(
            session_id="hook",
            entry_key=entry.key,
            score=0.8,
            is_relevant=True,
            matched_keywords={"recall", "effectiveness"},
        )

        result = resolve_entries([(entry, score)], tmp_path)

        assert len(result) == 1
        assert "Evaluating Recall System Effectiveness" in result[0].content
        assert "Anti-pattern" in result[0].content
        assert str(decision_file) == str(result[0].source_file)

    elif setup_case == "missing_file":
        entry = IndexEntry(
            key="nonexistent",
            description="test entry",
            referenced_file="agents/decisions/nonexistent.md",
            section="Test",
            keywords=frozenset({"test"}),
        )
        score = RelevanceScore(
            session_id="hook",
            entry_key=entry.key,
            score=0.5,
            is_relevant=True,
            matched_keywords={"test"},
        )

        result = resolve_entries([(entry, score)], tmp_path)

        assert len(result) == 0

    elif setup_case == "missing_section":
        decision_file = tmp_path / "agents" / "decisions" / "test.md"
        decision_file.parent.mkdir(parents=True, exist_ok=True)
        decision_file.write_text(
            "# Test Decisions\n\n## Some Other Section\n\nContent here\n"
        )

        entry = IndexEntry(
            key="nonexistent section",
            description="test entry",
            referenced_file="agents/decisions/test.md",
            section="Test",
            keywords=frozenset({"test"}),
        )
        score = RelevanceScore(
            session_id="hook",
            entry_key=entry.key,
            score=0.5,
            is_relevant=True,
            matched_keywords={"test"},
        )

        result = resolve_entries([(entry, score)], tmp_path)

        assert len(result) == 0
