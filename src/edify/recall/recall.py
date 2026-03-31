"""Calculate recall metrics and discovery patterns."""

import logging
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from edify.recall.index_parser import IndexEntry
from edify.recall.relevance import RelevanceScore
from edify.recall.tool_calls import ToolCall

logger = logging.getLogger(__name__)


class DiscoveryPattern(StrEnum):
    """Classification of how agent discovered a referenced file."""

    DIRECT = "direct"  # Read with no preceding Grep/Glob
    SEARCH_THEN_READ = "search_then_read"  # Grep/Glob before Read
    USER_DIRECTED = "user_directed"  # User message contained file path
    NOT_FOUND = "not_found"  # Relevant entry but file not Read


class EntryRecall(BaseModel):
    """Recall metrics for a single index entry."""

    entry_key: str
    referenced_file: str
    total_relevant_sessions: int  # Sessions where entry was relevant
    sessions_with_read: int  # Sessions that Read the file
    recall_percent: float  # 100 * sessions_with_read / total_relevant_sessions
    direct_percent: float  # % of discovered via direct Read
    search_then_read_percent: float  # % via search-then-read
    user_directed_percent: float  # % via user-directed
    pattern_counts: dict[str, int]  # Detailed pattern counts


class RecallAnalysis(BaseModel):
    """Overall recall analysis results."""

    sessions_analyzed: int
    relevant_pairs_total: int  # (session, entry) pairs where entry was relevant
    pairs_with_read: int  # Pairs where file was Read
    overall_recall_percent: float
    per_entry_results: list[EntryRecall]
    pattern_summary: dict[str, int]  # Aggregate pattern counts


def _extract_file_from_input(tool_input: dict[str, Any]) -> str | None:
    """Extract file path from tool input dict.

    Handles different tool types:
    - Read: file_path
    - Grep: path
    - Glob: path
    - Write: file_path
    - Bash: command (no file target)

    Args:
        tool_input: Tool input dictionary

    Returns:
        File path if found, None otherwise
    """
    # Try common file path keys
    for key in ["file_path", "path"]:
        if key in tool_input:
            path_value = tool_input[key]
            if isinstance(path_value, str):
                return path_value

    return None


def _matches_file_or_parent(target_file: str, tool_file: str) -> bool:
    """Check if tool file matches target file or its parent directory.

    Args:
        target_file: Referenced file from index entry (may be relative)
        tool_file: File from tool input (may be absolute)

    Returns:
        True if tool targets the file or its parent directory
    """
    target_path = Path(target_file)
    tool_path = Path(tool_file)

    # Exact match (both absolute or both relative with same path)
    if target_path == tool_path:
        return True

    # Normalize: compare via suffix match when paths differ in absoluteness
    # e.g., "/Users/.../agents/decisions/testing.md" matches
    # "agents/decisions/testing.md"
    if _paths_match_by_suffix(target_path, tool_path):
        return True

    # Tool targets parent directory of target file
    # e.g., tool_file="src/", target_file="src/file.md"
    try:
        target_path.relative_to(tool_path)
        # Only match if tool_path is a directory (no file extension)
        return bool(not tool_path.suffix)
    except ValueError:
        return False


def _paths_match_by_suffix(target_path: Path, tool_path: Path) -> bool:
    """Check if absolute and relative paths match by suffix comparison.

    Args:
        target_path: Target path (may be relative)
        tool_path: Tool path (may be absolute)

    Returns:
        True if paths match by suffix
    """
    if tool_path.is_absolute() and not target_path.is_absolute():
        return _suffix_matches(tool_path, target_path)
    if target_path.is_absolute() and not tool_path.is_absolute():
        return _suffix_matches(target_path, tool_path)
    return False


def _suffix_matches(abs_path: Path, rel_path: Path) -> bool:
    """Check if absolute path ends with relative path components.

    Args:
        abs_path: Absolute path
        rel_path: Relative path

    Returns:
        True if abs_path ends with rel_path
    """
    if len(rel_path.parts) > len(abs_path.parts):
        return False
    return abs_path.parts[-len(rel_path.parts) :] == rel_path.parts


def classify_discovery_pattern(
    _relevant_entry: RelevanceScore,
    tool_calls: list[ToolCall],
    referenced_file: str,
    _session_id: str,
) -> DiscoveryPattern:
    """Classify how agent discovered a referenced file.

    Analyzes the sequence of tool calls in the session to determine if:
    - File was Read directly (direct)
    - File was searched for first via Grep/Glob (search_then_read)
    - File path was in user message (user_directed)
    - File was never Read (not_found)

    Args:
        relevant_entry: RelevanceScore indicating entry was relevant
        tool_calls: Tool calls from the session
        referenced_file: File referenced by index entry
        session_id: Session identifier for logging

    Returns:
        DiscoveryPattern classification
    """
    # Find Read calls to the referenced file
    read_calls = [
        tc
        for tc in tool_calls
        if tc.tool_name == "Read"
        and _matches_file_or_parent(
            referenced_file, _extract_file_from_input(tc.input) or ""
        )
    ]

    if not read_calls:
        return DiscoveryPattern.NOT_FOUND

    first_read_index = tool_calls.index(read_calls[0])

    # Check for preceding Grep or Glob calls to same file/directory
    for i in range(first_read_index):
        tc = tool_calls[i]
        if tc.tool_name in ("Grep", "Glob"):
            tool_file = _extract_file_from_input(tc.input)
            if tool_file and _matches_file_or_parent(referenced_file, tool_file):
                return DiscoveryPattern.SEARCH_THEN_READ

    # Default to direct if no preceding search
    return DiscoveryPattern.DIRECT


