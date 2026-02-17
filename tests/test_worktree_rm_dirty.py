"""Tests for dirty tree checks in worktree rm."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.utils import _is_parent_dirty, _is_submodule_dirty
from tests.fixtures_worktree import _create_worktree


def test_is_parent_dirty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Returns False when clean, True when untracked or staged."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    assert _is_parent_dirty() is False

    (repo_path / "dirty.txt").write_text("dirty")
    assert _is_parent_dirty() is True

    subprocess.run(["git", "add", "dirty.txt"], check=True)
    assert _is_parent_dirty() is True


def test_is_submodule_dirty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Returns False when no submodule, False when clean, True when dirty."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    assert _is_submodule_dirty() is False

    original_run = subprocess.run

    def mock_run_clean(*args: object, **kwargs: object) -> object:
        cmd = args[0] if args else kwargs.get("args")
        if isinstance(cmd, list) and "-C" in cmd and "agent-core" in cmd:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="", stderr=""
            )
        return original_run(*args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(subprocess, "run", mock_run_clean)
    (repo_path / "agent-core").mkdir()
    assert _is_submodule_dirty() is False

    def mock_run_dirty(*args: object, **kwargs: object) -> object:
        cmd = args[0] if args else kwargs.get("args")
        if isinstance(cmd, list) and "-C" in cmd and "agent-core" in cmd:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout=" M file.txt\n", stderr=""
            )
        return original_run(*args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(subprocess, "run", mock_run_dirty)
    assert _is_submodule_dirty() is True


def test_rm_blocks_on_dirty_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Blocks removal if parent repo has uncommitted changes."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    (repo_path / "dirty.txt").write_text("dirty content")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 2
    assert "uncommitted" in result.output.lower() or "parent" in result.output.lower()


def test_rm_blocks_on_dirty_submodule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Blocks removal if submodule has uncommitted changes."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    monkeypatch.setattr(
        "claudeutils.worktree.cli._is_submodule_dirty",
        lambda: True,
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 2
    assert (
        "uncommitted" in result.output.lower() or "submodule" in result.output.lower()
    )


def test_rm_force_bypasses_dirty_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Force flag bypasses dirty check."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    (repo_path / "dirty.txt").write_text("dirty")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--force", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
