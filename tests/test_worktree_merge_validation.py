"""Tests for worktree merge validation."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_branch_existence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
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
