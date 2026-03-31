"""Tests for session handoff pipeline (Phase 4)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from edify.session.handoff.parse import (
    HandoffInput,
    HandoffInputError,
    parse_handoff_input,
)
from edify.session.handoff.pipeline import (
    HandoffState,
    clear_state,
    load_state,
    overwrite_status,
    save_state,
    write_completed,
)
from tests.pytest_helpers import init_repo_at

HANDOFF_INPUT_FIXTURE = """\
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

### Handoff CLI tool design (Phase A)
- Produced outline
- Review by outline-review-agent
"""


# Cycle 4.1: parse handoff stdin


def test_parse_handoff_input() -> None:
    """Valid input returns HandoffInput with status and completed."""
    result = parse_handoff_input(HANDOFF_INPUT_FIXTURE)
    assert isinstance(result, HandoffInput)
    assert result.status_line == "Design Phase A complete — outline reviewed."
    assert any("Produced outline" in line for line in result.completed_lines)
    assert any("### Handoff CLI tool design" in line for line in result.completed_lines)


def test_parse_handoff_missing_status() -> None:
    """Input without Status line raises HandoffInputError."""
    text = """\
## Completed This Session

- Something done
"""
    with pytest.raises(HandoffInputError, match="Status"):
        parse_handoff_input(text)


def test_parse_handoff_missing_completed() -> None:
    """Input without Completed heading raises HandoffInputError."""
    text = """\
**Status:** Done.
"""
    with pytest.raises(HandoffInputError, match="Completed"):
        parse_handoff_input(text)


def test_parse_handoff_preserves_blank_lines() -> None:
    """Parser preserves blank lines in completed section."""
    text = """\
**Status:** Done.

## Completed This Session

### Group A
- Item 1

### Group B
- Item 2
"""
    result = parse_handoff_input(text)
    # Should preserve internal blank line
    assert "" in result.completed_lines
    # Both groups should be present
    assert any("### Group A" in line for line in result.completed_lines)
    assert any("### Group B" in line for line in result.completed_lines)


# Cycle 4.2: status line overwrite

SESSION_FIXTURE = """\
# Session Handoff: 2026-03-15

**Status:** Old status text.

## Completed This Session

- Task A done

## In-tree Tasks

- [ ] **Task B** — `cmd` | sonnet
"""


def test_overwrite_status_line(tmp_path: Path) -> None:
    """overwrite_status replaces the Status line in session.md."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_FIXTURE)

    overwrite_status(session_file, "New status text.")

    content = session_file.read_text()
    assert "**Status:** New status text." in content
    assert "**Status:** Old status text." not in content
    # Other sections preserved
    assert "## Completed This Session" in content
    assert "## In-tree Tasks" in content
    assert "Task A done" in content
    assert "Task B" in content


def test_overwrite_status_line_idempotent(tmp_path: Path) -> None:
    """Subsequent overwrite_status calls replace, not append."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_FIXTURE)

    overwrite_status(session_file, "First update.")
    overwrite_status(session_file, "Second update.")

    content = session_file.read_text()
    assert "**Status:** Second update." in content
    assert "**Status:** First update." not in content
    assert content.count("**Status:**") == 1


def test_overwrite_status_line_multiline(tmp_path: Path) -> None:
    """Preserves multiline status text between heading and first ## section."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_FIXTURE)

    multiline_status = "Line one of status.\nLine two of status."
    overwrite_status(session_file, multiline_status)

    content = session_file.read_text()
    assert "Line one of status." in content
    assert "Line two of status." in content
    # Both lines must appear before the first ## section heading
    heading_pos = content.index("# Session Handoff:")
    first_section_pos = content.index("## ", heading_pos)
    status_region = content[heading_pos:first_section_pos]
    assert "Line one of status." in status_region
    assert "Line two of status." in status_region


def test_overwrite_status_backreference_in_text(tmp_path: Path) -> None:
    r"""Status text with regex backrefs like \g<1> not interpreted."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_FIXTURE)

    status_with_backref = r"Contains \g<1> and \g<3> patterns"
    overwrite_status(session_file, status_with_backref)

    content = session_file.read_text()
    assert r"\g<1>" in content
    assert r"\g<3>" in content


# Cycle 4.3: completed section write with committed detection


SESSION_WITH_COMPLETED = """\
# Session Handoff: 2026-03-15

