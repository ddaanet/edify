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
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
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
        ["git", "checkout", "test-branch"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
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
    import subprocess as real_subprocess
    from unittest.mock import MagicMock, patch

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
        with patch(
            "claudeutils.worktree.merge.subprocess.run", side_effect=selective_mock
        ):
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


def test_phase4_allows_already_merged(tmp_path: Path) -> None:
    """Phase 4 allows commit when branch already merged (idempotent)."""
    from claudeutils.worktree.merge import _phase4_merge_commit_and_precommit

    # Set up: Create branch, make changes, merge to main
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
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
        ["git", "checkout", "test-branch"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
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

    # Return to main and merge the branch
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "merge", "test-branch"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Now branch is already merged
    # Verify branch is merged (run git command directly in test repo)
    merge_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "test-branch", "HEAD"],
        cwd=repo_dir,
        check=False,
    )
    assert merge_check.returncode == 0, "Branch should be merged"

    # Simulate re-merge: stage some changes (e.g., additional work)
    (repo_dir / "additional.txt").write_text("additional content")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)

    # No MERGE_HEAD (already merged, not in merge state)
    merge_head_file = repo_dir / ".git" / "MERGE_HEAD"
    assert not merge_head_file.exists(), "MERGE_HEAD should not exist"

    # Verify staged changes present
    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_dir,
        check=False,
    )
    assert staged_check.returncode != 0, "Staged changes should be present"

    # Get commit before Phase 4 call
    commit_before = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Call Phase 4 - expecting it to exit with code 0 and create commit
    import os
    import subprocess as real_subprocess
    from unittest.mock import MagicMock, patch

    original_cwd = os.getcwd()
    exit_code = None

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
        with patch(
            "claudeutils.worktree.merge.subprocess.run", side_effect=selective_mock
        ):
            try:
                _phase4_merge_commit_and_precommit("test-branch")
                exit_code = 0
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
    # Expected behavior: exit code 0, commit created
    assert exit_code == 0, (
        f"Expected exit code 0 (success), got {exit_code}. "
        f"Commit before: '{commit_before}', after: '{commit_after}'"
    )
    assert commit_after != commit_before, (
        f"New commit should be created, but commit stayed as '{commit_before}'"
    )
    assert "Merge test-branch" in commit_after, (
        f"Commit message should contain merge reference, got: '{commit_after}'"
    )


def test_phase4_handles_no_merge_head_no_staged(tmp_path: Path) -> None:
    """Phase 4 handles no MERGE_HEAD + no staged changes: exit 2 if unmerged,
    skip if merged."""
    import os
    import subprocess as real_subprocess
    from unittest.mock import MagicMock, patch

    from claudeutils.worktree.merge import _phase4_merge_commit_and_precommit

    # Scenario A: Branch exists, no MERGE_HEAD, no staged changes, branch NOT merged
    repo_dir_a = tmp_path / "repo_a"
    repo_dir_a.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir_a, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (repo_dir_a / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "."], cwd=repo_dir_a, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Create branch
    subprocess.run(
        ["git", "branch", "test-branch"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "test-branch"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Make changes on branch
    (repo_dir_a / "file.txt").write_text("branch content")
    subprocess.run(["git", "add", "."], cwd=repo_dir_a, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "branch commit"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Return to main
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_dir_a, check=True, capture_output=True
    )

    # Verify no MERGE_HEAD
    merge_head_file_a = repo_dir_a / ".git" / "MERGE_HEAD"
    assert not merge_head_file_a.exists(), "MERGE_HEAD should not exist"

    # Verify no staged changes
    staged_check_a = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_dir_a,
        check=False,
    )
    assert staged_check_a.returncode == 0, "No staged changes should be present"

    # Verify branch NOT merged

    merge_check_a = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "test-branch", "HEAD"],
        cwd=repo_dir_a,
        check=False,
    )
    assert merge_check_a.returncode != 0, "Branch should not be merged"

    # Get commit before Phase 4 call
    commit_before_a = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Call Phase 4 - expecting exit code 2
    original_cwd = os.getcwd()
    exit_code_a = None

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
        os.chdir(repo_dir_a)
        with patch(
            "claudeutils.worktree.merge.subprocess.run", side_effect=selective_mock
        ):
            try:
                _phase4_merge_commit_and_precommit("test-branch")
                exit_code_a = 0
            except SystemExit as e:
                exit_code_a = e.code
    finally:
        os.chdir(original_cwd)

    # Get commit after Phase 4 call
    commit_after_a = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Assertions for Scenario A
    assert exit_code_a == 2, f"Scenario A: Expected exit code 2, got {exit_code_a}"
    assert commit_after_a == commit_before_a, (
        f"Scenario A: No commit should be created, but commit changed from '{commit_before_a}' to '{commit_after_a}'"
    )

    # Scenario B: Branch exists, no MERGE_HEAD, no staged changes, branch IS merged
    repo_dir_b = tmp_path / "repo_b"
    repo_dir_b.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir_b, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (repo_dir_b / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "."], cwd=repo_dir_b, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Create branch
    subprocess.run(
        ["git", "branch", "test-branch"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "test-branch"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Make changes on branch
    (repo_dir_b / "file.txt").write_text("branch content")
    subprocess.run(["git", "add", "."], cwd=repo_dir_b, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "branch commit"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Return to main and merge the branch
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_dir_b, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "merge", "test-branch"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Verify no MERGE_HEAD (already merged)
    merge_head_file_b = repo_dir_b / ".git" / "MERGE_HEAD"
    assert not merge_head_file_b.exists(), "MERGE_HEAD should not exist"

    # Verify no staged changes
    staged_check_b = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_dir_b,
        check=False,
    )
    assert staged_check_b.returncode == 0, "No staged changes should be present"

    # Verify branch IS merged
    merge_check_b = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "test-branch", "HEAD"],
        cwd=repo_dir_b,
        check=False,
    )
    assert merge_check_b.returncode == 0, "Branch should be merged"

    # Get commit before Phase 4 call
    commit_before_b = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Call Phase 4 - expecting exit code 0, no commit
    exit_code_b = None

    try:
        os.chdir(repo_dir_b)
        with patch(
            "claudeutils.worktree.merge.subprocess.run", side_effect=selective_mock
        ):
            try:
                _phase4_merge_commit_and_precommit("test-branch")
                exit_code_b = 0
            except SystemExit as e:
                exit_code_b = e.code
    finally:
        os.chdir(original_cwd)

    # Get commit after Phase 4 call
    commit_after_b = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Assertions for Scenario B
    assert exit_code_b == 0, f"Scenario B: Expected exit code 0, got {exit_code_b}"
    assert commit_after_b == commit_before_b, (
        f"Scenario B: No commit should be created (already merged), but commit changed from '{commit_before_b}' to '{commit_after_b}'"
    )


