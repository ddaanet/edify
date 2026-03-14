"""Tests for claudeutils.git shared helpers."""

import os
import subprocess
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from claudeutils.git import _fail, _git_ok, _is_submodule_dirty, discover_submodules
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
