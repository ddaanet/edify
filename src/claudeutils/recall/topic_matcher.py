"""Topic matching pipeline: index construction, matching, and output formatting."""

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from claudeutils.recall.index_parser import (
    IndexEntry,
    extract_keywords,
    parse_memory_index,
)
from claudeutils.recall.relevance import RelevanceScore, score_relevance
from claudeutils.when.resolver import extract_section

logger = logging.getLogger(__name__)


@dataclass
class ResolvedEntry:
    """Resolved decision file section."""

    content: str
    source_file: Path
    entry: IndexEntry


def build_inverted_index(entries: list[IndexEntry]) -> dict[str, list[IndexEntry]]:
    """Build inverted index mapping keywords to entries containing them."""
    index: dict[str, list[IndexEntry]] = defaultdict(list)
    for entry in entries:
        for keyword in entry.keywords:
            index[keyword].append(entry)
    return dict(index)


def get_candidates(
    prompt_keywords: set[str], inverted_index: dict[str, list[IndexEntry]]
) -> set[IndexEntry]:
    """Get candidate entries matching prompt keywords.

    Returns the union of all entries matching any prompt keyword.
    """
    candidates: set[IndexEntry] = set()
    for keyword in prompt_keywords:
        if keyword in inverted_index:
            candidates.update(inverted_index[keyword])
    return candidates


def score_and_rank(
    prompt_keywords: set[str],
    candidates: set[IndexEntry],
    threshold: float = 0.3,
    max_entries: int | None = None,
) -> list[tuple[IndexEntry, RelevanceScore]]:
    """Score and rank candidates by relevance to prompt keywords.

    Filters by threshold, sorts by score descending, caps to max_entries.
    """
    scored = [
        (entry, score_relevance("hook", prompt_keywords, entry, threshold=threshold))
        for entry in candidates
    ]
    relevant = [(entry, score) for entry, score in scored if score.is_relevant]
    ranked = sorted(relevant, key=lambda x: x[1].score, reverse=True)
    return ranked[:max_entries] if max_entries else ranked


def _capitalize_heading(text: str) -> str:
    """Capitalize heading text: normal words capitalized, all-caps preserved.

    Note: Same pattern exists in when/resolver.py:_build_heading.
    Not extracted — introducing when→recall dependency for a one-liner
    is disproportionate to the duplication risk.
    """
    words = text.split()
    return " ".join(w if w.isupper() else w.capitalize() for w in words)


def resolve_entries(
    entries: list[tuple[IndexEntry, RelevanceScore]], project_dir: Path
) -> list[ResolvedEntry]:
    """Resolve matched entries to decision file content.

    For each entry, constructs file path and tries both "When {key}" and
    "How to {key}" heading patterns. Silently skips entries with no matching
    section.

    Args:
        entries: List of (IndexEntry, RelevanceScore) tuples
        project_dir: Project root directory for resolving relative paths

    Returns:
        List of ResolvedEntry objects with extracted content
    """
    resolved: list[ResolvedEntry] = []

    for entry, _score in entries:
        file_path = project_dir / entry.referenced_file

        capitalized_key = _capitalize_heading(entry.key)
        headings_to_try = [
            f"## When {capitalized_key}",
            f"## How to {capitalized_key}",
        ]

        content = ""
        for heading in headings_to_try:
            content = extract_section(file_path, heading)
            if content:
                break

        if content:
            resolved.append(
                ResolvedEntry(content=content, source_file=file_path, entry=entry)
            )

    return resolved


@dataclass
class TopicMatchResult:
    """Dual-channel output from topic matching."""

    context: str
    system_message: str


def format_output(resolved: list[ResolvedEntry]) -> TopicMatchResult:
    """Format resolved entries as dual-channel output.

    Produces agent context (full decision sections) and user-visible system
    message (trigger list with injected line count).
    """
    if not resolved:
        return TopicMatchResult(context="", system_message="")

    context_parts = []
    trigger_list = []

    for resolved_entry in resolved:
        context_parts.append(
            f"{resolved_entry.content}\n\nSource: {resolved_entry.source_file}"
        )
        entry = resolved_entry.entry
        trigger_line = (
            f"{entry.key} | {entry.description}" if entry.description else entry.key
        )
        trigger_list.append(trigger_line)

    context = "\n\n".join(context_parts)
    context_lines = len(context.split("\n"))

    system_message = f"topic ({context_lines} lines):\n" + "\n".join(trigger_list)

    return TopicMatchResult(context=context, system_message=system_message)


