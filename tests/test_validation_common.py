"""Tests for validation common utilities."""

from pathlib import Path

import pytest

from edify.validation.common import find_project_root


def test_find_project_root_in_current_dir(tmp_path: Path) -> None:
    """Test finding root when CLAUDE.md exists in current directory."""
    (tmp_path / "CLAUDE.md").write_text("# Project")
    root = find_project_root(start=tmp_path)
    assert root == tmp_path


def test_find_project_root_in_parent(tmp_path: Path) -> None:
    """Test finding root when CLAUDE.md exists in parent directory."""
    (tmp_path / "CLAUDE.md").write_text("# Project")
    subdir = tmp_path / "src" / "app"
    subdir.mkdir(parents=True)
    root = find_project_root(start=subdir)
    assert root == tmp_path


def test_find_project_root_from_nested_subdirectory(tmp_path: Path) -> None:
    """Test finding root from deeply nested subdirectory."""
    (tmp_path / "CLAUDE.md").write_text("# Project")
    deep = tmp_path / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    root = find_project_root(start=deep)
    assert root == tmp_path


def test_find_project_root_custom_start_path(tmp_path: Path) -> None:
    """Test using custom start path parameter."""
    (tmp_path / "CLAUDE.md").write_text("# Project")
    subdir = tmp_path / "src"
    subdir.mkdir(parents=True)
    root = find_project_root(start=subdir)
    assert root == tmp_path


def test_find_project_root_not_found(tmp_path: Path) -> None:
    """Test that FileNotFoundError is raised when CLAUDE.md not found."""
    subdir = tmp_path / "src"
    subdir.mkdir(parents=True)
    with pytest.raises(FileNotFoundError, match="Could not find project root"):
        find_project_root(start=subdir)


def test_find_project_root_default_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that default start path uses current working directory."""
    (tmp_path / "CLAUDE.md").write_text("# Project")
    monkeypatch.chdir(tmp_path)
    root = find_project_root()
    assert root == tmp_path
