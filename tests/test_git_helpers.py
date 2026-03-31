"""Tests for edify.git shared helpers."""

import os
import subprocess
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from edify.git import (
    _fail,
    _git_ok,
    _is_dirty,
    _is_submodule_dirty,
    discover_submodules,
    git_status,
)
from tests.pytest_helpers import init_repo_at as _init_repo


def test_git_ok_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """_git_ok returns True for a valid git command in a valid repo."""
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert _git_ok("status") is True


def test_git_ok_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """_git_ok returns False for an invalid git command."""
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert _git_ok("log", "--invalidflag") is False


def test_fail_exits() -> None:
    """_fail raises SystemExit with the given code and prints msg to stdout."""

    @click.command()
    def cmd() -> None:
        _fail("error msg", code=2)

    runner = CliRunner()
    result = runner.invoke(cmd)
    assert result.exit_code == 2
    assert "error msg" in result.output


def test_discover_submodules_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """discover_submodules returns [] in a repo without submodules."""
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert discover_submodules() == []


def test_discover_submodules_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """discover_submodules returns submodule path in a repo with a submodule."""
    submod_remote = tmp_path / "submod-remote"
    _init_repo(submod_remote)

    parent = tmp_path / "parent"
    _init_repo(parent)
    monkeypatch.chdir(parent)

    env = {
        **os.environ,
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "protocol.file.allow",
        "GIT_CONFIG_VALUE_0": "always",
    }
    subprocess.run(
        ["git", "submodule", "add", str(submod_remote), "submod-name"],
        capture_output=True,
        check=True,
        cwd=str(parent),
        env=env,
    )
    subprocess.run(
        ["git", "-C", str(parent), "add", "."],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(parent), "commit", "-m", "add submodule"],
        capture_output=True,
        check=True,
    )

    result = discover_submodules()
    assert result == ["submod-name"]


@pytest.mark.parametrize(
    "scenario",
    ["clean", "dirty", "nonexistent"],
)
def test_is_submodule_dirty_parametrized(tmp_path: Path, scenario: str) -> None:
    """Tests _is_submodule_dirty with clean, dirty, and nonexistent paths."""
    if scenario == "nonexistent":
        result = _is_submodule_dirty(str(tmp_path / "does-not-exist"))
        assert result is False
        return

    submod = tmp_path / "mysubmod"
    _init_repo(submod)

    if scenario == "clean":
        result = _is_submodule_dirty(str(submod))
        assert result is False
    elif scenario == "dirty":
        (submod / "dirty.txt").write_text("dirty")
        result = _is_submodule_dirty(str(submod))
        assert result is True


# Cycle 2.1: git_status strip bug


def test_git_status_preserves_porcelain_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """git_status preserves leading space in XY porcelain code."""
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Create a tracked file, then modify without staging
    f = tmp_path / "a.py"
    f.write_text("original\n")
    subprocess.run(
        ["git", "add", "a.py"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "add a"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    f.write_text("modified\n")

    status = git_status()
    # Unstaged modification: XY = " M" (space-M), line = " M a.py"
    assert status.startswith(" M "), f"Expected ' M ...', got {status!r}"

    # Clean repo returns empty
    subprocess.run(
        ["git", "checkout", "--", "a.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    assert git_status() == ""


# Cycle 4.1: _is_dirty exclude_path with unstaged modifications


def test_is_dirty_excludes_path_with_unstaged_modifications(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exclude path filters unstaged modifications with space prefix."""
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Create a file in subdir/, add, commit, then modify without staging
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    f = subdir / "file.py"
    f.write_text("original\n")
    subprocess.run(
        ["git", "add", "subdir/file.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add file"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    f.write_text("modified\n")

    # Unstaged modification produces " M subdir/file.py" in porcelain
    # exclude_path="subdir" should exclude it
    assert _is_dirty(exclude_path="subdir") is False


def test_is_dirty_includes_files_outside_excluded_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_is_dirty(exclude_path=X) includes files not under X."""
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Create files in "other" and "subdir", commit, modify "other"
    other = tmp_path / "other"
    other.mkdir()
    f = other / "file.py"
    f.write_text("original\n")
    subprocess.run(
        ["git", "add", "other/file.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add file"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    f.write_text("modified\n")

    # Unstaged modification to "other/file.py" should NOT be excluded
    assert _is_dirty(exclude_path="subdir") is True
