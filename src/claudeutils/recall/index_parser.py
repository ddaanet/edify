"""Parse memory-index.md into structured entries."""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Common stopwords to exclude from keywords
STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "can",
    "for",
    "from",
    "to",
    "at",
    "in",
    "by",
    "on",
    "with",
    "as",
    "if",
    "and",
    "or",
    "not",
    "this",
    "that",
    "it",
    "its",
    "my",
    "your",
    "our",
    "their",
    "of",
}


class IndexEntry(BaseModel):
    """Parsed entry from memory-index.md."""

    key: str  # Text before em-dash
    description: str  # Text after em-dash
    referenced_file: str  # From parent H2 heading (file path)
    section: str  # Parent H2 heading text
    keywords: set[str]  # Extracted from key + description


def _extract_keywords(text: str) -> set[str]:
    """Extract keywords from text.

    Tokenizes on whitespace and punctuation, lowercases, removes stopwords.

    Args:
        text: Text to tokenize

    Returns:
        Set of keywords
    """
    # Split on whitespace and punctuation
    tokens = re.split(r"[\s\-_.,;:()[\]{}\"'`]+", text.lower())

    # Remove empty strings and stopwords
    return {token for token in tokens if token and token not in STOPWORDS}


def _parse_new_format_line(
    line: str, current_file: str, current_section: str
) -> IndexEntry | None:
    """Parse a /when or /how format line."""
    prefix_end = line.find(" ")
    trigger_start = prefix_end + 1
    pipe_idx = line.find(" | ")

    if pipe_idx != -1:
        trigger = line[trigger_start:pipe_idx].strip()
        extras = line[pipe_idx + 3 :].strip()
    else:
        trigger = line[trigger_start:].strip()
        extras = ""

    if not trigger:
        return None

    return IndexEntry(
        key=trigger,
        description="",
        referenced_file=current_file,
        section=current_section,
        keywords=_extract_keywords(trigger + " " + extras),
    )


def _parse_old_format_line(
    line: str, current_file: str, current_section: str
) -> IndexEntry | None:
    """Parse an old-format (key — description) line."""
    if " — " not in line:
        return None

    parts = line.split(" — ", 1)
    if len(parts) != 2:
        return None

    key = parts[0].strip()
    description = parts[1].strip()
    if not key or not description:
        return None

    return IndexEntry(
        key=key,
        description=description,
        referenced_file=current_file,
        section=current_section,
        keywords=_extract_keywords(key + " " + description),
    )


def parse_memory_index(index_file: Path) -> list[IndexEntry]:
    """Parse memory-index.md into structured entries.

    Extracts H2 sections (file paths) and entries in two formats:
    - New format: `/when trigger | extra keywords` or `/how trigger | extra keywords`
    - Old format: `key — description` (deprecated but still supported)

    Skips special sections that don't map to clear Read targets:
    - "Behavioral Rules (fragments — already loaded)"
    - "Technical Decisions (mixed — check entry for specific file)"
    """
    try:
        content = index_file.read_text()
    except OSError as e:
        logger.warning("Failed to read %s: %s", index_file, e)
        return []

    entries: list[IndexEntry] = []
    current_section = ""
    current_file = ""
    skip_section = False

    for line in content.split("\n"):
        if line.startswith("## "):
            current_section = line[3:].strip()
            if current_section.startswith(
                ("Behavioral Rules", "Technical Decisions")
            ):
                skip_section = True
                current_file = ""
            else:
                skip_section = False
                current_file = current_section
            continue

        if skip_section or not line.strip() or not current_file:
            continue

        if line.startswith(("/when ", "/how ")):
            entry = _parse_new_format_line(line, current_file, current_section)
        else:
            entry = _parse_old_format_line(line, current_file, current_section)

        if entry:
            entries.append(entry)

    return entries
