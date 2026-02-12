"""Tests for worktree rm subcommand."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _init_repo(repo_path: Path) -> None:
    """Initialize git repo with user config and initial commit."""
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "README.md").write_text("test")
    subprocess.run(
        ["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def _create_worktree(repo_path: Path, slug: str) -> Path:
    """Create worktree and return its path."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", slug])
    assert result.exit_code == 0
    container_path = repo_path.parent / f"{repo_path.name}-wt"
    return container_path / slug


def _branch_exists(name: str) -> bool:
    """Check if branch exists."""
    result = subprocess.run(
        ["git", "branch", "--list", name],
        capture_output=True,
        text=True,
        check=True,
    )
    return name in result.stdout


def test_rm_basic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Removes worktree directory and branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature")
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "removed" in result.output.lower()


def test_rm_dirty_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Warns about uncommitted changes but proceeds with removal."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature")
    (worktree_path / "newfile.txt").write_text("uncommitted")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "uncommitted" in result.output.lower() or "warning" in result.output.lower()


def test_rm_branch_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cleans up branch when directory removed externally."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature")
    assert _branch_exists("test-feature")

    subprocess.run(["rm", "-rf", str(worktree_path)], check=True, capture_output=True)
    assert not worktree_path.exists()
    assert _branch_exists("test-feature")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not _branch_exists("test-feature")
    assert (
        "error" not in result.output.lower()
        or "no such file" not in result.output.lower()
    )
