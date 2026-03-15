"""Session.md parser — shared by handoff and status subcommands.

Composes existing functions from worktree/session.py and
validation/task_parsing.py rather than reimplementing parsing logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from claudeutils.validation.task_parsing import ParsedTask, parse_task_line
from claudeutils.worktree.session import (
    _extract_plan_from_block,
    extract_task_blocks,
    find_section_bounds,
)

__all__ = [
    "ParsedTask",
    "SessionData",
    "SessionFileError",
    "parse_completed_section",
    "parse_session",
    "parse_status_line",
    "parse_tasks",
]


class SessionFileError(Exception):
    """Raised when session.md cannot be read."""


@dataclass
class SessionData:
    """Structured representation of a parsed session.md file."""

    date: str | None
    status_line: str | None
    completed: list[str]
    in_tree_tasks: list[ParsedTask]
    worktree_tasks: list[ParsedTask] = field(default_factory=list)


def parse_status_line(content: str) -> str | None:
    """Extract status text between ``# Session Handoff:`` and first ``## ``.

    Returns None if no ``# Session Handoff:`` heading found.
    """
    lines = content.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# Session Handoff:"):
            start_idx = i + 1
            break
    if start_idx is None:
        return None

    collected: list[str] = []
    for line in lines[start_idx:]:
        if line.startswith("## "):
            break
        collected.append(line)

    text = "\n".join(collected).strip()
    return text or None


def parse_completed_section(content: str) -> list[str]:
    """Extract lines under ``## Completed This Session``.

    Returns list of non-empty lines. Empty list if section missing or empty.
    """
    bounds = find_section_bounds(content, "Completed This Session")
    if bounds is None:
        return []

    lines = content.split("\n")
    section_lines = lines[bounds[0] + 1 : bounds[1]]
    return [line for line in section_lines if line.strip()]


def parse_tasks(content: str, section: str = "In-tree Tasks") -> list[ParsedTask]:
    """Parse task items from a named section of session.md.

    Composes ``extract_task_blocks`` → ``parse_task_line`` → extend with ``plan_dir``.
    Section name parameter makes in-tree and worktree parsing identical.

    Returns list of ParsedTask with ``plan_dir`` populated from continuation lines.
    """
    blocks = extract_task_blocks(content, section=section)
    tasks: list[ParsedTask] = []

    for block in blocks:
        parsed = parse_task_line(block.lines[0])
        if parsed is None:
            continue

        # Extend with plan_dir from continuation lines
        plan_dir = _extract_plan_from_block(block)
        # Strip status suffix from plan_dir (e.g., "parser" not "parser |")
        if plan_dir:
            plan_dir = re.sub(r"\s*\|.*$", "", plan_dir)
        parsed.plan_dir = plan_dir

        tasks.append(parsed)

    return tasks


def _extract_date(content: str) -> str | None:
    """Extract date from ``# Session Handoff: YYYY-MM-DD`` header."""
    m = re.search(r"^# Session Handoff:\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
    return m.group(1) if m else None


def parse_session(path: Path) -> SessionData:
    """Parse a session.md file into structured data.

    Args:
        path: Path to session.md file.

    Returns:
        SessionData with all sections parsed.

    Raises:
        SessionFileError: If file does not exist or cannot be read.
    """
    try:
        content = path.read_text()
    except FileNotFoundError:
        msg = f"Session file not found: {path}"
        raise SessionFileError(msg) from None
    except OSError as e:
        msg = f"Cannot read session file: {e}"
        raise SessionFileError(msg) from None

    return SessionData(
        date=_extract_date(content),
        status_line=parse_status_line(content),
        completed=parse_completed_section(content),
        in_tree_tasks=parse_tasks(content, section="In-tree Tasks"),
        worktree_tasks=parse_tasks(content, section="Worktree Tasks"),
    )