def test_validate_merge_result(tmp_path: Path) -> None:
    """Post-merge ancestry validation ensures slug is ancestor of HEAD."""
    import os
    import sys
    from io import StringIO

    from claudeutils.worktree.merge import _validate_merge_result

    # Scenario A: Valid merge - slug IS ancestor of HEAD
    repo_dir_a = tmp_path / "repo_a"
    repo_dir_a.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir_a, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (repo_dir_a / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "."], cwd=repo_dir_a, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Create branch
    subprocess.run(
        ["git", "branch", "test-branch"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "test-branch"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Make changes on branch
    (repo_dir_a / "file.txt").write_text("branch content")
    subprocess.run(["git", "add", "."], cwd=repo_dir_a, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "branch commit"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Return to main and merge properly
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_dir_a, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "merge", "test-branch"],
        cwd=repo_dir_a,
        check=True,
        capture_output=True,
    )

    # Call validation - should pass
    original_cwd = os.getcwd()
    exit_code_a = 0
    stderr_a = StringIO()

    try:
        os.chdir(repo_dir_a)
        old_stderr = sys.stderr
        sys.stderr = stderr_a
        try:
            _validate_merge_result("test-branch")
        except SystemExit as e:
            exit_code_a = e.code
        finally:
            sys.stderr = old_stderr
    finally:
        os.chdir(original_cwd)

    stderr_output_a = stderr_a.getvalue()

    # Assertions for Scenario A
    assert exit_code_a == 0, f"Expected exit code 0, got {exit_code_a}"
    assert "Error" not in stderr_output_a, (
        f"Should not have errors, got: {stderr_output_a}"
    )

    # Scenario B: Invalid merge - slug NOT ancestor of HEAD
    repo_dir_b = tmp_path / "repo_b"
    repo_dir_b.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir_b, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (repo_dir_b / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "."], cwd=repo_dir_b, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Create branch
    subprocess.run(
        ["git", "branch", "test-branch"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "test-branch"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Make changes on branch
    (repo_dir_b / "file.txt").write_text("branch content")
    subprocess.run(["git", "add", "."], cwd=repo_dir_b, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "branch commit"],
        cwd=repo_dir_b,
        check=True,
        capture_output=True,
    )

    # Return to main without merging
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo_dir_b, check=True, capture_output=True
    )

    # Call validation - should fail
    exit_code_b = 0
    stderr_b = StringIO()

    try:
        os.chdir(repo_dir_b)
        old_stderr = sys.stderr
        sys.stderr = stderr_b
        try:
            _validate_merge_result("test-branch")
        except SystemExit as e:
            exit_code_b = e.code
        finally:
            sys.stderr = old_stderr
    finally:
        os.chdir(original_cwd)

    stderr_output_b = stderr_b.getvalue()

    # Assertions for Scenario B
    assert exit_code_b == 2, f"Expected exit code 2, got {exit_code_b}"
    assert "Error: branch test-branch not fully merged" in stderr_output_b, (
        f"Should have merge error, got: {stderr_output_b}"
    )

    # Scenario C: Diagnostic - single parent commit triggers warning
    repo_dir_c = tmp_path / "repo_c"
    repo_dir_c.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir_c, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo_dir_c,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir_c,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (repo_dir_c / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "."], cwd=repo_dir_c, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_dir_c,
        check=True,
        capture_output=True,
    )

    # Create branch at same commit (fast-forward scenario)
    subprocess.run(
        ["git", "branch", "test-branch"],
        cwd=repo_dir_c,
        check=True,
        capture_output=True,
    )

    # Make a single-parent commit on main
    (repo_dir_c / "main-file.txt").write_text("main content")
    subprocess.run(["git", "add", "."], cwd=repo_dir_c, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "main commit"],
        cwd=repo_dir_c,
        check=True,
        capture_output=True,
    )

    # Call validation - should pass ancestry but warn about single parent
    stderr_c = StringIO()

    try:
        os.chdir(repo_dir_c)
        old_stderr = sys.stderr
        sys.stderr = stderr_c
        try:
            _validate_merge_result("test-branch")
        except SystemExit:
            pass
        finally:
            sys.stderr = old_stderr
    finally:
        os.chdir(original_cwd)

    stderr_output_c = stderr_c.getvalue()

    # Assertions for Scenario C
    assert "Warning: merge commit has 1 parent(s)" in stderr_output_c, (
        f"Should have single-parent warning, got: {stderr_output_c}"
    )


