"""Parse handoff stdin input into structured data."""

from __future__ import annotations

import re
from dataclasses import dataclass


class HandoffInputError(Exception):
    """Raised when handoff stdin is missing required markers."""


@dataclass
class HandoffInput:
    """Structured representation of handoff stdin."""

    status_line: str
    completed_lines: list[str]


def parse_handoff_input(text: str) -> HandoffInput:
    """Parse handoff stdin text into HandoffInput.

    Requires ``**Status:**`` line and ``## Completed This Session`` heading.

    Raises:
        HandoffInputError: If required markers are missing.
    """
    # Extract status line
    m = re.search(r"^\*\*Status:\*\*\s*(.+)", text, re.MULTILINE)
    if not m:
        msg = "Missing **Status:** line in handoff input"
        raise HandoffInputError(msg)
    status_line = m.group(1).strip()

    # Extract completed section
    lines = text.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## Completed This Session":
            start_idx = i + 1
            break

    if start_idx is None:
        msg = "Missing ## Completed This Session heading in handoff input"
        raise HandoffInputError(msg)

    completed: list[str] = []
    for line in lines[start_idx:]:
        if line.startswith("## "):
            break
        completed.append(line)

    while completed and not completed[-1].strip():
        completed.pop()

    return HandoffInput(status_line=status_line, completed_lines=completed)
