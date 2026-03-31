"""Tests for session handoff CLI wiring (Cycle 4.7 + rework)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.cli import cli
from edify.session.handoff.pipeline import load_state, save_state
from tests.pytest_helpers import (
    add_submodule,
    create_submodule_origin,
    init_repo_minimal,
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


HANDOFF_STDIN = """\
**Status:** Phase 4 complete.

## Completed This Session

- Implemented write_completed
- Wired CLI
"""

SESSION_FOR_CLI = """\
# Session Handoff: 2026-03-15

**Status:** Old status.

## Completed This Session

- Previous task

## In-tree Tasks

- [ ] **Build CLI** — `/runbook plans/cli/r.md` | sonnet
"""


def _setup_cli_repo(tmp_path: Path) -> Path:
    """Create a committed git repo with session.md for CLI tests."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_FOR_CLI)
    init_repo_minimal(tmp_path)
    _commit_session(tmp_path, session_file)
    return session_file


def test_session_handoff_cli_fresh(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fresh handoff updates session.md and outputs git diagnostics."""
    monkeypatch.chdir(tmp_path)
    session_file = _setup_cli_repo(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        input=HANDOFF_STDIN,
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 0
    content = session_file.read_text()
    assert "Phase 4 complete." in content
    assert "Implemented write_completed" in content
    assert "Previous task" not in content
    # Git diagnostics emitted (session.md modified relative to HEAD)
    assert "**Git status:**" in result.output
    # State file cleared after successful pipeline
    assert not (tmp_path / "tmp" / ".handoff-state.json").exists()


def test_session_handoff_cli_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Handoff with existing state file resumes without stdin."""
    monkeypatch.chdir(tmp_path)
    session_file = _setup_cli_repo(tmp_path)
    # Pre-populate state file
    save_state(HANDOFF_STDIN)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 0
    content = session_file.read_text()
    assert "Phase 4 complete." in content
    # State file cleared after successful resume
    assert not (tmp_path / "tmp" / ".handoff-state.json").exists()


def test_session_handoff_cli_no_stdin_no_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Handoff without stdin and no state exits 2 with error."""
    monkeypatch.chdir(tmp_path)
    session_file = _setup_cli_repo(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 2
    assert "**Error:**" in result.output


# Cycle 2.2: handoff shows submodule changes


def test_handoff_shows_submodule_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Handoff output includes dirty submodule changes."""
    parent = tmp_path / "parent"
    parent.mkdir()
    init_repo_minimal(parent)
    (parent / "init.md").write_text("init\n")
    subprocess.run(["git", "add", "."], cwd=parent, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    origin = create_submodule_origin(tmp_path, "plugin")
    add_submodule(parent, origin, "plugin")
    subprocess.run(
        ["git", "commit", "-m", "add sub"],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(parent)

    # Set up session.md in parent
    session_file = parent / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(SESSION_FOR_CLI)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add session"],
        cwd=parent,
        check=True,
        capture_output=True,
    )

    # Dirty the submodule
    (parent / "plugin" / "dirty.md").write_text("new file\n")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        input=HANDOFF_STDIN,
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 0
    # Should include submodule section with internal file changes
    assert "## Submodule: plugin" in result.output
    assert "dirty.md" in result.output


# Cycle 1.1: load_state() backward compat


def test_load_state_ignores_unknown_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """load_state() ignores truly unknown fields, loads known ones."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "tmp").mkdir()

    state_data = {
        "input_markdown": "test markdown",
        "timestamp": "2026-03-24T12:00:00+00:00",
        "step_reached": "write_session",
        "unknown_field": "should be ignored",
    }
    (tmp_path / "tmp" / ".handoff-state.json").write_text(json.dumps(state_data))

    result = load_state()

    assert result is not None
    assert result.input_markdown == "test markdown"
    assert result.timestamp == "2026-03-24T12:00:00+00:00"
    assert result.step_reached == "write_session"
    assert not hasattr(result, "unknown_field")


def test_handoff_missing_session_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Handoff with missing session.md exits 2 with error."""
    monkeypatch.chdir(tmp_path)
    init_repo_minimal(tmp_path)
    session_file = tmp_path / "agents" / "session.md"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        input=HANDOFF_STDIN,
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 2
    assert "**Error:**" in result.output
    assert "session" in result.output
    assert "Traceback" not in result.output


# Cycle 1.2: CLI resume from step_reached


def test_handoff_resume_from_diagnostics_skips_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resume from diagnostics skips writes, checks git."""
    monkeypatch.chdir(tmp_path)
    session_file = _setup_cli_repo(tmp_path)
    initial_content = session_file.read_text()

    # Save state with step_reached="diagnostics"
    save_state(HANDOFF_STDIN, step_reached="diagnostics")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 0
    # Writes were skipped; session.md unchanged
    assert session_file.read_text() == initial_content
    # Git diagnostics were emitted
    assert "**Git status:**" in result.output
    # State file cleared
    assert not (tmp_path / "tmp" / ".handoff-state.json").exists()


def test_handoff_updates_step_reached_after_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """step_reached persists correct value for crash recovery."""
    monkeypatch.chdir(tmp_path)
    _setup_cli_repo(tmp_path)

    # State at write_session (before writes complete)
    save_state(HANDOFF_STDIN, step_reached="write_session")
    state = load_state()
    assert state is not None
    assert state.step_reached == "write_session"

    # State at diagnostics (after writes, before cleanup)
    save_state(HANDOFF_STDIN, step_reached="diagnostics")
    state = load_state()
    assert state is not None
    assert state.step_reached == "diagnostics"

    # State file persists until explicit clear
    assert (tmp_path / "tmp" / ".handoff-state.json").exists()


# m-6: empty git_changes output


def test_handoff_skips_empty_git_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty git_changes omits code block, not an empty one."""
    monkeypatch.chdir(tmp_path)
    session_file = _setup_cli_repo(tmp_path)

    monkeypatch.setattr(
        "edify.session.handoff.cli.git_changes",
        lambda: "",
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        input=HANDOFF_STDIN,
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 0
    assert "**Git status:**" not in result.output


# m-15: resume from write_session step


def test_handoff_resume_from_write_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resume from write_session re-executes session writes."""
    monkeypatch.chdir(tmp_path)
    session_file = _setup_cli_repo(tmp_path)
    save_state(HANDOFF_STDIN, step_reached="write_session")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_handoff"],
        env={"CLAUDEUTILS_SESSION_FILE": str(session_file)},
    )

    assert result.exit_code == 0
    content = session_file.read_text()
    # Writes executed: status updated and completed replaced
    assert "Phase 4 complete." in content
    assert "Implemented write_completed" in content
    assert "Previous task" not in content
    # State file cleared after successful resume
    assert not (tmp_path / "tmp" / ".handoff-state.json").exists()