def test_merge_preserves_parent_repo_files(tmp_path: Path) -> None:
    """Full merge flow preserves both parent repo and submodule files."""
    import os
    import subprocess as real_subprocess
    from unittest.mock import MagicMock, patch

    from claudeutils.worktree.merge import (
        _phase1_validate_clean_trees,
        _phase3_merge_parent,
        _phase4_merge_commit_and_precommit,
    )

    # Set up parent repo
    parent_repo = tmp_path / "parent"
    parent_repo.mkdir()
    subprocess.run(["git", "init"], cwd=parent_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=parent_repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=parent_repo,
        check=True,
        capture_output=True,
    )

    # Initial commit
    (parent_repo / "initial.txt").write_text("initial content")
    subprocess.run(
        ["git", "add", "."], cwd=parent_repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=parent_repo,
        check=True,
        capture_output=True,
    )

    # Create worktree directory and branch
    worktree_dir = tmp_path / "wt" / "test"
    worktree_dir.mkdir(parents=True)
    subprocess.run(
        ["git", "worktree", "add", "-b", "test-branch", str(worktree_dir)],
        cwd=parent_repo,
        check=True,
        capture_output=True,
    )

    # Make changes in worktree: parent repo file
    parent_change_file = worktree_dir / "parent-change.txt"
    parent_change_file.write_text("parent repo change")

    # Commit changes in worktree branch
    subprocess.run(
        ["git", "add", "."], cwd=worktree_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "worktree changes"],
        cwd=worktree_dir,
        check=True,
        capture_output=True,
    )

    # Return to main repo for merge
    # Run merge flow (Phases 1, 3, 4 - skip phase 2 as no submodule)
    original_cwd = os.getcwd()

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
        os.chdir(parent_repo)
        with patch(
            "claudeutils.worktree.merge.subprocess.run", side_effect=selective_mock
        ):
            _phase1_validate_clean_trees("test-branch")
            # Skip phase 2 - no submodule
            _phase3_merge_parent("test-branch")
            _phase4_merge_commit_and_precommit("test-branch")
    finally:
        os.chdir(original_cwd)

    # Verify parent repo file exists in main after merge
    merged_parent_file = parent_repo / "parent-change.txt"
    assert merged_parent_file.exists(), "Parent repo file should exist after merge"

    # Verify merge commit has 2 parents
    parents = subprocess.run(
        ["git", "log", "-1", "--format=%p", "HEAD"],
        cwd=parent_repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    parent_count = len(parents.split())
    assert parent_count == 2, f"Merge commit should have 2 parents, got {parent_count}"

    # Verify branch is ancestor of HEAD
    ancestry_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "test-branch", "HEAD"],
        cwd=parent_repo,
        check=False,
    )
    assert ancestry_check.returncode == 0, "test-branch should be ancestor of HEAD"
