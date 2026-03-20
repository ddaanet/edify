"""Tests for session handoff CLI wiring (Cycle 4.7)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.session.handoff.pipeline import save_state


def _init_repo(path: Path) -> None:
    """Initialize a minimal git repo for CLI testing."""
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
    _init_repo(tmp_path)
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
    assert "Git status" in result.output
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
    save_state(HANDOFF_STDIN, step="write_session")

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
