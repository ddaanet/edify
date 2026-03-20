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
