"""Handoff pipeline: session.md mutation operations."""

from __future__ import annotations

import re
from pathlib import Path


def overwrite_status(session_path: Path, status_text: str) -> None:
    """Replace the **Status:** line in session.md.

    Finds the region between the ``# Session Handoff:`` heading and the first
    ``## `` section heading, replaces it with ``**Status:** {status_text}``,
    preserving a blank line before the next section.

    Args:
        session_path: Path to session.md file.
        status_text: New status text (single line).
    """
    text = session_path.read_text()

    # Match region from after "# Session Handoff:" line to first "## " heading
    # Capture: preamble (heading line + newline), region, rest-from-##
    pattern = re.compile(
        r"(# Session Handoff:[^\n]*\n)"  # group 1: heading line
        r"(.*?)"  # group 2: region to replace
        r"(\n## )",  # group 3: next section start
        re.DOTALL,
    )

    replacement = r"\g<1>\n**Status:** " + status_text + r"\n\g<3>"
    new_text, count = pattern.subn(replacement, text, count=1)

    if count == 0:
        msg = f"Could not find Session Handoff heading in {session_path}"
        raise ValueError(msg)

    session_path.write_text(new_text)


def write_completed(session_path: Path, new_lines: list[str]) -> None:
    """Write new_lines to the ## Completed This Session section of session.md.

    All three committed-detection modes (overwrite, append, auto-strip) result
    in writing new_lines and discarding prior section content — handled
    uniformly by _write_completed_section.

    Args:
        session_path: Path to session.md file.
        new_lines: Lines to write into the completed section.
    """
    _write_completed_section(session_path, new_lines)


def _write_completed_section(session_path: Path, new_lines: list[str]) -> None:
    """Replace ## Completed This Session content with new_lines."""
    text = session_path.read_text()
    lines = text.splitlines(keepends=True)

    start_idx: int | None = None
    end_idx: int | None = None
    for i, line in enumerate(lines):
        if line.strip() == "## Completed This Session":
            start_idx = i + 1
        elif start_idx is not None and line.startswith("## "):
            end_idx = i
            break

    if start_idx is None:
        msg = f"## Completed This Session not found in {session_path}"
        raise ValueError(msg)

    if end_idx is None:
        end_idx = len(lines)

    # Build replacement: blank line, new_lines, blank line before next section
    replacement = ["\n"] + [line + "\n" for line in new_lines] + ["\n"]
    new_lines_list = lines[:start_idx] + replacement + lines[end_idx:]
    session_path.write_text("".join(new_lines_list))
