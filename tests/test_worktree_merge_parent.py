"""Tests for worktree merge parent operations."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_parent_initiate(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify parent merge initiation with conflict detection.

    Behavior:
    - Run `git merge --no-commit --no-ff <slug>` with check=False
    - Capture exit code and output
    - When exit code 0: merge clean, proceed to commit
    - When exit code ≠ 0: conflicts occurred, get conflict list from
      `git diff --name-only --diff-filter=U`
    - Store conflict list for auto-resolution logic
    """
    monkeypatch.chdir(repo_with_submodule)

    _commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    subprocess.run(
        ["git", "branch", "test-merge"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0, f"new command should succeed, got: {result.output}"

    worktree_path = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "test-merge"
    )

    # Add a change on the worktree branch
    _commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")

    # Switch back to main and add a different change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    _commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    git_status = subprocess.run(
        ["git", "status"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )

    merge_head = subprocess.run(
        ["git", "rev-parse", "MERGE_HEAD"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert merge_head.returncode == 0, (
        f"MERGE_HEAD missing. Status:\n{git_status.stdout}\nStderr: {merge_head.stderr}"
    )




def _commit_file(path: Path, filename: str, content: str, message: str) -> None:
    """Create, stage, and commit a file."""
    (path / filename).write_text(content)
    subprocess.run(["git", "add", filename], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message], cwd=path, check=True, capture_output=True
    )
