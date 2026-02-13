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


def test_merge_conflict_agent_core(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify agent-core conflict auto-resolution.

    Behavior:
    - When agent-core appears in conflict list during merge
    - Auto-resolve using `git checkout --ours agent-core`
    - Stage the resolution with `git add agent-core`
    - Remove agent-core from the remaining conflict list
    - Rationale: submodule already merged in Phase 2, conflict is stale
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

    # Add a change on the worktree branch to a non-agent-core file
    _commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")

    # Also update submodule on branch
    (worktree_path / "agent-core" / "branch-change.txt").write_text("branch change\n")
    subprocess.run(
        ["git", "add", "branch-change.txt"],
        cwd=worktree_path / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Branch change in submodule"],
        cwd=worktree_path / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update agent-core submodule on branch"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add a conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    _commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")

    # Also update agent-core on main to different commit
    (repo_with_submodule / "agent-core" / "main-change.txt").write_text("main change\n")
    subprocess.run(
        ["git", "add", "main-change.txt"],
        cwd=repo_with_submodule / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Main change in submodule"],
        cwd=repo_with_submodule / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update agent-core on main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Check that agent-core is NOT in unmerged paths (it should have been auto-resolved)
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    conflicts = [c for c in unmerged.stdout.strip().split("\n") if c.strip()]
    assert "agent-core" not in conflicts, (
        f"agent-core should be auto-resolved, but found in conflicts: {conflicts}"
    )

    # Verify MERGE_HEAD is set (merge is in progress)
    merge_head = subprocess.run(
        ["git", "rev-parse", "MERGE_HEAD"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert merge_head.returncode == 0, "MERGE_HEAD should be set"


def _commit_file(path: Path, filename: str, content: str, message: str) -> None:
    """Create, stage, and commit a file."""
    (path / filename).write_text(content)
    subprocess.run(["git", "add", filename], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message], cwd=path, check=True, capture_output=True
    )
