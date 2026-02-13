"""Test for worktree merge jobs.md conflict auto-resolution."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_conflict_jobs_md(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Auto-resolve jobs.md conflict with warning."""
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

    # Create agents dir and initial jobs.md on both sides
    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (worktree_path / "agents").mkdir(exist_ok=True)

    # Main: jobs.md with plan A status
    (repo_with_submodule / "agents" / "jobs.md").write_text(
        "# Jobs\n\n| Plan | Status |\n|------|--------|\n| plan-a | planned |\n"
    )
    subprocess.run(
        ["git", "add", "agents/jobs.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add jobs.md with plan A"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Worktree: start with same
    (worktree_path / "agents" / "jobs.md").write_text(
        "# Jobs\n\n| Plan | Status |\n|------|--------|\n| plan-a | planned |\n"
    )
    subprocess.run(
        ["git", "add", "agents/jobs.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add jobs.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Worktree: update plan A status
    (worktree_path / "agents" / "jobs.md").write_text(
        "# Jobs\n\n| Plan | Status |\n|------|--------|\n| plan-a | complete |\n"
    )
    subprocess.run(
        ["git", "add", "agents/jobs.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update plan A status in worktree"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Main: update jobs.md (different change, will conflict)
    (repo_with_submodule / "agents" / "jobs.md").write_text(
        "# Jobs\n\n| Plan | Status |\n|------|--------|\n| plan-a | designed |\n"
    )
    subprocess.run(
        ["git", "add", "agents/jobs.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update plan A status on main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Verify jobs.md is NOT in unmerged paths (auto-resolved)
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    conflicts = [c for c in unmerged.stdout.strip().split("\n") if c.strip()]
    msg = f"agents/jobs.md should be auto-resolved, but found in conflicts: {conflicts}"
    assert "agents/jobs.md" not in conflicts, msg

    # Verify output contains warning about jobs.md resolution
    assert "jobs.md" in result.output, (
        f"Output should mention jobs.md resolution, got: {result.output}"
    )
    assert "kept ours" in result.output, (
        f"Output should mention 'kept ours', got: {result.output}"
    )


def _commit_file(path: Path, filename: str, content: str, message: str) -> None:
    """Create, stage, and commit a file."""
    (path / filename).write_text(content)
    subprocess.run(["git", "add", filename], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message], cwd=path, check=True, capture_output=True
    )
