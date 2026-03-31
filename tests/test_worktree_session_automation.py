"""Tests for worktree CLI automation of session.md task movement."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree
from edify.worktree.git_ops import wt_path


def test_new_task_mode_adds_slug_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Task mode: adds slug marker to task in Worktree Tasks."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = """# Session Handoff

## In-tree Tasks

- [ ] **Fix bug Y** — `/design` | haiku

## Worktree Tasks

- [ ] **Implement feature X** — `/runbook` | sonnet

## Blockers / Gotchas

- None currently
"""
    session_file.write_text(session_content)

    result = CliRunner().invoke(worktree, ["new", "Implement feature X"])
    assert result.exit_code == 0

    updated_session = session_file.read_text()
    assert "## In-tree Tasks" in updated_session
    assert "- [ ] **Fix bug Y** — `/design` | haiku" in updated_session
    assert "## Worktree Tasks" in updated_session
    assert "→ `implement-feature-x`" in updated_session
    assert (
        "- [ ] **Implement feature X** → `implement-feature-x` — `/runbook` | sonnet"
        in updated_session
    )


def test_rm_removes_slug_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Rm command removes slug marker from task in Worktree Tasks."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = """# Session Handoff

## In-tree Tasks

- [ ] **Other task** — `/runbook` | sonnet

## Worktree Tasks

- [ ] **Feature A** → `feature-a` — `/design` | haiku
"""
    session_file.write_text(session_content)
    # Track session.md on main (matches production state)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "track session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a branch for feature-a
    subprocess.run(
        ["git", "branch", "feature-a"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(
        worktree, ["new", "--branch", "feature-a", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    wt_path("feature-a")

    # Merge branch so rm guard allows removal
    subprocess.run(
        ["git", "merge", "feature-a", "--no-edit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["rm", "feature-a"])
    assert result.exit_code == 0

    final_session = session_file.read_text()
    # Slug marker should be removed
    assert "→ `feature-a`" not in final_session
    # Task should still be in Worktree Tasks but without marker
    assert "- [ ] **Feature A** — `/design` | haiku" in final_session


def test_rm_e2e_slug_marker_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """E2E: rm removes slug marker from task in Worktree Tasks."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = """# Session Handoff

## In-tree Tasks

- [ ] **Other task** — `/design` | sonnet

## Worktree Tasks

- [ ] **Complete the feature** → `complete-the-feature` — `/runbook` | haiku
"""
    session_file.write_text(session_content)
    # Track session.md on main (matches production state)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "track session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a branch for the task
    subprocess.run(
        ["git", "branch", "complete-the-feature"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(
        worktree,
        ["new", "--branch", "complete-the-feature", "--session", str(session_file)],
    )
    assert result.exit_code == 0

    # Merge the branch (in this simple test case, nothing changes on branch)
    subprocess.run(
        ["git", "merge", "complete-the-feature", "--no-edit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["rm", "complete-the-feature"])
    assert result.exit_code == 0
    assert "Removed complete-the-feature" in result.output

    final_session = session_file.read_text()
    assert "## Worktree Tasks" in final_session
    # Slug marker should be removed
    assert "→ `complete-the-feature`" not in final_session
    # Task should still be there without marker
    assert "- [ ] **Complete the feature** — `/runbook` | haiku" in final_session
    assert "Other task" in final_session
