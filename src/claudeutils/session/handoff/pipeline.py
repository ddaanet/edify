"""Handoff pipeline: session.md mutation operations."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

_STATE_FILE = Path("tmp") / ".handoff-state.json"


@dataclass
class HandoffState:
    """Persisted handoff pipeline state for crash recovery."""

    input_markdown: str
    timestamp: str
    step_reached: str = "write_session"


def save_state(input_md: str, step_reached: str = "write_session") -> None:
    """Write HandoffState to tmp/.handoff-state.json.

    Args:
        input_md: Raw handoff stdin markdown.
        step_reached: Pipeline step reached for crash recovery.
    """
    _STATE_FILE.parent.mkdir(exist_ok=True)
    state = HandoffState(
        input_markdown=input_md,
        timestamp=datetime.now(tz=UTC).isoformat(),
        step_reached=step_reached,
    )
    _STATE_FILE.write_text(json.dumps(asdict(state)))


def load_state() -> HandoffState | None:
    """Load HandoffState from tmp/.handoff-state.json.

    Returns:
        HandoffState if the file exists, None otherwise.
    """
    if not _STATE_FILE.exists():
        return None
    data = json.loads(_STATE_FILE.read_text())
    known_fields = HandoffState.__dataclass_fields__.keys()
    filtered_data = {k: v for k, v in data.items() if k in known_fields}
    return HandoffState(**filtered_data)


def clear_state() -> None:
    """Delete the state file; no-op if absent."""
    _STATE_FILE.unlink(missing_ok=True)


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

    def replacement_func(m: re.Match[str]) -> str:
        return m.group(1) + "\n**Status:** " + status_text + "\n" + m.group(3)

    new_text, count = pattern.subn(replacement_func, text, count=1)

    if count == 0:
        msg = f"Could not find Session Handoff heading in {session_path}"
        raise ValueError(msg)

    session_path.write_text(new_text)


def _find_repo_root(path: Path) -> Path:
    """Walk up from path to find directory containing .git.

    Args:
        path: Starting path (file or directory).

    Returns:
        Path to repo root.

    Raises:
        ValueError: If .git not found.
    """
    current = path if path.is_dir() else path.parent
    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            msg = f"Could not find .git from {path}"
            raise ValueError(msg)
        current = current.parent


def _extract_completed_section(text: str) -> str:
    """Extract lines between ## Completed This Session and next ## heading.

    Args:
        text: Full session.md content.

    Returns:
        Section content (without the ## heading).
    """
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
        return ""

    if end_idx is None:
        end_idx = len(lines)

    return "".join(lines[start_idx:end_idx]).strip("\n")


def _detect_write_mode(session_path: Path) -> tuple[str, str]:
    """Detect completed section write mode from git diff.

    Returns:
        Tuple of (mode, committed_section). Mode is ``"overwrite"``,
        ``"append"``, or ``"autostrip"``. committed_section is the
        extracted text from HEAD (empty when git is unavailable).
    """
    try:
        repo_root = _find_repo_root(session_path)
    except ValueError:
        return ("overwrite", "")

    rel_path = session_path.relative_to(repo_root)

    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        committed_completed = _extract_completed_section(result.stdout)
    except subprocess.CalledProcessError:
        return ("overwrite", "")

    current_completed = _extract_completed_section(session_path.read_text())

    if committed_completed == current_completed:
        return ("overwrite", committed_completed)

    committed_lines = {
        line.rstrip() for line in committed_completed.splitlines() if line.strip()
    }
    current_lines = [
        line.rstrip() for line in current_completed.splitlines() if line.strip()
    ]

    if committed_lines and committed_lines.issubset(set(current_lines)):
        return ("autostrip", committed_completed)

    return ("append", committed_completed)


def write_completed(session_path: Path, new_lines: list[str]) -> None:
    """Write new_lines to the ## Completed This Session section of session.md.

    Detects committed state to handle three modes:
    - overwrite: No diff from HEAD → replace section
    - append: Old removed, new present → add to new
    - autostrip: Old preserved with additions → replace section

    Args:
        session_path: Path to session.md file.
        new_lines: Lines to write into the completed section.
    """
    mode, committed_section = _detect_write_mode(session_path)
    if mode == "overwrite":
        _write_completed_section(session_path, new_lines)
    elif mode == "append":
        current = _extract_completed_section(session_path.read_text())
        current_lines = list(current.splitlines())
        combined = current_lines + new_lines
        _write_completed_section(session_path, combined)
    elif mode == "autostrip":
        committed_set = {
            line.strip() for line in committed_section.splitlines() if line.strip()
        }
        current_section = _extract_completed_section(session_path.read_text())
        uncommitted = [
            line
            for line in current_section.splitlines()
            if not line.strip() or line.strip() not in committed_set
        ]
        combined = uncommitted + new_lines
        _write_completed_section(session_path, combined)


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