**Status:** Previous session status.

## Completed This Session

- Old task A
- Old task B

## In-tree Tasks

- [ ] **Task C** — `cmd` | sonnet
"""


def test_write_completed_replaces_section(tmp_path: Path) -> None:
    """write_completed replaces section content with new_lines."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)

    write_completed(session_file, ["- New task done."])

    content = session_file.read_text()
    assert "## Completed This Session" in content
    assert "- New task done." in content
    assert "- Old task A" not in content
    assert "- Old task B" not in content
    # Other sections preserved
    assert "## In-tree Tasks" in content


def test_write_completed_with_empty_section(tmp_path: Path) -> None:
    """write_completed writes new_lines when prior section is empty."""
    session_file = tmp_path / "session.md"
    cleared = SESSION_WITH_COMPLETED.replace("- Old task A\n- Old task B\n", "")
    session_file.write_text(cleared)

    write_completed(session_file, ["- New task done."])

    content = session_file.read_text()
    assert "- New task done." in content
    assert "- Old task A" not in content
    assert "- Old task B" not in content


def test_write_completed_with_accumulated_content(tmp_path: Path) -> None:
    """Autostrip removes committed content, keeps new additions."""
    init_repo_at(tmp_path)
    session_file = tmp_path / "session.md"
    # Commit original completed content
    session_file.write_text(SESSION_WITH_COMPLETED)
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "session.md"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "add session"],
        capture_output=True,
        check=True,
    )
    # Accumulate new content alongside committed content
    accumulated = SESSION_WITH_COMPLETED.replace(
        "- Old task B\n",
        "- Old task B\n- New task done.\n",
    )
    session_file.write_text(accumulated)

    write_completed(session_file, ["- New task done."])

    content = session_file.read_text()
    assert "- New task done." in content
    assert "- Old task A" not in content
    assert "- Old task B" not in content


# Cycle 4.4: state caching


def test_state_cache_create(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """save_state creates tmp/.handoff-state.json with required fields."""
    monkeypatch.chdir(tmp_path)

    save_state("# input markdown")

    state_file = tmp_path / "tmp" / ".handoff-state.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text())
    assert data["input_markdown"] == "# input markdown"
    assert "timestamp" in data
    # Timestamp is ISO format (contains 'T' separator)
    assert "T" in data["timestamp"]


def test_state_cache_resume(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_state returns HandoffState when state file exists, else None."""
    monkeypatch.chdir(tmp_path)

    # No file yet
    assert load_state() is None

    save_state("# my input")
    result = load_state()

    assert isinstance(result, HandoffState)
    assert result.input_markdown == "# my input"
    # File survives load (not deleted)
    assert (tmp_path / "tmp" / ".handoff-state.json").exists()


def test_state_cache_cleanup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """clear_state removes the state file; idempotent when already absent."""
    monkeypatch.chdir(tmp_path)

    # Idempotent when no file
    clear_state()

    save_state("# input")
    assert load_state() is not None

    clear_state()
    assert load_state() is None
    # No error on second clear
    clear_state()


def test_save_state_includes_step_reached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """save_state writes step_reached to state file."""
    monkeypatch.chdir(tmp_path)

    save_state("# input", step_reached="write_session")

    state_file = tmp_path / "tmp" / ".handoff-state.json"
    data = json.loads(state_file.read_text())
    assert data["step_reached"] == "write_session"


def test_load_state_backward_compat_missing_step_reached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """load_state defaults step_reached when missing."""
    monkeypatch.chdir(tmp_path)

    tmp_path.joinpath("tmp").mkdir(exist_ok=True)
    state_file = tmp_path / "tmp" / ".handoff-state.json"
    state_file.write_text(
        json.dumps(
            {
                "input_markdown": "# test",
                "timestamp": "2026-03-25T12:00:00+00:00",
            }
        )
    )

    state = load_state()
    assert state is not None
    assert state.step_reached == "write_session"
