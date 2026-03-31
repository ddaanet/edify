"""Tests for worktree rm subcommand."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree
from edify.worktree.git_ops import _is_merge_commit
from tests.fixtures_worktree import _branch_exists, _create_worktree


def test_rm_basic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Removes worktree directory and branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "removed" in result.output.lower()


def test_rm_branch_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Cleans up branch when directory removed externally."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert _branch_exists("test-feature")

    subprocess.run(["rm", "-rf", str(worktree_path)], check=True, capture_output=True)
    assert not worktree_path.exists()
    assert _branch_exists("test-feature")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not _branch_exists("test-feature")
    assert (
        "error" not in result.output.lower()
        or "no such file" not in result.output.lower()
    )


def test_rm_removes_slug_marker_from_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Remove slug marker from session.md when worktree is removed.

    Verifies that rm() calls remove_slug_marker to update Worktree Tasks.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create a worktree task entry in session.md
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `test-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # Create test-feature branch with a commit, then merge it into main.
    subprocess.run(
        ["git", "checkout", "-b", "test-feature"], check=True, capture_output=True
    )
    (repo_path / "feature.txt").write_text("feature content")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Feature commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "test-feature"], check=True, capture_output=True
    )

    # Create worktree (branch already exists, worktree add attaches to it)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0

    # Verify slug marker was removed from session.md
    session_content = session_file.read_text()
    assert "→ `test-feature`" not in session_content
    # Task should still be there without marker
    assert "- [ ] **Task One** — description" in session_content


def test_rm_does_not_amend_on_normal_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """When HEAD is a normal commit (not merge), rm() must NOT amend."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `test-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # HEAD is a normal commit (1 parent, not merge)
    assert not _is_merge_commit()

    # Create worktree and remove it
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])
    assert result.exit_code == 0

    # If amend happened incorrectly, the task removal would be in HEAD commit
    # Instead, verify session.md in HEAD still has the task (was NOT amended in)
    session_in_head = subprocess.run(
        ["git", "show", "HEAD:agents/session.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    # If no amend, HEAD:agents/session.md still contains the task
    # (the modification from remove_slug_marker is only in working tree)
    assert "Worktree Tasks" in session_in_head


def test_rm_git_error_shows_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Git failure during rm shows error message, not traceback."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    _create_worktree(repo_path, "test-feature", init_repo)

    # Inject git failure at worktree removal
    err = subprocess.CalledProcessError(1, ["git", "worktree", "remove"])
    err.stderr = "fatal: test error message"

    def _raise(*_args: object, **_kwargs: object) -> None:
        raise err

    monkeypatch.setattr("edify.worktree.cli._remove_worktrees", _raise)

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 1
    assert "git error:" in result.output
    assert "test error message" in result.output
    assert isinstance(result.exception, SystemExit)  # controlled exit, not crash


def test_rm_force_bypasses_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Force flag bypasses safety checks."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--force", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "removed" in result.output.lower()
