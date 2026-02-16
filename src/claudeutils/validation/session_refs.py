"""Reject tmp/ file references in session tracking files.

Session files (session.md, learnings.md, jobs.md) document persistent
state across sessions. References to tmp/ paths are ephemeral
(gitignored) and break when sessions restart.

Checks:
- No tmp/ path references in session tracking files
"""

import re
from pathlib import Path

# tmp/ followed by alphanumeric start + path characters
# Requires letter/digit after slash to avoid matching sentence-ending "tmp/."
TMP_REF_PATTERN = re.compile(r"\btmp/[a-zA-Z0-9][a-zA-Z0-9._/\-]*")

SESSION_FILES = [
    "agents/session.md",
    "agents/learnings.md",
    "agents/jobs.md",
]


def check_tmp_references(lines: list[str]) -> list[tuple[int, str]]:
    """Find tmp/ path references in file lines.

    Args:
        lines: File content as list of lines.

    Returns:
        List of (line_number, matched_text) pairs.
    """
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        hits.extend((i, m.group(0)) for m in TMP_REF_PATTERN.finditer(line))
    return hits


def validate(root: Path) -> list[str]:
    """Validate session tracking files for tmp/ references.

    Args:
        root: Project root directory.

    Returns:
        List of error strings. Empty if no errors.
    """
    errors = []
    for rel_path in SESSION_FILES:
        full_path = root / rel_path
        if not full_path.exists():
            continue
        with full_path.open() as f:
            lines = f.readlines()
        hits = check_tmp_references(lines)
        for lineno, matched in hits:
            errors.append(f"  {rel_path}:{lineno}: tmp/ reference: {matched}")
    return errors
