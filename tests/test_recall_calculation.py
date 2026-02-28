"""Tests for recall calculation and discovery patterns."""

from claudeutils.recall.index_parser import IndexEntry
from claudeutils.recall.recall import (
    DiscoveryPattern,
    calculate_recall,
    classify_discovery_pattern,
)
from claudeutils.recall.relevance import RelevanceScore
from claudeutils.recall.tool_calls import ToolCall


def test_discovery_pattern_direct() -> None:
    """Direct read with no preceding search."""
    entry_file = "/path/to/file.md"
    relevant = RelevanceScore(
        session_id="session1",
        entry_key="test entry",
        score=0.8,
        is_relevant=True,
        matched_keywords={"test"},
    )

    tool_calls = [
        ToolCall(
            tool_name="Read",
            tool_id="read_1",
            input={"file_path": "/path/to/file.md"},
            timestamp="2025-12-16T10:00:00.000Z",
            session_id="session1",
        ),
    ]

    pattern = classify_discovery_pattern(relevant, tool_calls, entry_file, "session1")
    assert pattern == DiscoveryPattern.DIRECT


def test_discovery_pattern_search_then_read() -> None:
    """Grep then Read pattern."""
    entry_file = "/path/to/file.md"
    relevant = RelevanceScore(
        session_id="session1",
        entry_key="test entry",
        score=0.8,
        is_relevant=True,
        matched_keywords={"test"},
    )

    tool_calls = [
        ToolCall(
            tool_name="Grep",
            tool_id="grep_1",
            input={"path": "/path/to"},
            timestamp="2025-12-16T10:00:00.000Z",
            session_id="session1",
        ),
        ToolCall(
            tool_name="Read",
            tool_id="read_1",
            input={"file_path": "/path/to/file.md"},
            timestamp="2025-12-16T10:00:01.000Z",
            session_id="session1",
        ),
    ]

    pattern = classify_discovery_pattern(relevant, tool_calls, entry_file, "session1")
    assert pattern == DiscoveryPattern.SEARCH_THEN_READ


def test_discovery_pattern_not_found() -> None:
    """File never read."""
    entry_file = "/path/to/file.md"
    relevant = RelevanceScore(
        session_id="session1",
        entry_key="test entry",
        score=0.8,
        is_relevant=True,
        matched_keywords={"test"},
    )

    tool_calls = [
        ToolCall(
            tool_name="Grep",
            tool_id="grep_1",
            input={"path": "/other/path"},
            timestamp="2025-12-16T10:00:00.000Z",
            session_id="session1",
        ),
    ]

    pattern = classify_discovery_pattern(relevant, tool_calls, entry_file, "session1")
    assert pattern == DiscoveryPattern.NOT_FOUND


def test_calculate_recall_simple() -> None:
    """Calculate recall for simple case."""
    entries = [
        IndexEntry(
            key="test entry",
            description="for testing",
            referenced_file="test.md",
            section="Test",
            keywords=frozenset({"test"}),
        ),
    ]

    sessions_data = {
        "session1": [
            ToolCall(
                tool_name="Read",
                tool_id="read_1",
                input={"file_path": "test.md"},
                timestamp="2025-12-16T10:00:00.000Z",
                session_id="session1",
            ),
        ],
    }

    relevant_entries = {
        "session1": [
            RelevanceScore(
                session_id="session1",
                entry_key="test entry",
                score=0.8,
                is_relevant=True,
                matched_keywords={"test"},
            ),
        ],
    }

    analysis = calculate_recall(sessions_data, relevant_entries, entries)

    assert analysis.sessions_analyzed == 1
    assert analysis.relevant_pairs_total == 1
    assert analysis.pairs_with_read == 1
    assert analysis.overall_recall_percent == 100.0


def test_calculate_recall_multiple_sessions() -> None:
    """Calculate recall across multiple sessions."""
    entries = [
        IndexEntry(
            key="test entry",
            description="for testing",
            referenced_file="test.md",
            section="Test",
            keywords=frozenset({"test"}),
        ),
    ]

    sessions_data = {
        "session1": [
            ToolCall(
                tool_name="Read",
                tool_id="read_1",
                input={"file_path": "test.md"},
                timestamp="2025-12-16T10:00:00.000Z",
                session_id="session1",
            ),
        ],
        "session2": [],  # No reads
    }

    relevant_entries = {
        "session1": [
            RelevanceScore(
                session_id="session1",
                entry_key="test entry",
                score=0.8,
                is_relevant=True,
                matched_keywords={"test"},
            ),
        ],
        "session2": [
            RelevanceScore(
                session_id="session2",
                entry_key="test entry",
                score=0.8,
                is_relevant=True,
                matched_keywords={"test"},
            ),
        ],
    }

    analysis = calculate_recall(sessions_data, relevant_entries, entries)

    assert analysis.sessions_analyzed == 2
    assert analysis.relevant_pairs_total == 2
    assert analysis.pairs_with_read == 1
    assert analysis.overall_recall_percent == 50.0


