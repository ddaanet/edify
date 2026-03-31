"""Tests for worktree submodule initialization."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree


def test_new_submodule(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    setup_repo_with_submodule: Callable[[Path, Callable[[Path], None]], None],
) -> None:
    """Verify new subcommand initializes submodule and creates branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path, init_repo)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-feature"])

    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    submodule_path = worktree_path / "plugin"
    assert submodule_path.exists()

    result = subprocess.run(
        [
            "git",
            "-C",
            str(submodule_path),
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    branch_name = result.stdout.strip()
    assert branch_name == "test-feature"

    result = subprocess.run(
        ["git", "-C", str(submodule_path), "branch", "--list"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout


def test_new_worktree_submodule(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    setup_repo_with_submodule: Callable[[Path, Callable[[Path], None]], None],
) -> None:
    """Verify submodule uses worktree-based approach with branch reuse."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path, init_repo)

    runner = CliRunner()

    result = runner.invoke(worktree, ["new", "--branch", "feature-x"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "feature-x"
    assert worktree_path.exists()

    submodule_path = worktree_path / "plugin"
    assert submodule_path.exists()

    result = subprocess.run(
        [
            "git",
            "-C",
            str(submodule_path),
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "feature-x"

    result = subprocess.run(
        ["git", "-C", str(repo_path / "plugin"), "worktree", "list"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert str(submodule_path) in result.stdout

    result = runner.invoke(worktree, ["new", "--branch", "feature-y"])
    assert result.exit_code == 0

    worktree_path2 = container_path / "feature-y"
    submodule_path2 = worktree_path2 / "plugin"
    assert submodule_path2.exists()

    result = subprocess.run(
        [
            "git",
            "-C",
            str(submodule_path2),
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "feature-y"

    subprocess.run(
        ["git", "-C", str(repo_path / "plugin"), "branch", "existing-feature"],
        check=True,
        capture_output=True,
    )

    result = runner.invoke(worktree, ["new", "--branch", "existing-feature"])
    assert result.exit_code == 0

    worktree_path3 = container_path / "existing-feature"
    submodule_path3 = worktree_path3 / "plugin"
    assert submodule_path3.exists()

    result = subprocess.run(
        [
            "git",
            "-C",
            str(submodule_path3),
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "existing-feature"


def test_rm_deletes_submodule_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    setup_repo_with_submodule: Callable[[Path, Callable[[Path], None]], None],
) -> None:
    """Rm deletes both parent and submodule branches."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path, init_repo)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-feature"])
    assert result.exit_code == 0

    # Precondition: submodule branch exists
    sub_branch = subprocess.run(
        ["git", "-C", "plugin", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in sub_branch.stdout, "submodule branch should exist"

    result = runner.invoke(worktree, ["rm", "test-feature"])
    assert result.exit_code == 0

    # Parent branch gone
    parent_branch = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in parent_branch.stdout

    # Submodule branch gone
    sub_branch = subprocess.run(
        ["git", "-C", "plugin", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in sub_branch.stdout, "submodule branch should be deleted"

    # Worktree directory removed
    container_path = tmp_path / "repo-wt"
    assert not (container_path / "test-feature").exists()