def calculate_recall(
    sessions_data: dict[str, list[ToolCall]],  # session_id -> tool_calls
    relevant_entries: dict[str, list[RelevanceScore]],  # session_id -> relevant entries
    index_entries: list[IndexEntry],
) -> RecallAnalysis:
    """Calculate overall recall metrics and per-entry results.

    Args:
        sessions_data: Mapping of session_id to tool calls
        relevant_entries: Mapping of session_id to relevant index entries
        index_entries: All index entries for reference

    Returns:
        RecallAnalysis with overall and per-entry metrics
    """
    # Build mapping of entry_key to IndexEntry for file lookup
    entry_map = {entry.key: entry for entry in index_entries}

    # Aggregate metrics per entry
    entry_metrics: dict[str, dict[str, Any]] = {}

    for session_id, relevant_list in relevant_entries.items():
        tool_calls = sessions_data.get(session_id, [])

        for rel_score in relevant_list:
            entry_key = rel_score.entry_key
            if entry_key not in entry_metrics:
                entry = entry_map.get(entry_key)
                if not entry:
                    continue

                entry_metrics[entry_key] = {
                    "file": entry.referenced_file,
                    "total_relevant": 0,
                    "sessions_with_read": set(),
                    "patterns": {
                        DiscoveryPattern.DIRECT.value: 0,
                        DiscoveryPattern.SEARCH_THEN_READ.value: 0,
                        DiscoveryPattern.USER_DIRECTED.value: 0,
                        DiscoveryPattern.NOT_FOUND.value: 0,
                    },
                }

            # Count this as a relevant occurrence
            entry_metrics[entry_key]["total_relevant"] += 1

            # Classify discovery pattern and check if file was read
            entry = entry_map.get(entry_key)
            if entry:
                pattern = classify_discovery_pattern(
                    rel_score, tool_calls, entry.referenced_file, session_id
                )

                entry_metrics[entry_key]["patterns"][pattern.value] += 1

                if pattern != DiscoveryPattern.NOT_FOUND:
                    entry_metrics[entry_key]["sessions_with_read"].add(session_id)

    # Build per-entry results
    per_entry_results: list[EntryRecall] = []
    total_relevant = 0
    total_with_read = 0
    pattern_counts = {
        DiscoveryPattern.DIRECT.value: 0,
        DiscoveryPattern.SEARCH_THEN_READ.value: 0,
        DiscoveryPattern.USER_DIRECTED.value: 0,
        DiscoveryPattern.NOT_FOUND.value: 0,
    }

    for entry_key, metrics in entry_metrics.items():
        total_rel = metrics["total_relevant"]
        sessions_read = len(metrics["sessions_with_read"])
        recall_pct = (100 * sessions_read / total_rel) if total_rel > 0 else 0

        patterns = metrics["patterns"]
        found_count = (
            patterns[DiscoveryPattern.DIRECT.value]
            + patterns[DiscoveryPattern.SEARCH_THEN_READ.value]
            + patterns[DiscoveryPattern.USER_DIRECTED.value]
        )
        direct_pct = (
            (100 * patterns[DiscoveryPattern.DIRECT.value] / found_count)
            if found_count > 0
            else 0
        )
        search_pct = (
            (100 * patterns[DiscoveryPattern.SEARCH_THEN_READ.value] / found_count)
            if found_count > 0
            else 0
        )
        user_pct = (
            (100 * patterns[DiscoveryPattern.USER_DIRECTED.value] / found_count)
            if found_count > 0
            else 0
        )

        result = EntryRecall(
            entry_key=entry_key,
            referenced_file=metrics["file"],
            total_relevant_sessions=total_rel,
            sessions_with_read=sessions_read,
            recall_percent=recall_pct,
            direct_percent=direct_pct,
            search_then_read_percent=search_pct,
            user_directed_percent=user_pct,
            pattern_counts=patterns,
        )
        per_entry_results.append(result)

        total_relevant += total_rel
        total_with_read += sessions_read
        for pattern_name, count in patterns.items():
            pattern_counts[pattern_name] += count

    # Sort per-entry results by recall (highest first)
    per_entry_results.sort(key=lambda r: r.recall_percent, reverse=True)

    overall_recall = (
        (100 * total_with_read / total_relevant) if total_relevant > 0 else 0
    )

    return RecallAnalysis(
        sessions_analyzed=len(sessions_data),
        relevant_pairs_total=total_relevant,
        pairs_with_read=total_with_read,
        overall_recall_percent=overall_recall,
        per_entry_results=per_entry_results,
        pattern_summary=pattern_counts,
    )
