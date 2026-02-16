"""Tests for _is_branch_merged guard function."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.utils import _is_branch_merged


def test_is_branch_merged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify branch merge detection with git merge-base.

    Tests that _is_branch_merged returns True for merged branches and False for
    unmerged branches using git merge-base --is-ancestor.
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Create a branch that will be merged into main
    subprocess.run(
        ["git", "checkout", "-b", "merged-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "merged-file.txt").write_text("merged content")
    subprocess.run(
        ["git", "add", "merged-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit on merged branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and merge the branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "merge", "merged-branch", "--no-edit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Test that merged branch returns True
    assert _is_branch_merged("merged-branch") is True

    # Create a branch that will NOT be merged
    subprocess.run(
        ["git", "checkout", "-b", "unmerged-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "unmerged-file.txt").write_text("unmerged content")
    subprocess.run(
        ["git", "add", "unmerged-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit on unmerged branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main to verify unmerged branch is not an ancestor
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Test that unmerged branch returns False
    assert _is_branch_merged("unmerged-branch") is False
