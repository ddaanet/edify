"""Topic matching pipeline: index construction, matching, and output formatting."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from claudeutils.recall.index_parser import IndexEntry, extract_keywords
from claudeutils.recall.relevance import RelevanceScore, score_relevance
from claudeutils.when.resolver import extract_section


@dataclass
class ResolvedEntry:
    """Resolved decision file section."""

    content: str
    source_file: Path
    entry: IndexEntry


def build_inverted_index(entries: list[IndexEntry]) -> dict[str, list[IndexEntry]]:
    """Build inverted index mapping keywords to entries containing them.

    Args:
        entries: List of IndexEntry objects

    Returns:
        Dictionary mapping keyword strings to lists of IndexEntry objects
    """
    index: dict[str, list[IndexEntry]] = defaultdict(list)
    for entry in entries:
        for keyword in entry.keywords:
            index[keyword].append(entry)
    return dict(index)


def get_candidates(
    prompt_text: str, inverted_index: dict[str, list[IndexEntry]]
) -> set[IndexEntry]:
    """Get candidate entries matching prompt keywords.

    Tokenizes prompt using the same rules as index entries, then returns
    the union of all entries matching any prompt keyword.

    Args:
        prompt_text: Text to tokenize and match against index
        inverted_index: Inverted index from build_inverted_index()

    Returns:
        Set of IndexEntry objects with keyword overlap
    """
    prompt_keywords = extract_keywords(prompt_text)
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

    Filters entries by relevance threshold and caps results to max_entries.

    Args:
        prompt_keywords: Set of keywords extracted from prompt
        candidates: Set of candidate entries to score
        threshold: Minimum score to include entry (default 0.3)
        max_entries: Maximum entries to return (default None = all)

    Returns:
        List of (IndexEntry, RelevanceScore) tuples sorted by score descending
    """
    scored = [
        (entry, score_relevance("hook", prompt_keywords, entry, threshold=threshold))
        for entry in candidates
    ]
    relevant = [(entry, score) for entry, score in scored if score.is_relevant]
    ranked = sorted(relevant, key=lambda x: x[1].score, reverse=True)
    return ranked[:max_entries] if max_entries else ranked


def _capitalize_heading(text: str) -> str:
    """Capitalize heading text: normal words capitalized, all-caps preserved."""
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
