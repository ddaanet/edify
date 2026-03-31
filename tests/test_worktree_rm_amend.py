"""Tests for worktree rm amend safety — verifies amend targets correct merge."""

from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree
from edify.worktree.git_ops import _is_merge_commit
from tests.fixtures_worktree import _create_worktree, _git_setup


def test_rm_does_not_amend_wrong_branch_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Rm must not amend HEAD when merge commit is from a different branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task for "other-wt"
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `other-wt` — description\n"
    )
    _git_setup("add", "agents/session.md")
    _git_setup("commit", "-m", "Add session")

    # Create and merge "merged-branch" (a DIFFERENT branch, not "other-wt")
    _git_setup("checkout", "-b", "merged-branch")
    (repo_path / "merged.txt").write_text("merged content")
    _git_setup("add", "merged.txt")
    _git_setup("commit", "-m", "Merged branch commit")
    _git_setup("checkout", "main")
    _git_setup("merge", "--no-ff", "merged-branch")

    assert _is_merge_commit()

    # Create worktree for "other-wt" (not the branch that was merged)
    worktree_path = _create_worktree(repo_path, "other-wt", init_repo)
    assert worktree_path.exists()

    # Record HEAD commit hash before rm
    head_before = _git_setup("rev-parse", "HEAD").strip()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "other-wt"])
    assert result.exit_code == 0

    # HEAD should NOT have been amended — commit hash unchanged
    head_after = _git_setup("rev-parse", "HEAD").strip()
    assert head_before == head_after
    assert "amend" not in result.output.lower()


def test_rm_force_does_not_amend_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """--force rm must never amend, even when HEAD is a merge commit."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `force-wt` — description\n"
    )
    _git_setup("add", "agents/session.md")
    _git_setup("commit", "-m", "Add session")

    # Create and merge a different branch to make HEAD a merge commit
    _git_setup("checkout", "-b", "some-feature")
    (repo_path / "feature.txt").write_text("feature")
    _git_setup("add", "feature.txt")
    _git_setup("commit", "-m", "Feature")
    _git_setup("checkout", "main")
    _git_setup("merge", "--no-ff", "some-feature")

    assert _is_merge_commit()

    # Create worktree for force-wt (never merged)
    worktree_path = _create_worktree(repo_path, "force-wt", init_repo)
    assert worktree_path.exists()

    head_before = _git_setup("rev-parse", "HEAD").strip()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--force", "force-wt"])
    assert result.exit_code == 0

    # HEAD must not be amended
    head_after = _git_setup("rev-parse", "HEAD").strip()
    assert head_before == head_after
    assert "amend" not in result.output.lower()
