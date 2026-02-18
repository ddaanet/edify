"""Tests for MERGE_HEAD detection in worktree merge operations."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.merge import _detect_merge_state, _phase4_merge_commit_and_precommit


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


def test_merge_resumes_from_parent_resolved(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge resumes from parent_resolved state.

    Repo has MERGE_HEAD with no unresolved conflicts. merge(slug) should:
    - Exit with code 0
    - Create a merge commit (HEAD has 2+ parents)
    - Not raise CalledProcessError from clean tree check
    """
    from claudeutils.worktree.merge import merge

    monkeypatch.chdir(repo_with_submodule)

    # Set up initial commit on main
    (repo_with_submodule / "main.txt").write_text("main content\n")
    subprocess.run(["git", "add", "main.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        check=True,
        capture_output=True,
    )

    # Create branch with unique file
    subprocess.run(
        ["git", "checkout", "-b", "feature-branch"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "branch-file.txt").write_text("branch content\n")
    subprocess.run(["git", "add", "branch-file.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add branch file"],
        check=True,
        capture_output=True,
    )

    # Switch back to main and make conflicting change in different file
    subprocess.run(
        ["git", "checkout", "main"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "other.txt").write_text("other content\n")
    subprocess.run(["git", "add", "other.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add other file"],
        check=True,
        capture_output=True,
    )

    # Start merge manually (not committed yet)
    merge_result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "feature-branch"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert merge_result.returncode == 0, "Merge should succeed with auto-resolution"

    # Verify no unresolved conflicts
    conflicts = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert (
        not conflicts.stdout.strip()
    ), f"Expected no conflicts, got: {conflicts.stdout}"

    # Verify MERGE_HEAD exists
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_check.returncode == 0, "MERGE_HEAD should exist"

    # Invoke merge() - should succeed and create merge commit
    merge("feature-branch")

    # Verify MERGE_HEAD is gone
    merge_head_after = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_after.returncode != 0, (
        "MERGE_HEAD should be removed after merge()"
    )

    # Verify merge commit was created (HEAD has 2+ parents)
    log_output = subprocess.run(
        ["git", "cat-file", "-p", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    parent_count = len(
        [line for line in log_output.stdout.split("\n") if line.startswith("parent ")]
    )
    assert parent_count >= 2, (
        f"Expected merge commit with 2+ parents, got {parent_count}"
    )


def test_merge_continues_to_phase3_when_submodule_conflicts(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge routes submodule_conflicts state to Phase 3.

    When agent-core has MERGE_HEAD (mid-merge), calling merge(slug) should:
    - Detect submodule_conflicts state (not clean)
    - Skip the clean-tree check
    - Route to Phase 3 (merge parent)
    - Exit with code 0 or 3 (not 1 from clean-tree check)
    """
    from claudeutils.worktree.merge import merge

    monkeypatch.chdir(repo_with_submodule)

    # Set up initial commit on main
    (repo_with_submodule / "main.txt").write_text("main content\n")
    subprocess.run(["git", "add", "main.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        check=True,
        capture_output=True,
    )

    # Create branch to merge
    subprocess.run(
        ["git", "checkout", "-b", "test-branch"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "branch.txt").write_text("branch content\n")
    subprocess.run(["git", "add", "branch.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add branch file"],
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "checkout", "main"],
        check=True,
        capture_output=True,
    )

    # Create a conflicting commit on agent-core
    agent_core = repo_with_submodule / "agent-core"
    (agent_core / "feature.py").write_text("main feature\n")
    subprocess.run(
        ["git", "-C", str(agent_core), "add", "feature.py"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(agent_core), "commit", "-m", "Main feature"],
        check=True,
        capture_output=True,
    )

    # Create another commit on agent-core to merge
    subprocess.run(
        ["git", "-C", str(agent_core), "checkout", "-b", "ac-feature"],
        check=True,
        capture_output=True,
    )
    (agent_core / "feature.py").write_text("branch feature\n")
    subprocess.run(
        ["git", "-C", str(agent_core), "add", "feature.py"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(agent_core), "commit", "-m", "Branch feature"],
        check=True,
        capture_output=True,
    )

    # Switch back to main on agent-core
    subprocess.run(
        ["git", "-C", str(agent_core), "checkout", "main"],
        check=True,
        capture_output=True,
    )

    # Put agent-core in mid-merge state with NO conflicts
    merge_result = subprocess.run(
        ["git", "-C", str(agent_core), "merge", "--no-commit", "--no-ff", "ac-feature"],
        capture_output=True,
        text=True,
        check=False,
    )
    # The merge should succeed (no real conflicts, just different content we allow)
    if merge_result.returncode != 0:
        # If there are conflicts, resolve them
        subprocess.run(
            ["git", "-C", str(agent_core), "checkout", "--ours", "feature.py"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(agent_core), "add", "feature.py"],
            check=True,
            capture_output=True,
        )

    # Verify agent-core has MERGE_HEAD
    merge_head_check = subprocess.run(
        ["git", "-C", str(agent_core), "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_check.returncode == 0, "agent-core should have MERGE_HEAD"

    # Test _detect_merge_state directly - should return submodule_conflicts after GREEN
    # For RED, it will return clean (test will fail)
    state = _detect_merge_state("test-branch")
    assert state == "submodule_conflicts", (
        f"Expected submodule_conflicts state, got {state}"
    )

    # Invoke merge() via CliRunner - should NOT exit with code 1 from clean-tree check
    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "test-branch"])

    assert result.exit_code in (0, 3), (
        f"Expected exit code 0 or 3, got {result.exit_code}. "
        f"Output: {result.output}"
    )


def test_merge_reports_and_exits_3_when_parent_conflicts(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test merge exits with code 3 when parent merge has unresolved conflicts.

    Repo has MERGE_HEAD with unresolved conflicts. merge(slug) should:
    - Exit with code 3
    - Not run --abort or clean
    - MERGE_HEAD still exists after call
    - Output contains name of conflicted file
    - No traceback in output
    """
    monkeypatch.chdir(repo_with_submodule)

    # Set up initial commit on main
    (repo_with_submodule / "main.txt").write_text("main content\n")
    subprocess.run(["git", "add", "main.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        check=True,
        capture_output=True,
    )

    # Create branch with conflicting content in same file
    subprocess.run(
        ["git", "checkout", "-b", "conflict-branch"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "src").mkdir(parents=True, exist_ok=True)
    (repo_with_submodule / "src" / "feature.py").write_text("branch version\n")
    subprocess.run(["git", "add", "src/feature.py"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add feature on branch"],
        check=True,
        capture_output=True,
    )

    # Switch back to main and create different content in same file
    subprocess.run(
        ["git", "checkout", "main"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "src").mkdir(parents=True, exist_ok=True)
    (repo_with_submodule / "src" / "feature.py").write_text("main version\n")
    subprocess.run(["git", "add", "src/feature.py"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add feature on main"],
        check=True,
        capture_output=True,
    )

    # Start merge manually (not committed, will have conflicts)
    merge_result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "conflict-branch"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Verify MERGE_HEAD exists
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_check.returncode == 0, "MERGE_HEAD should exist"

    # Verify unresolved conflicts
    conflicts = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert conflicts.stdout.strip(), "Expected unresolved conflicts"

    # Invoke merge() via CLI - should exit with code 3
    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "conflict-branch"])

    assert result.exit_code == 3, (
        f"Expected exit code 3, got {result.exit_code}. Output: {result.output}"
    )

    # Verify MERGE_HEAD still exists (no --abort was run)
    merge_head_after = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_after.returncode == 0, (
        "MERGE_HEAD should still exist after merge()"
    )

    # Verify output contains conflicted filename
    assert "feature.py" in result.output, (
        f"Expected 'feature.py' in output, got: {result.output}"
    )

    # Verify no traceback
    assert "Traceback" not in result.output, (
        f"Expected no traceback, got: {result.output}"
    )
