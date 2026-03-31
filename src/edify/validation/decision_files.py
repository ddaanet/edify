"""Validate decision file structure.

Detects sections with no direct content (only sub-headings).
Such sections must be marked structural with '.' prefix.

Hard error - no autofix. Agent decides:
- Add '.' prefix → organizational grouping
- Add substantive content → knowledge section
"""

import re
from pathlib import Path

# Minimum substantive lines before first sub-heading to be considered "knowledge"
CONTENT_THRESHOLD = 2

DECISION_GLOBS = [
    "agents/decisions/*.md",
]


def parse_heading(line: str) -> tuple[int, str, bool] | None:
    """Parse a heading line.

    Args:
        line: A line from the file.

    Returns:
        Tuple of (level, title, is_structural) or None if not a heading.
        is_structural is True if title starts with '.'.
    """
    match = re.match(r"^(#{2,6}) (.+)$", line.strip())
    if not match:
        return None
    level = len(match.group(1))
    title = match.group(2)
    is_structural = title.startswith(".")
    return level, title, is_structural


def count_substantive_content(
    content_lines: list[str], first_subheading_idx: int
) -> int:
    """Count substantive lines before first sub-heading.

    Args:
        content_lines: Lines of content in the section.
        first_subheading_idx: Index of first sub-heading.

    Returns:
        Number of substantive lines (non-empty, non-comment).
    """
    before_subheading = content_lines[:first_subheading_idx]
    substantive = [
        line
        for line in before_subheading
        if line.strip() and not line.strip().startswith("<!--")
    ]
    return len(substantive)


def collect_section_content(
    lines: list[str], start_idx: int, level: int
) -> tuple[list[str], int | None, int]:
    """Collect content lines until next heading at same or higher level.

    Args:
        lines: All lines in the file.
        start_idx: Index to start collecting from.
        level: Level of the current section heading.

    Returns:
        Tuple of (content_lines, first_subheading_idx, end_idx).
        content_lines: Lines in the section.
        first_subheading_idx: Index of first sub-heading, or None if no sub-headings.
        end_idx: Index where collection stopped.
    """
    content_lines: list[str] = []
    first_subheading_idx: int | None = None
    i = start_idx
    n = len(lines)

    while i < n:
        next_parsed = parse_heading(lines[i])
        if next_parsed:
            next_level = next_parsed[0]
            # Same or higher level = end of this section
            if next_level <= level:
                break
            # Sub-heading found
            if first_subheading_idx is None:
                first_subheading_idx = len(content_lines)
        content_lines.append(lines[i])
        i += 1

    return content_lines, first_subheading_idx, i


def analyze_file(filepath: Path) -> list[tuple[int, str, int]]:
    """Analyze a file for organizational sections missing structural marker.

    Args:
        filepath: Path to the file to analyze.

    Returns:
        List of (line_number, heading_title, level) for violations.
    """
    try:
        lines = filepath.read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    violations = []
    i = 0
    n = len(lines)

    while i < n:
        parsed = parse_heading(lines[i])
        if not parsed:
            i += 1
            continue

        level, title, is_structural = parsed
        heading_line = i + 1  # 1-indexed for error messages
        i += 1

        # Already structural - skip
        if is_structural:
            continue

        # Collect content until next heading at same or higher level
        content_lines, first_subheading_idx, i = collect_section_content(
            lines, i, level
        )

        # No sub-headings = not organizational (all content is direct)
        if first_subheading_idx is None:
            continue

        # Organizational if few substantive lines before sub-heading
        substantive_count = count_substantive_content(
            content_lines, first_subheading_idx
        )
        if substantive_count <= CONTENT_THRESHOLD:
            violations.append((heading_line, title, level))

    return violations


def validate(root: Path) -> list[str]:
    """Validate all decision files.

    Args:
        root: Project root directory.

    Returns:
        List of error messages. Empty list if no errors found.
    """
    errors = []

    for glob_pattern in DECISION_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            rel = filepath.relative_to(root)
            violations = analyze_file(filepath)

            for lineno, title, level in violations:
                hashes = "#" * level
                errors.append(
                    f"  {rel}:{lineno}: section '{title}' has no direct content\n"
                    f"    Action required:\n"
                    f"    A) Mark structural: '{hashes} .{title}'\n"
                    f"    B) Add substantive content before sub-headings"
                )

    return errors
