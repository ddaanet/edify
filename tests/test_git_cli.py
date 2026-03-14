"""Tests for claudeutils._git changes command."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.git_cli import git_group


def _init_repo(path: Path) -> None:
    """Initialize a git repo with an initial commit."""
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Test"],
        capture_output=True,
        check=True,
    )
    readme = path / "README.md"
    readme.write_text("init")
    subprocess.run(
        ["git", "-C", str(path), "add", "."], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "-C", str(path), "commit", "-m", "init"],
        capture_output=True,
        check=True,
    )


def _add_submodule_gitlink(parent: Path, sub_name: str) -> Path:
    """Register sub_name as a gitlink submodule inside parent without cloning.

    Uses git plumbing (update-index --cacheinfo 160000) so the submodule repo
    stays as an independent git repo in place rather than being cloned.
    """
    sub_path = parent / sub_name
    sub_path.mkdir()

    # Initialize the submodule as its own git repo
    subprocess.run(["git", "init", str(sub_path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(sub_path), "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(sub_path), "config", "user.name", "Test"],
        capture_output=True,
        check=True,
    )
    (sub_path / "README.md").write_text("submodule init")
    subprocess.run(
        ["git", "-C", str(sub_path), "add", "."],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(sub_path), "commit", "-m", "submodule init"],
        capture_output=True,
        check=True,
    )

    # Register the gitmodules config
    (parent / ".gitmodules").write_text(
        f'[submodule "{sub_name}"]\n\tpath = {sub_name}\n\turl = ./{sub_name}\n'
    )

    # Get the submodule HEAD hash
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(sub_path),
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result.stdout.strip()

    # Register the gitlink in the parent index
    subprocess.run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{commit_hash},{sub_name}",
        ],
        cwd=str(parent),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "add", ".gitmodules"],
        cwd=str(parent),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(parent), "commit", "-m", f"add submodule {sub_name}"],
        capture_output=True,
        check=True,
    )

    return sub_path


def test_git_changes_clean_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean repo produces 'Tree is clean.' output with exit 0."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "clean" in result.output.lower()


def test_git_changes_dirty_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dirty parent produces ## Parent section with filename and diff."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
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
    assert "modified content" in result.output or "diff" in result.output.lower()


def test_git_changes_with_submodule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dirty submodule produces ## Submodule: section with prefixed paths."""
    parent = tmp_path / "parent"
    parent.mkdir()
    _init_repo(parent)
    sub_path = _add_submodule_gitlink(parent, "agent-core")
    monkeypatch.chdir(parent)

    # Make the submodule dirty: add a new untracked file (clear "?? " prefix in status)
    (sub_path / "new_file.txt").write_text("untracked content in submodule")

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "## Submodule: agent-core" in result.output
    # Status line must show prefixed path: agent-core/new_file.txt not bare new_file.txt
    assert "agent-core/new_file.txt" in result.output
    # Verify that any status line for new_file.txt includes the submodule prefix
    lines = result.output.splitlines()
    for line in lines:
        if "new_file.txt" in line and not line.strip().startswith("#"):
            assert "agent-core/" in line


def test_git_changes_clean_submodule_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean submodule section omitted when parent is dirty."""
    parent = tmp_path / "parent"
    parent.mkdir()
    _init_repo(parent)
    _add_submodule_gitlink(parent, "agent-core")
    monkeypatch.chdir(parent)

    # Make only the parent dirty (not the submodule)
    (parent / "README.md").write_text("parent change")

    runner = CliRunner()
    result = runner.invoke(git_group, ["changes"])

    assert result.exit_code == 0
    assert "## Parent" in result.output
    # Submodule is clean — its section must not appear
    assert "## Submodule" not in result.output
