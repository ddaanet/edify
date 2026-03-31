"""Validate learnings.md identifier syntax and uniqueness.

Checks:
- Title format: ## Title (markdown header)
- Max word count per title (default: 7)
- No duplicate titles
- No empty titles
"""

import re
from pathlib import Path

MAX_WORDS = 7
TITLE_PATTERN = re.compile(r"^## (.+)$")


def _find_preamble_end(lines: list[str]) -> int:
    """Find the 1-based line number where preamble ends.

    Preamble boundary is the first ``---`` (horizontal rule) or first ``## ``
    heading, whichever comes first. ``---`` is included in the preamble;
    a ``## `` heading is content (preamble ends at the line before it).

    Returns:
        1-based line number of last preamble line. 0 if file starts with
        a ``## `` heading. ``len(lines)`` if no boundary found.
    """
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "---":
            return i
        if TITLE_PATTERN.match(stripped):
            return i - 1
    return len(lines)


def extract_titles(lines: list[str]) -> list[tuple[int, str]]:
    """Extract (line_number, title_text) pairs from learning titles.

    Args:
        lines: List of file lines.

    Returns:
        List of (line_number, title_text) tuples, skipping preamble.
    """
    preamble_end = _find_preamble_end(lines)
    titles = []
    for i, line in enumerate(lines, 1):
        if i <= preamble_end:
            continue
        stripped = line.strip()
        m = TITLE_PATTERN.match(stripped)
        if m:
            titles.append((i, m.group(1)))
    return titles


def parse_segments(content: str) -> dict[str, list[str]]:
    """Parse learnings.md into segments keyed by heading text.

    Args:
        content: Raw file content as string.

    Returns:
        Ordered dict mapping heading text (or empty string for preamble) to list of
        body lines. The heading line itself is not included in body lines.
    """
    lines = content.splitlines()
    segments: dict[str, list[str]] = {}
    current_heading = ""
    current_body: list[str] = []

    for line in lines:
        m = TITLE_PATTERN.match(line)
        if m:
            if current_heading or current_body:
                segments[current_heading] = current_body
            current_heading = m.group(1)
            current_body = []
        else:
            current_body.append(line)

    if current_heading or current_body:
        segments[current_heading] = current_body

    return segments


def _detect_orphaned_content(lines: list[str]) -> list[str]:
    """Find non-blank lines after preamble but before first ## heading."""
    preamble_end = _find_preamble_end(lines)
    errors: list[str] = []
    first_heading_line = None
    for i, line in enumerate(lines, 1):
        if i <= preamble_end:
            continue
        if TITLE_PATTERN.match(line.strip()):
            first_heading_line = i
            break

    if first_heading_line is None:
        return errors

    for i in range(preamble_end + 1, first_heading_line):
        stripped = lines[i - 1].strip()
        if stripped:
            errors.append(
                f"  line {i}: orphaned content (not under a ## heading): {stripped}"
            )
    return errors


def validate(path: Path, root: Path, max_words: int = MAX_WORDS) -> list[str]:
    """Validate learnings file. Returns list of error strings.

    Args:
        path: Path to learnings file (relative to root).
        root: Project root directory.
        max_words: Maximum allowed words in a title (default: 7).

    Returns:
        List of error messages. Empty list if no errors found.
    """
    full_path = root / path
    try:
        with full_path.open() as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    titles = extract_titles(lines)
    errors = []
    seen: dict[str, int] = {}

    for lineno, title in titles:
        words = title.split()

        # Prefix check: title must start with When or How to
        if not (title.startswith(("When ", "How to "))):
            errors.append(
                f"  line {lineno}: prefix required — title must start with "
                f"'When ' or 'How to ': ## {title}"
            )
        else:
            # Content word count check: min 2 words after prefix
            content_words = words[2:] if title.startswith("How to ") else words[1:]
            if len(content_words) < 2:
                errors.append(
                    f"  line {lineno}: insufficient content words — need at least 2 "
                    f"content words after prefix: ## {title}"
                )

        # Word count check
        if len(words) > max_words:
            errors.append(
                f"  line {lineno}: title has {len(words)} words (max {max_words}): "
                f"## {title}"
            )

        key = title.lower()
        if key in seen:
            errors.append(
                f"  line {lineno}: duplicate title (first at line {seen[key]}): "
                f"## {title}"
            )
        else:
            seen[key] = lineno

    errors.extend(_detect_orphaned_content(lines))
    return errors
