"""Shared task-line parsing for session.md consumers.

Single source of truth for parsing task lines. Consolidates
three independent TASK_PATTERN regexes from session_structure.py,
tasks.py, and worktree/session.py (NFR-4).

Format: - [x] **Name** → `slug` — `command` | model | restart | priority
"""

import re
from dataclasses import dataclass, field

# Permissive task-line pattern — matches any single char in checkbox position.
# Validation of the checkbox value is separate (VALID_CHECKBOXES).
TASK_PATTERN = re.compile(r"^- \[(?P<checkbox>.)\] \*\*(?P<name>.+?)\*\*")

# Valid checkbox values
VALID_CHECKBOXES = frozenset({" ", "x", ">", "!", "\u2020", "-"})

# Worktree marker: → `slug` (between name and em dash)
WORKTREE_MARKER_PATTERN = re.compile(r"\u2192 `(?P<slug>[a-z0-9][-a-z0-9]*)`")

# Command: backtick-wrapped text after em dash
COMMAND_PATTERN = re.compile(r"\u2014.*?`(?P<command>[^`]+)`")

# Valid model tiers
VALID_MODELS = frozenset({"haiku", "sonnet", "opus"})


@dataclass
class ParsedTask:
    """Structured representation of a session.md task line."""

    name: str
    checkbox: str  # ' ', 'x', '>', '!', '\u2020' (dagger), '-' (canceled)
    full_line: str
    line_number: int = 0
    command: str | None = None
    model: str | None = None
    worktree_marker: str | None = None
    restart: bool = False
    priority: str | None = field(default=None)


def parse_task_line(line: str, lineno: int = 0) -> ParsedTask | None:
    """Parse a session.md task line into structured fields.

    Args:
        line: Raw line text.
        lineno: Line number in the file (1-based). 0 if unknown.

    Returns:
        ParsedTask if line matches task format, None otherwise.
    """
    m = TASK_PATTERN.match(line.strip())
    if not m:
        return None

    name = m.group("name")
    checkbox = m.group("checkbox")

    # Worktree marker
    wt_match = WORKTREE_MARKER_PATTERN.search(line)
    worktree_marker = wt_match.group("slug") if wt_match else None

    # Command (backtick-wrapped after em dash)
    cmd_match = COMMAND_PATTERN.search(line)
    command = cmd_match.group("command") if cmd_match else None

    # Parse pipe-separated metadata after em dash
    model = None
    restart = False
    priority = None

    # Split on em dash, take everything after
    parts = line.split("—", 1)
    if len(parts) == 2:
        metadata = parts[1]
        # Split on pipe, check each segment
        segments = [s.strip() for s in metadata.split("|")]
        for seg in segments[1:]:  # skip first segment (description/command)
            seg_lower = seg.lower().strip()
            if seg_lower in VALID_MODELS:
                model = seg_lower
            elif seg_lower == "restart":
                restart = True
            elif re.match(r"^\d+(\.\d+)?$", seg_lower):
                priority = seg_lower

    return ParsedTask(
        name=name,
        checkbox=checkbox,
        full_line=line,
        line_number=lineno,
        command=command,
        model=model,
        worktree_marker=worktree_marker,
        restart=restart,
        priority=priority,
    )
