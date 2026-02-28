"""Topic matching pipeline: index construction, matching, and output formatting."""

from collections import defaultdict

from claudeutils.recall.index_parser import IndexEntry


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
