"""Tests for worktree new command - creation and collision handling."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_new_collision_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Reuses existing branch without error."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0
    assert (tmp_path / "repo-wt" / "test-feature").exists()


def test_new_directory_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects existing directory collision."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    container_path = tmp_path / "repo-wt"
    container_path.mkdir()
    (container_path / "test-feature").mkdir()

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 1
    assert "existing" in result.output.lower() or "directory" in result.output.lower()
    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in result.stdout


def test_new_basic_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates worktree with new branch in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0
    assert "repo-wt/test-feature" in result.output

    worktree_path = tmp_path / "repo-wt" / "test-feature"
    assert worktree_path.exists()

    branch_result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in branch_result.stdout

    head_result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in head_result.stdout


def test_new_command_sibling_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates multiple worktrees in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-wt"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    assert (container_path / "test-wt").exists()
    assert "repo-wt/test-wt" in result.output

    branch_result = subprocess.run(
        ["git", "branch", "--list", "test-wt"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-wt" in branch_result.stdout

    result = runner.invoke(worktree, ["new", "another-wt"])
    assert result.exit_code == 0
    assert (container_path / "another-wt").exists()
    assert "repo-wt/another-wt" in result.output

    subprocess.run(
        ["git", "branch", "existing-branch"], check=True, capture_output=True
    )
    result = runner.invoke(worktree, ["new", "existing-branch"])
    assert result.exit_code == 0
    assert (container_path / "existing-branch").exists()
    assert "repo-wt/existing-branch" in result.output


def test_new_cleans_up_on_git_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Cleans up empty directory when git worktree add fails."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    monkeypatch.setattr(
        "claudeutils.worktree.cli._setup_worktree",
        lambda *a, **kw: (_ for _ in ()).throw(
            subprocess.CalledProcessError(255, "git worktree add")
        ),
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code != 0

    container = repo_path.parent / f"{repo_path.name}-wt"
    wt = container / "test-feature"
    assert not wt.exists(), "worktree directory should be cleaned up"
    assert not container.exists(), "empty container should be cleaned up"
