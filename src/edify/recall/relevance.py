"""Score relevance between session topics and index entries."""

from pydantic import BaseModel

from edify.recall.index_parser import IndexEntry


class RelevanceScore(BaseModel):
    """Relevance score result."""

    session_id: str
    entry_key: str
    score: float  # 0.0 to 1.0
    is_relevant: bool  # True if score >= threshold
    matched_keywords: set[str]  # Keywords that matched


def score_relevance(
    session_id: str,
    session_keywords: set[str],
    entry: IndexEntry,
    threshold: float = 0.3,
) -> RelevanceScore:
    """Score relevance between session topics and index entry.

    Uses normalized keyword overlap: |intersection| / |entry keywords|.
    This measures what fraction of the entry's keywords appear in the session.

    Args:
        session_id: Session identifier
        session_keywords: Keywords extracted from session
        entry: Index entry to score against
        threshold: Relevance threshold (default 0.3)

    Returns:
        RelevanceScore with score, is_relevant flag, and matched keywords
    """
    if not entry.keywords:
        # Edge case: entry with no keywords (shouldn't happen with proper parsing)
        score = 0.0
        matched = set()
    else:
        # Calculate keyword overlap
        matched = session_keywords & entry.keywords
        score = len(matched) / len(entry.keywords)

    is_relevant = score >= threshold

    return RelevanceScore(
        session_id=session_id,
        entry_key=entry.key,
        score=score,
        is_relevant=is_relevant,
        matched_keywords=matched,
    )


def find_relevant_entries(
    session_id: str,
    session_keywords: set[str],
    entries: list[IndexEntry],
    threshold: float = 0.3,
) -> list[RelevanceScore]:
    """Find all relevant entries for a session.

    Args:
        session_id: Session identifier
        session_keywords: Keywords extracted from session
        entries: Index entries to score
        threshold: Relevance threshold (default 0.3)

    Returns:
        List of RelevanceScore objects for relevant entries (score >= threshold)
    """
    relevant = []

    for entry in entries:
        score_result = score_relevance(session_id, session_keywords, entry, threshold)
        if score_result.is_relevant:
            relevant.append(score_result)

    # Sort by score descending
    relevant.sort(key=lambda r: r.score, reverse=True)

    return relevant
