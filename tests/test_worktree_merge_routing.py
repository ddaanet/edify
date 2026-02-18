"""Tests for merge() routing logic based on merge state detection."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.merge import _detect_merge_state, merge
from claudeutils.worktree.utils import _is_branch_merged


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
        [
            line
            for line in log_output.stdout.split("\n")
            if line.startswith("parent ")
        ]
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

    # Test _detect_merge_state directly
    # should return submodule_conflicts after GREEN
    state = _detect_merge_state("test-branch")
    assert state == "submodule_conflicts", (
        f"Expected submodule_conflicts state, got {state}"
    )

    # Invoke merge() via CliRunner
    # should NOT exit with code 1 from clean-tree check
    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "test-branch"])

    assert result.exit_code in (0, 3), (
        f"Expected exit code 0 or 3, got {result.exit_code}. "
        f"Output: {result.output}"
    )


def test_merge_clean_state_runs_full_pipeline(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge(clean) routes through all 4 phases.

    When no merge is in progress and branch is not merged, merge(slug) should:
    - Detect 'clean' state
    - Run Phase 1 (validate clean trees)
    - Run Phase 2 (resolve submodule if needed)
    - Run Phase 3 (merge parent)
    - Run Phase 4 (commit and precommit)
    - Result: HEAD has exactly 2 parents (merge commit), exit code 0
    - _is_branch_merged(slug) returns True after call
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

    # Create branch with unique file
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

    # Switch back to main and make a different commit (diverge)
    subprocess.run(
        ["git", "checkout", "main"],
        check=True,
        capture_output=True,
    )
    (repo_with_submodule / "main2.txt").write_text("main commit 2\n")
    subprocess.run(["git", "add", "main2.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Second commit on main"],
        check=True,
        capture_output=True,
    )

    # Verify no MERGE_HEAD exists (clean state)
    merge_head_before = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert (
        merge_head_before.returncode != 0
    ), "Should start in clean state (no MERGE_HEAD)"

    # Verify branch not merged yet
    assert not _is_branch_merged("test-branch"), "Branch should not be merged yet"

    # Invoke merge() - should route through all 4 phases for clean state
    merge("test-branch")

    # Verify merge commit was created: HEAD has exactly 2 parents
    log_output = subprocess.run(
        ["git", "cat-file", "-p", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    parent_lines = [
        line for line in log_output.split("\n") if line.startswith("parent ")
    ]
    assert len(parent_lines) == 2, (
        f"Expected exactly 2 parents (merge commit), got {len(parent_lines)}"
    )

    # Verify merge commit message
    commit_msg = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert commit_msg.startswith("🔀 Merge"), (
        f"Expected merge commit message starting with '🔀 Merge', got: {commit_msg}"
    )

    # Verify branch is now merged
    assert _is_branch_merged("test-branch"), "Branch should be merged after merge()"

    # Verify MERGE_HEAD is gone
    merge_head_after = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert (
        merge_head_after.returncode != 0
    ), "MERGE_HEAD should be removed after merge()"


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
    subprocess.run(
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
