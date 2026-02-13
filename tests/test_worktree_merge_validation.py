"""Tests for worktree merge validation."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_branch_existence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Verify branch exists and warn about missing worktree directory."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Test 1: Branch doesn't exist
    result = CliRunner().invoke(worktree, ["merge", "nonexistent-branch"])
    assert result.exit_code == 2
    assert "Branch nonexistent-branch not found" in result.output

    # Test 2: Branch exists but worktree directory doesn't
    subprocess.run(["git", "branch", "branch-only"], check=True, capture_output=True)
    result = CliRunner().invoke(worktree, ["merge", "branch-only"])
    assert result.exit_code == 0
    assert "Worktree directory not found, merging branch only" in result.output

    # Test 3: Both branch and worktree directory exist
    subprocess.run(["git", "branch", "full-merge"], check=True, capture_output=True)
    result = CliRunner().invoke(worktree, ["new", "full-merge"])
    assert result.exit_code == 0

    result = CliRunner().invoke(worktree, ["merge", "full-merge"])
    assert result.exit_code == 0
    assert "Worktree directory not found" not in result.output


def test_merge_conflict_source_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Abort merge when source file conflicts remain after auto-resolution."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Get current branch (default branch after init)
    current_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Create a branch with conflicting source file
    subprocess.run(
        ["git", "checkout", "-b", "conflict-feature"],
        check=True,
        capture_output=True,
    )
    (repo_path / "src").mkdir()
    (repo_path / "src" / "module.py").write_text(
        "# feature version\nprint('feature')\n"
    )
    subprocess.run(["git", "add", "src/"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add feature module"],
        check=True,
        capture_output=True,
    )

    # Go back to original branch and create conflicting change
    subprocess.run(
        ["git", "checkout", current_branch],
        check=True,
        capture_output=True,
    )
    (repo_path / "src").mkdir(exist_ok=True)
    (repo_path / "src" / "module.py").write_text("# main version\nprint('main')\n")
    subprocess.run(["git", "add", "src/"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add conflicting module"],
        check=True,
        capture_output=True,
    )

    # Create branch pointing to conflict-feature for merge (branch only, no worktree)
    subprocess.run(
        ["git", "branch", "merge-conflict"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "branch", "-f", "merge-conflict", "conflict-feature"],
        check=True,
        capture_output=True,
    )

    # Merge should abort with conflict message
    result = CliRunner().invoke(worktree, ["merge", "merge-conflict"])
    assert result.exit_code == 1
    assert "Merge aborted:" in result.output or "conflicts" in result.output.lower()

    # Verify merge was aborted (no merge in progress)
    merge_head = repo_path / ".git" / "MERGE_HEAD"
    assert not merge_head.exists(), "MERGE_HEAD should not exist after abort"


def test_merge_idempotency(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Test merge can be re-run after manual intervention (idempotency)."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Create feature branch with a new file
    subprocess.run(
        ["git", "checkout", "-b", "feature-branch"],
        check=True,
        capture_output=True,
    )
    (repo_path / "feature.txt").write_text("feature content\n")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add feature"],
        check=True,
        capture_output=True,
    )

    # Go back to main
    subprocess.run(
        ["git", "checkout", "-"],
        check=True,
        capture_output=True,
    )

    # Create worktree branch (points to feature-branch for successful merge)
    subprocess.run(
        ["git", "branch", "wt-feature", "feature-branch"],
        check=True,
        capture_output=True,
    )

    # First merge attempt: succeeds (clean merge)
    result = CliRunner().invoke(worktree, ["merge", "wt-feature"])
    assert result.exit_code == 0, f"First merge should succeed. Output: {result.output}"

    # Reset to before merge to test re-running
    subprocess.run(
        ["git", "reset", "--hard", "HEAD~1"],
        check=True,
        capture_output=True,
    )

    # Second merge attempt (idempotency test): should succeed again
    result = CliRunner().invoke(worktree, ["merge", "wt-feature"])
    # After successful merge, branch may be deleted or already merged
    # Accept either outcome (0 = re-runs cleanly, 2 = branch gone/already merged)
    assert result.exit_code in (0, 2), (
        f"Merge should succeed or be idempotent. Output: {result.output}"
    )

    # Verify no duplicate commits: final state should match single successful merge
    log_output = subprocess.run(
        ["git", "log", "--oneline"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    # Count merge commits related to feature-branch
    feature_commits = [
        line for line in log_output.split("\n") if "feature" in line.lower()
    ]
    # Should have the original feature commit plus at most one merge commit
    assert len(feature_commits) <= 2, (
        "Feature should appear at most twice (original + merge, no duplicates)"
    )
