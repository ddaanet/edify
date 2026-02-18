"""Tests for MERGE_HEAD detection in worktree merge operations."""

import subprocess
from pathlib import Path

import pytest

from claudeutils.worktree.merge import (
    _detect_merge_state,
    _phase4_merge_commit_and_precommit,
)


def test_detect_state_merged(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify _detect_merge_state returns 'merged' when branch is ancestor of HEAD."""
    monkeypatch.chdir(repo_with_submodule)

    # Set up repo: create initial commit
    (repo_with_submodule / "file.txt").write_text("content\n")
    subprocess.run(["git", "add", "file.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add file"],
        check=True,
        capture_output=True,
    )

    # Create branch from current HEAD
    subprocess.run(
        ["git", "branch", "test-branch", "HEAD"],
        check=True,
        capture_output=True,
    )

    # Merge the branch into main
    subprocess.run(
        ["git", "merge", "--no-edit", "test-branch"],
        check=True,
        capture_output=True,
    )

    # After merge, _detect_merge_state should return "merged"
    state = _detect_merge_state("test-branch")
    assert state == "merged", f"Expected 'merged', got '{state}'"

    # Control: create an unmerged branch by:
    # 1. Create a commit on main
    (repo_with_submodule / "main_file.txt").write_text("main content\n")
    subprocess.run(["git", "add", "main_file.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Main commit"],
        check=True,
        capture_output=True,
    )

    # 2. Create unmerged-branch pointing to the previous commit (before main_file.txt)
    subprocess.run(
        ["git", "branch", "unmerged-branch", "HEAD~1"],
        check=True,
        capture_output=True,
    )

    # 3. Make a commit on unmerged-branch that won't be on main
    subprocess.run(
        ["git", "checkout", "unmerged-branch"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "unmerged.txt").write_text("unmerged content\n")
    subprocess.run(["git", "add", "unmerged.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Unmerged commit"],
        check=True,
        capture_output=True,
    )

    # 4. Check out main to leave unmerged-branch unmerged
    subprocess.run(
        ["git", "checkout", "main"],
        check=True,
        capture_output=True,
    )
    state_clean = _detect_merge_state("unmerged-branch")
    assert state_clean == "clean", f"Expected 'clean', got '{state_clean}'"


def test_phase4_merge_head_empty_diff(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Verify _phase4 commits with MERGE_HEAD present and empty diff."""
    monkeypatch.chdir(repo_with_submodule)

    # Set up initial state
    (repo_with_submodule / "file.txt").write_text("content\n")
    subprocess.run(["git", "add", "file.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add file"],
        check=True,
        capture_output=True,
    )

    # Create test branch
    subprocess.run(
        ["git", "branch", "test-branch", "HEAD"],
        check=True,
        capture_output=True,
    )

    # Simulate merge in progress: create MERGE_HEAD manually
    branch_commit = subprocess.run(
        ["git", "rev-parse", "test-branch"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    (repo_with_submodule / ".git" / "MERGE_HEAD").write_text(f"{branch_commit}\n")

    # Verify MERGE_HEAD exists
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_check.returncode == 0, "MERGE_HEAD should exist"

    # Verify NO staged changes
    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
    )
    assert staged_check.returncode == 0, "Should have no staged changes"

    # Call _phase4 - should detect MERGE_HEAD and commit
    _phase4_merge_commit_and_precommit("test-branch")

    # Verify MERGE_HEAD is gone
    merge_head_after = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_after.returncode != 0, (
        "MERGE_HEAD should be removed after _phase4"
    )

    # Verify merge commit was created
    log_output = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert log_output.stdout.strip().startswith("🔀 Merge"), (
        f"Expected merge commit, got: {log_output.stdout}"
    )

    # Verify git branch -d succeeds (branch is ancestor of HEAD after merge commit)
    branch_delete = subprocess.run(
        ["git", "branch", "-d", "test-branch"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert branch_delete.returncode == 0, (
        f"git branch -d should succeed after merge commit: {branch_delete.stderr}"
    )


