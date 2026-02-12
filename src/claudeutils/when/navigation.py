"""Markdown heading hierarchy extraction."""

from dataclasses import dataclass


@dataclass
class HeadingInfo:
    """Information about a markdown heading."""

    text: str
    level: int
    parent: str | None
    line_number: int


def extract_heading_hierarchy(content: str) -> dict[str, HeadingInfo]:
    """Extract heading hierarchy from markdown content.

    Args:
        content: Markdown text content

    Returns:
        Dict mapping heading text to HeadingInfo with parent, level, and line info
    """
    hierarchy: dict[str, HeadingInfo] = {}
    stack: list[tuple[int, str]] = []

    for line_num, line in enumerate(content.split("\n"), start=1):
        stripped = line.lstrip()

        if not stripped.startswith("#"):
            continue

        heading_text = stripped.lstrip("#").strip()
        level = len(stripped) - len(stripped.lstrip("#"))

        while stack and stack[-1][0] >= level:
            stack.pop()

        parent = stack[-1][1] if stack else None
        hierarchy[heading_text] = HeadingInfo(
            text=heading_text, level=level, parent=parent, line_number=line_num
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
