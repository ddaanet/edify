"""Tests for handoff committed detection (H-2 write modes)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from edify.session.handoff.pipeline import (
    _detect_write_mode,
    write_completed,
)
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

    # Remove committed content and add new — triggers append mode
    # (committed lines absent from current section)
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


# m-7: trailing whitespace normalization in section comparison


def test_detect_write_mode_trailing_whitespace(tmp_path: Path) -> None:
    """Trailing blank line diff is overwrite, not autostrip."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"

    # Commit with trailing blank line before next section
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # Remove trailing blank line — content semantically identical
    no_trailing = SESSION_WITH_COMPLETED.replace(
        "- Old task B\n\n## In-tree Tasks",
        "- Old task B\n## In-tree Tasks",
    )
    session_file.write_text(no_trailing)

    mode, _ = _detect_write_mode(session_file)
    assert mode == "overwrite"


# m-5: indentation-aware comparison


def test_detect_write_mode_indentation_not_autostrip(
    tmp_path: Path,
) -> None:
    """Indentation change prevents false autostrip match."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"

    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # Change indentation of one item + add new content
    modified = SESSION_WITH_COMPLETED.replace(
        "- Old task A\n",
        "  - Old task A\n- New addition\n",
    )
    session_file.write_text(modified)

    mode, _ = _detect_write_mode(session_file)
    assert mode == "append"


# m-1: blank line preservation in append/autostrip


def test_write_completed_append_preserves_blank_lines(
    tmp_path: Path,
) -> None:
    """Blank lines between groups preserved in append mode."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # Prior uncommitted handoff: replaced content has groups with
    # blank line between (triggers append — committed removed)
    prior = SESSION_WITH_COMPLETED.replace(
        "- Old task A\n- Old task B\n",
        "### Group 1\n- Item 1\n\n### Group 2\n- Item 2\n",
    )
    session_file.write_text(prior)

    write_completed(session_file, ["- Fresh work."])

    content = session_file.read_text()
    completed = content.split("## Completed This Session")[1]
    completed = completed.split("## In-tree")[0]
    assert "- Item 1\n\n### Group 2" in completed


def test_write_completed_autostrip_preserves_blank_lines(
    tmp_path: Path,
) -> None:
    """Blank lines in uncommitted content preserved in autostrip."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # Agent appends: committed items kept + two new groups with
    # blank line between (triggers autostrip — committed preserved)
    prior = SESSION_WITH_COMPLETED.replace(
        "- Old task B\n",
        "- Old task B\n\n### Group 1\n- Item 1\n\n### Group 2\n- Item 2\n",
    )
    session_file.write_text(prior)

    write_completed(session_file, ["- Fresh."])

    content = session_file.read_text()
    completed = content.split("## Completed This Session")[1]
    completed = completed.split("## In-tree")[0]
    assert "- Old task A" not in completed
    # Inter-group blank line preserved in uncommitted content
    assert "- Item 1\n\n### Group 2" in completed


# m-17: direct _detect_write_mode unit test (all 3 modes)


def test_detect_write_mode_all_three_modes(tmp_path: Path) -> None:
    """Each mode triggers under its documented condition."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    _commit_session(tmp_path, session_file)

    # No changes → overwrite
    mode, _ = _detect_write_mode(session_file)
    assert mode == "overwrite"

    # Remove committed, add new → append
    session_file.write_text(
        SESSION_WITH_COMPLETED.replace(
            "- Old task A\n- Old task B\n",
            "- Replaced content\n",
        )
    )
    mode, _ = _detect_write_mode(session_file)
    assert mode == "append"

    # Keep committed, add new → autostrip
    session_file.write_text(
        SESSION_WITH_COMPLETED.replace(
            "- Old task B\n",
            "- Old task B\n- Additional item\n",
        )
    )
    mode, committed = _detect_write_mode(session_file)
    assert mode == "autostrip"
    assert "- Old task A" in committed


# m-14: autostrip error fallback (git show fails → overwrite)


def test_detect_write_mode_overwrite_on_no_head(tmp_path: Path) -> None:
    """Returns overwrite when HEAD has no session.md."""
    init_repo_minimal(tmp_path)
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    # File exists on disk but NOT committed → git show HEAD: fails

    mode, committed = _detect_write_mode(session_file)
    assert mode == "overwrite"
    assert committed == ""
