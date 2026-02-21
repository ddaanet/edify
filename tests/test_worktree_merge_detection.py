"""Tests for merge commit detection functions in git_ops."""

from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.git_ops import _is_merge_commit, _is_merge_of
from tests.fixtures_worktree import _git_setup


def test_detects_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects merge commit via parent count."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Root commit (0 parents) is not a merge commit
    assert not _is_merge_commit()

    # Normal commit (1 parent) is not a merge commit
    (repo_path / "second.txt").write_text("second")
    _git_setup("add", "second.txt")
    _git_setup("commit", "-m", "Second commit")
    assert not _is_merge_commit()

    # Create another branch and merge to create merge commit
    _git_setup("checkout", "-b", "feature")
    (repo_path / "feature.txt").write_text("feature content")
    _git_setup("add", "feature.txt")
    _git_setup("commit", "-m", "Feature commit")
    _git_setup("checkout", "main")
    _git_setup("merge", "--no-ff", "feature")

    # Merge commit has 2 parents
    assert _is_merge_commit()


def test_is_merge_of_distinguishes_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """_is_merge_of returns True only when slug's branch is a merge parent."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create and merge "feature-a"
    _git_setup("checkout", "-b", "feature-a")
    (repo_path / "a.txt").write_text("a")
    _git_setup("add", "a.txt")
    _git_setup("commit", "-m", "Add a")
    _git_setup("checkout", "main")
    _git_setup("merge", "--no-ff", "feature-a")

    assert _is_merge_commit()
    assert _is_merge_of("feature-a")
    assert not _is_merge_of("feature-b")  # branch doesn't exist — not a parent

    # Create "feature-b" (not merged) — verify it's not identified as merge parent
    _git_setup("checkout", "-b", "feature-b")
    (repo_path / "b.txt").write_text("b")
    _git_setup("add", "b.txt")
    _git_setup("commit", "-m", "Add b")
    _git_setup("checkout", "main")

    # HEAD is still the merge of feature-a, not feature-b
    assert _is_merge_of("feature-a")
    assert not _is_merge_of("feature-b")