def _entries_to_json_serializable(entries: list[IndexEntry]) -> list[dict[str, object]]:
    """Convert IndexEntry list to JSON-serializable format."""
    return [
        {
            "key": entry.key,
            "description": entry.description,
            "referenced_file": entry.referenced_file,
            "section": entry.section,
            "keywords": sorted(entry.keywords),
        }
        for entry in entries
    ]


def _dict_to_index(
    inverted_index: dict[str, list[IndexEntry]],
) -> dict[str, list[dict[str, object]]]:
    """Convert inverted index to JSON-serializable format."""
    return {
        keyword: _entries_to_json_serializable(entries)
        for keyword, entries in inverted_index.items()
    }


def _get_cache_path(index_path: Path, project_dir: Path) -> Path:
    """Generate cache file path based on hash of index path and project dir."""
    hash_input = str(index_path) + str(project_dir)
    hash_digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]
    return project_dir / "tmp" / f"topic-index-{hash_digest}.json"


def _json_to_entries(entries_json: list[dict[str, object]]) -> list[IndexEntry]:
    """Reconstruct IndexEntry list from JSON-serializable format."""
    entries = []
    for entry_dict in entries_json:
        keywords_data = entry_dict.get("keywords")
        keywords = (
            frozenset(str(k) for k in keywords_data)
            if isinstance(keywords_data, list)
            else frozenset()
        )
        entries.append(
            IndexEntry(
                key=str(entry_dict["key"]),
                description=str(entry_dict["description"]),
                referenced_file=str(entry_dict["referenced_file"]),
                section=str(entry_dict["section"]),
                keywords=keywords,
            )
        )
    return entries


def _json_to_inverted_index(
    index_json: dict[str, list[dict[str, object]]],
) -> dict[str, list[IndexEntry]]:
    """Reconstruct inverted index from JSON-serializable format."""
    index: dict[str, list[IndexEntry]] = {}
    for keyword, entries_list in index_json.items():
        index[keyword] = _json_to_entries(entries_list)
    return index


def _save_index_cache(
    entries: list[IndexEntry],
    inverted_index: dict[str, list[IndexEntry]],
    cache_path: Path,
    source_mtime: float,
) -> None:
    """Save index to cache file.

    Silently fail on cache write error.
    """
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        cache_data = {
            "entries": _entries_to_json_serializable(entries),
            "inverted_index": _dict_to_index(inverted_index),
            "timestamp": source_mtime,
        }

        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(cache_data, f)
    except (OSError, TypeError):
        logger.debug("Failed to cache index to %s", cache_path)


def get_or_build_index(
    index_path: Path, project_dir: Path
) -> tuple[list[IndexEntry], dict[str, list[IndexEntry]]]:
    """Build inverted index from memory-index file and cache it.

    Reads from cache if available and source file is unchanged (mtime check).
    Cache miss or source file newer than cache triggers rebuild.

    Args:
        index_path: Path to memory-index.md file
        project_dir: Project root directory

    Returns:
        Tuple of (entries list, inverted index dict)
    """
    if not index_path.exists():
        return [], {}

    cache_path = _get_cache_path(index_path, project_dir)
    source_mtime = index_path.stat().st_mtime

    if cache_path.exists():
        try:
            cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
            cache_timestamp = cache_data.get("timestamp", 0.0)

            if source_mtime <= cache_timestamp:
                entries = _json_to_entries(cache_data["entries"])
                inverted_index = _json_to_inverted_index(cache_data["inverted_index"])
                return entries, inverted_index
        except (OSError, json.JSONDecodeError, KeyError):
            logger.debug("Failed to read cache from %s, rebuilding", cache_path)

    entries = parse_memory_index(index_path)
    inverted_index = build_inverted_index(entries)
    _save_index_cache(entries, inverted_index, cache_path, source_mtime)

    return entries, inverted_index


def match_topics(
    prompt_text: str,
    index_path: Path,
    project_dir: Path,
    threshold: float = 0.3,
    max_entries: int = 3,
) -> TopicMatchResult:
    """Top-level entry point for topic matching pipeline.

    Wraps: get_or_build_index → get_candidates → score_and_rank →
    resolve_entries → format_output
    """
    _entries, inverted_index = get_or_build_index(index_path, project_dir)
    prompt_keywords = extract_keywords(prompt_text)
    candidates = get_candidates(prompt_keywords, inverted_index)
    ranked = score_and_rank(prompt_keywords, candidates, threshold, max_entries)
    resolved = resolve_entries(ranked, project_dir)
    return format_output(resolved)
