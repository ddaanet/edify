"""Tests for worktree CLI automation of session.md task movement."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.utils import wt_path


def test_new_task_mode_moves_task_to_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Task mode: after worktree created, moves task from Pending to Worktree Tasks."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = r"""# Session Handoff

## Pending Tasks

- [ ] **Implement feature X** — `\`/runbook\`` | sonnet
- [ ] **Fix bug Y** — `\`/design\`` | haiku

## Blockers / Gotchas

- None currently
"""
    session_file.write_text(session_content)

    result = CliRunner().invoke(worktree, ["new", "--task", "Implement feature X"])
    assert result.exit_code == 0

    updated_session = session_file.read_text()
    assert "## Pending Tasks" in updated_session
    assert (
        "Implement feature X"
        not in updated_session.split("## Pending Tasks")[1].split("## ")[0]
    )
    assert "## Worktree Tasks" in updated_session
    assert "Implement feature X" in updated_session.split("## Worktree Tasks")[1]
    assert "→ `implement-feature-x`" in updated_session
    assert "Fix bug Y" in updated_session


def test_rm_calls_remove_worktree_task_before_branch_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Rm command calls remove_worktree_task before deleting branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = r"""# Session Handoff

## Pending Tasks

- [ ] **Other task** — `\`/runbook\`` | sonnet

## Worktree Tasks

- [ ] **Feature A** → `feature-a` — `\`/design\`` | haiku
"""
    session_file.write_text(session_content)

    result = CliRunner().invoke(
        worktree, ["new", "feature-a", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    worktree_path = wt_path("feature-a")
    worktree_session = worktree_path / "agents" / "session.md"

    worktree_session_content = r"""# Focused Session

## Pending Tasks

## Worktree Tasks
"""
    worktree_session.write_text(worktree_session_content)
    subprocess.run(
        ["git", "-C", str(worktree_path), "add", "agents/session.md"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(worktree_path), "commit", "-m", "mark task complete"],
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["rm", "feature-a"])
    assert result.exit_code == 0

    final_session = session_file.read_text()
    assert "## Worktree Tasks" not in final_session or "Feature A" not in final_session


def test_rm_e2e_removes_completed_task_from_worktree_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """E2E: rm removes task from Worktree Tasks when task completed in branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = r"""# Session Handoff

## Pending Tasks

- [ ] **Other task** — `\`/design\`` | sonnet

## Worktree Tasks

- [ ] **Complete the feature** → `complete-the-feature` — `\`/runbook\`` | haiku
"""
    session_file.write_text(session_content)

    result = CliRunner().invoke(
        worktree, ["new", "complete-the-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    worktree_path = wt_path("complete-the-feature")
    worktree_session = worktree_path / "agents" / "session.md"

    worktree_content = worktree_session.read_text()
    assert "## Pending Tasks" in worktree_content
    assert "Complete the feature" in worktree_content

    worktree_session_completed = r"""# Focused Session

## Pending Tasks

## Blockers / Gotchas
"""
    worktree_session.write_text(worktree_session_completed)
    subprocess.run(
        ["git", "-C", str(worktree_path), "add", "agents/session.md"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(worktree_path), "commit", "-m", "complete task"],
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["rm", "complete-the-feature"])
    assert result.exit_code == 0
    assert "Removed worktree complete-the-feature" in result.output

    final_session = session_file.read_text()
    assert "Complete the feature" not in final_session
    assert "Other task" in final_session
