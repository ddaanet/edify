"""Parse /when and /how format entries from index files."""

from pathlib import Path

from pydantic import BaseModel


class WhenEntry(BaseModel):
    """Entry parsed from /when or /how index format."""

    operator: str
    trigger: str
    extra_triggers: list[str]
    line_number: int
    section: str


def parse_index(index_path: Path) -> list[WhenEntry]:
    """Parse index file for /when and /how format entries.

    Format: /when trigger text | extra1, extra2
    Track current H2 section as context for each entry.
    """
    content = index_path.read_text()
    lines = content.split("\n")
    entries = []
    current_section = ""

    for line_num, line in enumerate(lines, 1):
        # Track H2 section headings
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue

        # Parse /when and /how lines
        if line.startswith(("/when ", "/how ")):
            operator, rest = line.split(" ", 1)
            operator = operator[1:]  # Remove leading /

            # Split on first pipe for trigger and extras
            if "|" in rest:
                trigger, extras_str = rest.split("|", 1)
                trigger = trigger.strip()
                # Split on comma, strip each, filter out empty segments
                extra_triggers = [e.strip() for e in extras_str.split(",") if e.strip()]
            else:
                trigger = rest.strip()
                extra_triggers = []

            entry = WhenEntry(
                operator=operator,
                trigger=trigger,
                extra_triggers=extra_triggers,
                line_number=line_num,
                section=current_section,
            )
            entries.append(entry)

    return entries
