"""Tests for Track 2: Merge correctness (MERGE_HEAD checkpoint)."""

import subprocess
from pathlib import Path


def test_phase4_refuses_single_parent_when_unmerged(tmp_path: Path) -> None:
    """Phase 4 refuses single-parent commit when branch unmerged."""
    from claudeutils.worktree.merge import _phase4_merge_commit_and_precommit

    # Set up: Create branch, make changes, stage them
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=repo_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (repo_dir / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Create branch
    subprocess.run(
        ["git", "branch", "test-branch"], cwd=repo_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "checkout", "test-branch"], cwd=repo_dir, check=True, capture_output=True
    )

    # Make changes on branch
    (repo_dir / "file.txt").write_text("branch content")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "branch commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Return to main
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_dir, check=True, capture_output=True
    )

    # Make changes on main to create divergence
    (repo_dir / "other.txt").write_text("main content")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "main commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Initiate merge (will stage changes but we'll remove MERGE_HEAD)
    subprocess.run(
        ["git", "merge", "--no-commit", "test-branch"],
        cwd=repo_dir,
        check=False,
        capture_output=True,
    )

    # Simulate MERGE_HEAD loss
    merge_head_file = repo_dir / ".git" / "MERGE_HEAD"
    if merge_head_file.exists():
        merge_head_file.unlink()

    # Verify staged changes present
    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_dir,
        check=False,
    )
    assert staged_check.returncode != 0, "Staged changes should be present"

    # Verify branch NOT merged
    from claudeutils.worktree.utils import _is_branch_merged

    assert not _is_branch_merged("test-branch"), "Branch should not be merged"

    # Get commit before Phase 4 call
    commit_before = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Call Phase 4 - expecting it to exit with code 2 and no commit
    import os
    from unittest.mock import patch, MagicMock
    import subprocess as real_subprocess

    original_cwd = os.getcwd()
    exit_code = 0

    # Save reference to real subprocess.run before patching
    real_run = real_subprocess.run

    # Create a mock for just precommit
    mock_precommit = MagicMock()
    mock_precommit.returncode = 0
    mock_precommit.stderr = ""

    def selective_mock(cmd, **kwargs):
        if cmd[0] == "just" and "precommit" in cmd:
            return mock_precommit
        return real_run(cmd, **kwargs)

    try:
        os.chdir(repo_dir)
        # Patch the subprocess.run call that runs "just precommit"
        with patch("claudeutils.worktree.merge.subprocess.run", side_effect=selective_mock):
            try:
                _phase4_merge_commit_and_precommit("test-branch")
            except SystemExit as e:
                exit_code = e.code
    finally:
        os.chdir(original_cwd)

    # Get commit after Phase 4 call
    commit_after = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Assertions
    # Expected behavior: exit code 2, no commit
    # Current behavior: exit code 0, commit created
    assert exit_code == 2, (
        f"Expected exit code 2 (refuse), got {exit_code}. "
        f"Commit before: '{commit_before}', after: '{commit_after}'"
    )
    assert commit_after == commit_before, (
        f"No new commit should be created, but commit changed from '{commit_before}' to '{commit_after}'"
    )
