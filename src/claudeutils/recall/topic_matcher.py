"""Topic matching pipeline: index construction, matching, and output formatting."""

from collections import defaultdict

from claudeutils.recall.index_parser import IndexEntry, extract_keywords


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
