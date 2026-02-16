"""Tests for _is_branch_merged guard function."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.cli import _classify_branch
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


def test_classify_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify branch classification by commit count and focused marker.

    Tests that _classify_branch returns (count, is_focused) where:
    - count is the number of commits between merge-base and branch tip
    - is_focused is True only if count==1 and message matches
      "Focused session for {slug}"
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    # Case 1: Focused-session-only branch (1 commit with marker)
    subprocess.run(
        ["git", "checkout", "-b", "focused-session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Create the exact marker text from _create_session_commit
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Focused session for focused-session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("focused-session")
    assert count == 1, f"Expected count=1 but got {count}"
    assert is_focused is True, f"Expected is_focused=True but got {is_focused}"

    # Case 2: Real-history branch (1 user commit)
    # (we're already on main from the checkout - above)
    subprocess.run(
        ["git", "checkout", "-b", "real-history"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "user-file.txt").write_text("user content")
    subprocess.run(
        ["git", "add", "user-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "User commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("real-history")
    assert count == 1
    assert is_focused is False

    # Case 3: Multi-commit branch (3 commits)
    # (we're already on main from the checkout - above)
    subprocess.run(
        ["git", "checkout", "-b", "multi-commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    for i in range(3):
        (repo_path / f"file-{i}.txt").write_text(f"content {i}")
        subprocess.run(
            ["git", "add", f"file-{i}.txt"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"Commit {i}"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("multi-commit")
    assert count == 3
    assert is_focused is False

    # Case 4: Marker with similar but wrong format (missing "for")
    # (we're already on main from the checkout - above)
    subprocess.run(
        ["git", "checkout", "-b", "wrong-format"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Focused session wrong-format"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("wrong-format")
    assert count == 1
    assert is_focused is False
