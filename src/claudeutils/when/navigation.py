"""Markdown heading hierarchy extraction."""

from dataclasses import dataclass

from claudeutils.when.fuzzy import score_match
from claudeutils.when.index_parser import WhenEntry


@dataclass
class HeadingInfo:
    """Information about a markdown heading."""

    text: str
    level: int
    parent: str | None
    line_number: int
    is_structural: bool = False


def extract_heading_hierarchy(content: str) -> dict[str, HeadingInfo]:
    """Extract heading hierarchy from markdown content.

    Args:
        content: Markdown text content

    Returns:
        Dict mapping heading text to HeadingInfo with parent, level, and line info
    """
    hierarchy: dict[str, HeadingInfo] = {}
    stack: list[tuple[int, str]] = []  # (level, heading_text)

    for line_num, line in enumerate(content.split("\n"), start=1):
        stripped = line.lstrip()

        if not stripped.startswith("#"):
            continue

        heading_text = stripped.lstrip("#").strip()
        level = len(stripped) - len(stripped.lstrip("#"))
        is_structural = heading_text.startswith(".")

        while stack and stack[-1][0] >= level:
            stack.pop()

        parent = stack[-1][1] if stack else None
        hierarchy[heading_text] = HeadingInfo(
            text=heading_text,
            level=level,
            parent=parent,
            line_number=line_num,
            is_structural=is_structural,
        )
        stack.append((level, heading_text))

    return hierarchy


def compute_ancestors(heading: str, file_path: str, file_content: str) -> list[str]:
    """Compute ancestor links for a heading.

    Args:
        heading: Target heading text
        file_path: Path to the markdown file
        file_content: Markdown content

    Returns:
        List of ancestor links in format `/when .SectionTitle` for headings,
        plus `/when ..filename.md` as final link
    """
    hierarchy = extract_heading_hierarchy(file_content)

    if heading not in hierarchy:
        return []

    ancestors: list[str] = []
    current = hierarchy[heading]

    # Walk up and collect ancestor chain
    ancestor_chain: list[str] = []
    while current.parent is not None:
        ancestor_chain.append(current.parent)
        current = hierarchy[current.parent]

    # Reverse to get top-down order
    ancestors = [f"/when .{name}" for name in reversed(ancestor_chain)]
    ancestors.append(f"/when ..{file_path}")
    return ancestors


def _map_entries_to_headings(
    entries: list[WhenEntry], hierarchy: dict[str, HeadingInfo]
) -> dict[str, str]:
    """Map entry triggers to their best-matching headings via fuzzy scoring.

    Args:
        entries: List of WhenEntry objects
        hierarchy: Heading hierarchy dict from extract_heading_hierarchy

    Returns:
        Dict mapping trigger text to heading text
    """
    entry_to_heading: dict[str, str] = {}
    for entry in entries:
        best_match = None
        best_score = 0.0
        for heading_text in hierarchy:
            score = score_match(entry.trigger, heading_text)
            if score > best_score:
                best_score = score
                best_match = heading_text

        if best_match:
            entry_to_heading[entry.trigger] = best_match

    return entry_to_heading


def compute_siblings(
    heading: str, file_content: str, entries: list[WhenEntry]
) -> list[str]:
    """Compute sibling links (entries under same parent heading).

    Structural headings (. prefix) are excluded from sibling grouping as they
    are containers, not content sections.

    Args:
        heading: Target heading text
        file_content: Markdown content
        entries: List of WhenEntry objects from index

    Returns:
        List of sibling trigger links (other entries with same parent)
    """
    hierarchy = extract_heading_hierarchy(file_content)

    if heading not in hierarchy:
        return []

    target = hierarchy[heading]
    parent = target.parent

    if parent is None:
        return []

    # If parent is structural, no sibling grouping
    if hierarchy[parent].is_structural:
        return []

    # Map entries to their headings
    entry_to_heading = _map_entries_to_headings(entries, hierarchy)

    # Find entries with matching parent, excluding target
    siblings = []
    for entry in entries:
        entry_heading = entry_to_heading.get(entry.trigger)
        if not entry_heading:
            continue

        if entry_heading == heading:
            continue

        entry_heading_info = hierarchy.get(entry_heading)
        if not entry_heading_info:
            continue

        if entry_heading_info.parent == parent and not entry_heading_info.is_structural:
            siblings.append(f"/when {entry.trigger}")

    return siblings


def format_navigation(ancestors: list[str], siblings: list[str]) -> str:
    """Format ancestor and sibling links as navigation output.

    Args:
        ancestors: List of ancestor links
        siblings: List of sibling links

    Returns:
        Formatted navigation string with "Broader:" and "Related:" sections,
        omitting empty sections. Returns empty string if both lists are empty.
    """
    sections = []

    if ancestors:
        sections.append("Broader:\n" + "\n".join(ancestors))

    if siblings:
        sections.append("Related:\n" + "\n".join(siblings))

    return "\n\n".join(sections)