def test_calculate_recall_per_entry_metrics() -> None:
    """Per-entry metrics calculated correctly."""
    entries = [
        IndexEntry(
            key="entry a",
            description="description a",
            referenced_file="a.md",
            section="Test",
            keywords=frozenset({"entry_a"}),
        ),
        IndexEntry(
            key="entry b",
            description="description b",
            referenced_file="b.md",
            section="Test",
            keywords=frozenset({"entry_b"}),
        ),
    ]

    sessions_data = {
        "session1": [
            ToolCall(
                tool_name="Read",
                tool_id="read_a",
                input={"file_path": "a.md"},
                timestamp="2025-12-16T10:00:00.000Z",
                session_id="session1",
            ),
        ],
        "session2": [
            ToolCall(
                tool_name="Read",
                tool_id="read_b",
                input={"file_path": "b.md"},
                timestamp="2025-12-16T10:00:00.000Z",
                session_id="session2",
            ),
        ],
    }

    relevant_entries = {
        "session1": [
            RelevanceScore(
                session_id="session1",
                entry_key="entry a",
                score=0.8,
                is_relevant=True,
                matched_keywords={"entry_a"},
            ),
            RelevanceScore(
                session_id="session1",
                entry_key="entry b",
                score=0.8,
                is_relevant=True,
                matched_keywords={"entry_b"},
            ),
        ],
        "session2": [
            RelevanceScore(
                session_id="session2",
                entry_key="entry a",
                score=0.8,
                is_relevant=True,
                matched_keywords={"entry_a"},
            ),
            RelevanceScore(
                session_id="session2",
                entry_key="entry b",
                score=0.8,
                is_relevant=True,
                matched_keywords={"entry_b"},
            ),
        ],
    }

    analysis = calculate_recall(sessions_data, relevant_entries, entries)

    assert len(analysis.per_entry_results) == 2

    # Find entry a result: relevant in session1 and session2, read only in session1
    entry_a = next(r for r in analysis.per_entry_results if r.entry_key == "entry a")
    assert entry_a.total_relevant_sessions == 2
    assert entry_a.sessions_with_read == 1
    assert entry_a.recall_percent == 50.0

    # Find entry b result: relevant in session1 and session2, read only in session2
    entry_b = next(r for r in analysis.per_entry_results if r.entry_key == "entry b")
    assert entry_b.total_relevant_sessions == 2
    assert entry_b.sessions_with_read == 1
    assert entry_b.recall_percent == 50.0


def test_calculate_recall_empty_input() -> None:
    """Empty input returns zero metrics."""
    analysis = calculate_recall({}, {}, [])

    assert analysis.sessions_analyzed == 0
    assert analysis.relevant_pairs_total == 0
    assert analysis.pairs_with_read == 0
    assert analysis.overall_recall_percent == 0.0
    assert analysis.per_entry_results == []


def test_discovery_pattern_absolute_vs_relative_paths() -> None:
    """Path matching works with absolute tool paths and relative index paths."""
    # Index entry uses relative path (as stored in memory-index.md)
    entry_file = "agents/decisions/testing.md"
    relevant = RelevanceScore(
        session_id="session1",
        entry_key="test entry",
        score=0.8,
        is_relevant=True,
        matched_keywords={"test"},
    )

    # Tool call uses absolute path (as recorded in real sessions)
    tool_calls = [
        ToolCall(
            tool_name="Read",
            tool_id="read_1",
            input={
                "file_path": "/Users/david/code/claudeutils/agents/decisions/testing.md"
            },
            timestamp="2025-12-16T10:00:00.000Z",
            session_id="session1",
        ),
    ]

    pattern = classify_discovery_pattern(relevant, tool_calls, entry_file, "session1")
    # Should match despite path format difference
    assert pattern == DiscoveryPattern.DIRECT
