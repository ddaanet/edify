"""Tests for handoff committed detection (H-2 write modes)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from claudeutils.session.handoff.pipeline import write_completed
from tests.pytest_helpers import init_repo_minimal

SESSION_WITH_COMPLETED = """\
# Session Handoff: 2026-03-15

**Status:** Previous session status.

## Completed This Session

- Old task A
- Old task B

## In-tree Tasks

- [ ] **Task C** — `cmd` | sonnet
"""


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


# H-2 mode: overwrite (no diff from HEAD)


def test_write_completed_overwrite_when_no_diff(tmp_path: Path) -> None:
    """write_completed overwrites section when no diff from HEAD."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    write_completed(session_file, ["- New work."])

    content = session_file.read_text()
    assert "- New work." in content
    assert "- Old task A" not in content
    assert "- Old task B" not in content


# Also covers M-1: committed-state overwrite verification


def test_write_completed_overwrites_committed_state(
    tmp_path: Path,
) -> None:
    """write_completed overwrites section after session.md is committed."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    write_completed(session_file, ["- New work done."])

    content = session_file.read_text()
    assert "- New work done." in content
    assert "- Old task A" not in content
    assert "- Old task B" not in content


# H-2 mode: append (old removed, new present)


def test_write_completed_appends_when_prior_uncommitted(
    tmp_path: Path,
) -> None:
    """write_completed appends when prior changes not committed."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # Simulate prior uncommitted handoff: replace old
    # content with new (removing old, writing new)
    prior_content = SESSION_WITH_COMPLETED.replace(
        "- Old task A\n- Old task B\n",
        "- First handoff.\n",
    )
    session_file.write_text(prior_content)

    # Now call write_completed with additional work
    write_completed(session_file, ["- Additional work."])

    content = session_file.read_text()
    # Should have both prior uncommitted + new
    assert "- First handoff." in content
    assert "- Additional work." in content
    # Should NOT have old committed content
    assert "- Old task A" not in content
    assert "- Old task B" not in content


# H-2 mode: autostrip (old preserved with additions)


def test_write_completed_autostrip_when_old_preserved(
    tmp_path: Path,
) -> None:
    """Autostrip strips committed, keeps uncommitted additions."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # Agent appends without clearing: keeps committed items +
    # adds new uncommitted item (simulates appended work)
    prior_content = SESSION_WITH_COMPLETED.replace(
        "- Old task B\n",
        "- Old task B\n- New uncommitted item\n",
    )
    session_file.write_text(prior_content)

    # Now call write_completed with fresh work
    write_completed(session_file, ["- Fresh work."])

    content = session_file.read_text()
    # Committed items should be stripped
    assert "- Old task A" not in content
    assert "- Old task B" not in content
    # Uncommitted additions should be kept
    assert "- New uncommitted item" in content
    # Fresh work should be present
    assert "- Fresh work." in content
