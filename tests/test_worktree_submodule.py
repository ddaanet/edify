"""Tests for worktree submodule initialization."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _setup_repo_with_submodule(
    repo_path: Path, init_repo: Callable[[Path], None]
) -> None:
    """Set up a test repo with a simulated submodule (gitlink)."""
    init_repo(repo_path)

    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    subprocess.run(
        ["git", "init"], cwd=agent_core_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    (agent_core_path / "core.txt").write_text("core content")
    subprocess.run(
        ["git", "add", "core.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial core commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    gitmodules_path = repo_path / ".gitmodules"
    gitmodules_path.write_text(
        '[submodule "agent-core"]\n\tpath = agent-core\n\turl = ./agent-core\n'
    )

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result.stdout.strip()

    subprocess.run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{commit_hash},agent-core",
        ],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", ".gitmodules"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(
        ["git", "add", ".gitignore"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def test_new_submodule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify new subcommand initializes submodule and creates branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path, init_repo)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    submodule_path = worktree_path / "agent-core"
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify submodule uses worktree-based approach with branch reuse."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path, init_repo)

    runner = CliRunner()

    result = runner.invoke(worktree, ["new", "feature-x"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "feature-x"
    assert worktree_path.exists()

    submodule_path = worktree_path / "agent-core"
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
        ["git", "-C", str(repo_path / "agent-core"), "worktree", "list"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert str(submodule_path) in result.stdout

    result = runner.invoke(worktree, ["new", "feature-y"])
    assert result.exit_code == 0

    worktree_path2 = container_path / "feature-y"
    submodule_path2 = worktree_path2 / "agent-core"
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
        ["git", "-C", str(repo_path / "agent-core"), "branch", "existing-feature"],
        check=True,
        capture_output=True,
    )

    result = runner.invoke(worktree, ["new", "existing-feature"])
    assert result.exit_code == 0

    worktree_path3 = container_path / "existing-feature"
    submodule_path3 = worktree_path3 / "agent-core"
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
