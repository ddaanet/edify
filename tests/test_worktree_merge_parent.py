"""Tests for worktree merge parent operations."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_parent_initiate(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
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

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

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
    commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")

    # Switch back to main and add a different change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    git_status = subprocess.run(
        ["git", "status"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )

    # After merge completes, MERGE_HEAD should not exist and status should be clean
    merge_head = subprocess.run(
        ["git", "rev-parse", "MERGE_HEAD"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert merge_head.returncode != 0, (
        "MERGE_HEAD should not exist after merge completes. "
        f"Status:\n{git_status.stdout}"
    )

    # Verify merge was completed (working tree clean)
    assert (
        "nothing to commit" in git_status.stdout
        or "working tree clean" in git_status.stdout
    ), f"Tree should be clean after merge. Status:\n{git_status.stdout}"


def test_merge_precommit_validation(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Verify merge commits staged changes and runs precommit validation.

    Behavior:
    - After successful merge (no conflicts): check for staged changes
    - Run `git diff --cached --quiet` (exit ≠ 0 means changes staged)
    - If staged changes: `git commit -m "🔀 Merge <slug>"`
    - Then run `just precommit` with exit code capture
    - If precommit passes (exit 0): exit 0 with success message
    - If precommit fails (exit ≠ 0): exit 1 with failure message
    """
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

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
    commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")

    # Switch back to main and add a different change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Verify merge commit was created with proper message
    merge_commit = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        check=True,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert merge_commit.stdout.strip().startswith("🔀 Merge"), (
        f"Merge commit message should start with '🔀 Merge', got: {merge_commit.stdout}"
    )

    # Verify git status is clean (no staged changes)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert not status.stdout.strip(), (
        f"Tree should be clean after merge, got: {status.stdout}"
    )


def test_merge_precommit_failure(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Test Phase 4: merge succeeds but precommit fails.

    Behavior:
    - After successful merge (no conflicts): check for staged changes
    - Run `git diff --cached --quiet` (exit ≠ 0 means changes staged)
    - If staged changes: `git commit -m "🔀 Merge <slug>"`
    - Then run `just precommit` with exit code capture
    - If precommit fails (exit ≠ 0): exit 1 with failure message
    """
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

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
    commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")

    # Switch back to main and add a different change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")

    # Mock precommit to fail
    original_run = subprocess.run

    def mock_run_with_failure(
        *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        cmd = args[0] if args else kwargs.get("args")
        if (
            isinstance(cmd, list)
            and cmd
            and cmd[0] == "just"
            and len(cmd) > 1
            and cmd[1] == "precommit"
        ):
            mock_result: subprocess.CompletedProcess[str] = subprocess.CompletedProcess(
                cmd, returncode=1
            )
            mock_result.stdout = ""
            mock_result.stderr = "Precommit validation failed"
            return mock_result
        # Type system limitation: can't type *args/**kwargs forwarding perfectly
        return original_run(*args, **kwargs)  # type: ignore[call-overload,no-any-return]

    monkeypatch.setattr(subprocess, "run", mock_run_with_failure)

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 1, (
        f"merge should fail when precommit fails: {result.output}"
    )
    assert "Precommit" in result.output or "failed" in result.output.lower(), (
        f"Error message should mention precommit failure: {result.output}"
    )

    # Verify merge was completed (MERGE_HEAD should not exist)
    merge_head = subprocess.run(
        ["git", "rev-parse", "MERGE_HEAD"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert merge_head.returncode != 0, (
        "MERGE_HEAD should not exist after merge completes, even if precommit fails"
    )
