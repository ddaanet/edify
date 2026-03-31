"""Tests for path encoding utilities."""

from pathlib import Path

import pytest

from edify.paths import encode_project_path, get_project_history_dir


def test_encode_project_path_basic() -> None:
    """Encode standard project paths."""
    assert encode_project_path("/Users/david/code/foo") == "-Users-david-code-foo"
    assert encode_project_path("/home/user/project") == "-home-user-project"


def test_encode_project_path_root() -> None:
    """Handle root path edge case."""
    assert encode_project_path("/") == "-"


def test_encode_project_path_rejects_relative() -> None:
    """Reject relative paths that don't start with /."""
    with pytest.raises(ValueError, match="absolute"):
        encode_project_path("relative/path")


def test_encode_project_path_trailing_slash() -> None:
    """Strip trailing slash from output."""
    assert encode_project_path("/Users/david/code/foo/") == "-Users-david-code-foo"


def test_get_project_history_dir_basic() -> None:
    """Construct standard history directory path."""
    result = get_project_history_dir("/Users/david/code/foo")
    expected = Path.home() / ".claude" / "projects" / "-Users-david-code-foo"
    assert result == expected


def test_get_project_history_dir_returns_path() -> None:
    """Return Path object, not string."""
    result = get_project_history_dir("/Users/david/code/foo")
    assert isinstance(result, Path)


def test_get_project_history_dir_uses_encoding() -> None:
    """Use encode_project_path() for encoded portion."""
    project = "/home/user/project"
    result = get_project_history_dir(project)
    encoded = encode_project_path(project)
    assert result.name == encoded
