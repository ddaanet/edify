"""Compress key functionality for heading corpus loading."""

import re
from itertools import combinations
from pathlib import Path

from claudeutils.when.fuzzy import rank_matches


def load_heading_corpus(decisions_dir: Path) -> list[str]:
    """Load heading corpus from decision files.

    Args:
        decisions_dir: Path to the decisions directory.

    Returns:
        List of heading text strings from H2 and H3 headings, excluding
        structural headings (those starting with a dot).
    """
    headings = []

    # Scan all .md files in the directory
    for file_path in sorted(decisions_dir.glob("*.md")):
        content = file_path.read_text()

        # Extract H2+ headings: ^#{2,}\s+(.+)$
        for match in re.finditer(r"^#{2,}\s+(.+)$", content, re.MULTILINE):
            heading_text = match.group(1)

            # Filter out structural headings (starting with dot)
            if not heading_text.startswith("."):
                headings.append(heading_text)

    return headings


def generate_candidates(heading: str) -> list[str]:
    """Generate candidate triggers from heading via word-drop algorithm.

    Generates all combinations by dropping words from the heading, keeping
    only those with 2+ words. Also generates singularized versions by
    removing trailing 's'. Returns lowercase candidates sorted by length
    (shortest first).

    Args:
        heading: Heading text (e.g., "How to Encode Paths")

    Returns:
        List of candidate triggers, sorted by word count ascending.
    """
    words = heading.lower().split()
    candidates = set()

    # Generate all combinations of words (drop varying word counts)
    for r in range(len(words) - 1, 1, -1):  # r from len-1 down to 2 (keep 2+ words)
        for combo in combinations(range(len(words)), r):
            candidate = " ".join(words[i] for i in combo)
            candidates.add(candidate)

            # Add singularized version (drop trailing 's')
            words_in_combo = [words[i] for i in combo]
            if words_in_combo[-1].endswith("s"):
                singularized_words = [*words_in_combo[:-1], words_in_combo[-1][:-1]]
                if len(singularized_words) >= 2:
                    singularized = " ".join(singularized_words)
                    candidates.add(singularized)

    # Sort by word count (length), then alphabetically for stability
    return sorted(candidates, key=lambda x: (len(x.split()), x))


def verify_unique(trigger: str, corpus: list[str]) -> bool:
    """Verify that a trigger uniquely resolves to one heading in the corpus.

    Uses fuzzy scoring to rank candidates. A trigger is unique if the top
    match's score is significantly higher than the second match's score
    (2x or larger gap).

    Args:
        trigger: The search trigger (index key)
        corpus: List of headings to search against

    Returns:
        True if trigger uniquely resolves to one heading, False otherwise
    """
    if not corpus:
        return False

    ranked = rank_matches(trigger, corpus, limit=2)

    if not ranked:
        return False

    if len(ranked) == 1:
        return True

    top_score = ranked[0][1]
    second_score = ranked[1][1]

    return top_score >= 2 * second_score


def compress_key(heading: str, corpus: list[str]) -> str:
    """Generate minimal unique trigger from heading.

    Generates candidate triggers in order of length (shortest first), tests
    each for uniqueness, and returns the first that uniquely resolves to the
    heading. If no shorter candidate is unique, returns the full heading
    lowercased as fallback.

    Args:
        heading: The heading text (e.g., "How to Encode Paths")
        corpus: List of all headings for uniqueness verification

    Returns:
        Shortest unique trigger string, or full heading lowercased if none found
    """
    candidates = generate_candidates(heading)

    # Linear scan of candidates, shortest first
    for candidate in candidates:
        if verify_unique(candidate, corpus):
            return candidate

    # Fallback: full heading lowercased
    return heading.lower()
