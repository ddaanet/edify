"""Tests for session handoff pipeline (Phase 4)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from claudeutils.session.handoff.context import PrecommitResult, format_diagnostics
from claudeutils.session.handoff.parse import (
    HandoffInput,
    HandoffInputError,
    parse_handoff_input,
)
from claudeutils.session.handoff.pipeline import (
    HandoffState,
    clear_state,
    load_state,
    overwrite_status,
    save_state,
    write_completed,
)

HANDOFF_INPUT_FIXTURE = """\
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent
"""


# Cycle 4.1: parse handoff stdin


def test_parse_handoff_input() -> None:
    """Valid input returns HandoffInput with status and completed."""
    result = parse_handoff_input(HANDOFF_INPUT_FIXTURE)
    assert isinstance(result, HandoffInput)
    assert result.status_line == "Design Phase A complete — outline reviewed."
    assert len(result.completed_lines) > 0
    assert any("Produced outline" in line for line in result.completed_lines)


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


def _init_repo(path: Path) -> None:
    """Initialize a minimal git repo for testing write_completed."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=path,
        check=True,
        capture_output=True,
    )


def _commit_session(path: Path, session_file: Path) -> None:
    """Stage and commit session.md in the test repo."""
    subprocess.run(
        ["git", "add", str(session_file.relative_to(path))],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=path,
        check=True,
        capture_output=True,
    )


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
    """write_completed replaces accumulated prior-session content."""
    session_file = tmp_path / "session.md"
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

    save_state("# input markdown", step="write_session")

    state_file = tmp_path / "tmp" / ".handoff-state.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text())
    assert data["input_markdown"] == "# input markdown"
    assert data["step_reached"] == "write_session"
    assert "timestamp" in data
    # Timestamp is ISO format (contains 'T' separator)
    assert "T" in data["timestamp"]


def test_state_cache_resume(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_state returns HandoffState when state file exists, else None."""
    monkeypatch.chdir(tmp_path)

    # No file yet
    assert load_state() is None

    save_state("# my input", step="precommit")
    result = load_state()

    assert isinstance(result, HandoffState)
    assert result.input_markdown == "# my input"
    assert result.step_reached == "precommit"
    # File survives load (not deleted)
    assert (tmp_path / "tmp" / ".handoff-state.json").exists()


def test_state_cache_cleanup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """clear_state removes the state file; idempotent when already absent."""
    monkeypatch.chdir(tmp_path)

    # Idempotent when no file
    clear_state()

    save_state("# input", step="diagnostics")
    assert load_state() is not None

    clear_state()
    assert load_state() is None
    # No error on second clear
    clear_state()


# Cycle 4.6: diagnostic output


def test_diagnostics_precommit_pass() -> None:
    """format_diagnostics includes precommit output and git info when passed."""
    result = format_diagnostics(
        PrecommitResult(passed=True, output="All checks passed"),
        git_output="M agents/session.md",
        learnings_age_days=None,
    )
    assert "All checks passed" in result
    assert "M agents/session.md" in result
    # No age warning when learnings_age_days is None
    assert "Learnings" not in result

    # Also verify computed-but-young (below threshold) produces no warning
    result_young = format_diagnostics(
        PrecommitResult(passed=True, output="All checks passed"),
        git_output="M agents/session.md",
        learnings_age_days=3,
    )
    assert "Learnings" not in result_young


def test_diagnostics_precommit_fail() -> None:
    """Excludes git output on failure; includes learnings warning when stale."""
    result = format_diagnostics(
        PrecommitResult(passed=False, output="lint failed: E501"),
        git_output="M agents/session.md",
        learnings_age_days=8,
    )
    assert "lint failed: E501" in result
    # Git output excluded on failure
    assert "M agents/session.md" not in result
    # Learnings age warning included when >= 7 days even on failure
    assert "Learnings" in result


def test_diagnostics_learnings_age() -> None:
    """format_diagnostics includes age warning when learnings_age_days >= 7."""
    result = format_diagnostics(
        PrecommitResult(passed=True, output="OK"),
        git_output="nothing to show",
        learnings_age_days=10,
    )
    assert "Learnings" in result
    assert "10" in result
    assert "codify" in result.lower()
