"""Tests for edify._git changes command."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.git_cli import git_group
from tests.pytest_helpers import add_submodule, create_submodule_origin, init_repo_at


def _add_submodule(parent: Path, tmp_path: Path, sub_name: str) -> Path:
    """Add a submodule using canonical pytest_helpers."""
    origin = create_submodule_origin(tmp_path, sub_name)
    add_submodule(parent, origin, sub_name)
    subprocess.run(
        ["git", "-C", str(parent), "commit", "-m", f"add submodule {sub_name}"],
        capture_output=True,
        check=True,
    )
    return parent / sub_name


def test_git_changes_clean_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean repo produces 'Tree is clean.' output with exit 0."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_at(repo)
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "Tree is clean." in result.output


def test_git_changes_dirty_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dirty parent produces ## Parent section with filename and diff."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo_at(repo)
    monkeypatch.chdir(repo)

    # Create a tracked file change (modify README.md which is tracked)
    (repo / "README.md").write_text("modified content")

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "## Parent" in result.output
    # Status output includes README.md
    assert "README.md" in result.output
    # Diff output should also be present
    assert "modified content" in result.output
    assert "diff" in result.output.lower()


def test_git_changes_with_submodule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dirty submodule produces ## Submodule: section with prefixed paths."""
    parent = tmp_path / "parent"
    parent.mkdir()
    init_repo_at(parent)
    sub_path = _add_submodule(parent, tmp_path, "plugin")
    monkeypatch.chdir(parent)

    # Make the submodule dirty: add a new untracked file (clear "?? " prefix in status)
    (sub_path / "new_file.txt").write_text("untracked content in submodule")

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "## Submodule: plugin" in result.output
    # Status line must show prefixed path: plugin/new_file.txt not bare new_file.txt
    assert "plugin/new_file.txt" in result.output
    # Verify that any status line for new_file.txt includes the submodule prefix
    lines = result.output.splitlines()
    for line in lines:
        if "new_file.txt" in line and not line.strip().startswith("#"):
            assert "plugin/" in line


def test_git_changes_clean_submodule_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean submodule section omitted when parent is dirty."""
    parent = tmp_path / "parent"
    parent.mkdir()
    init_repo_at(parent)
    _add_submodule(parent, tmp_path, "plugin")
    monkeypatch.chdir(parent)

    # Make only the parent dirty (not the submodule)
    (parent / "README.md").write_text("parent change")

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "## Parent" in result.output
    # Submodule is clean — its section must not appear
    assert "## Submodule" not in result.output
