"""Tests for topic matching and inverted index construction."""

from claudeutils.recall.index_parser import IndexEntry
from claudeutils.recall.topic_matcher import build_inverted_index, get_candidates


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
