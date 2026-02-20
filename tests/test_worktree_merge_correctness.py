"""Tests for Track 2: Merge correctness (MERGE_HEAD checkpoint)."""

import contextlib
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.git_ops import _is_branch_merged
from claudeutils.worktree.merge import (
    _phase1_validate_clean_trees,
    _phase3_merge_parent,
    _phase4_merge_commit_and_precommit,
    _validate_merge_result,
)
from tests.fixtures_worktree import last_commit_subject, make_repo_with_branch


def test_phase4_refuses_single_parent_when_unmerged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Phase 4 refuses single-parent commit when branch unmerged."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, diverge=True)
    monkeypatch.chdir(repo)

    # Merge --no-commit then simulate MERGE_HEAD loss
    subprocess.run(
        ["git", "merge", "--no-commit", "test-branch"],
        cwd=repo,
        check=False,
        capture_output=True,
    )
    (repo / ".git" / "MERGE_HEAD").unlink(missing_ok=True)

    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo,
            check=False,
        ).returncode
        != 0
    ), "Staged changes should be present"
    assert not _is_branch_merged("test-branch")

    commit_before = last_commit_subject(repo)
    exit_code = 0
    try:
        _phase4_merge_commit_and_precommit("test-branch")
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 2, f"Expected exit code 2, got {exit_code}"
    assert last_commit_subject(repo) == commit_before, "No new commit should be created"


def test_phase4_allows_already_merged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Phase 4 allows commit when branch already merged (idempotent)."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, merge=True)
    monkeypatch.chdir(repo)

    # Stage additional changes on top of already-merged state
    (repo / "additional.txt").write_text("additional content")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)

    assert not (repo / ".git" / "MERGE_HEAD").exists()
    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo,
            check=False,
        ).returncode
        != 0
    ), "Staged changes should be present"

    commit_before = last_commit_subject(repo)
    exit_code = None
    try:
        _phase4_merge_commit_and_precommit("test-branch")
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code

    commit_after = last_commit_subject(repo)
    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
    assert commit_after != commit_before, "New commit should be created"
    assert "Merge test-branch" in commit_after


def test_phase4_no_merge_head_unmerged_exits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Phase 4 exits 2 when no MERGE_HEAD, no staged, branch unmerged."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo)
    monkeypatch.chdir(repo)

    assert not (repo / ".git" / "MERGE_HEAD").exists()
    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo,
            check=False,
        ).returncode
        == 0
    ), "No staged changes"

    commit_before = last_commit_subject(repo)
    exit_code = None
    try:
        _phase4_merge_commit_and_precommit("test-branch")
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 2, f"Expected exit code 2, got {exit_code}"
    assert last_commit_subject(repo) == commit_before, "No commit should be created"


def test_phase4_no_merge_head_merged_skips(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Phase 4 skips when no MERGE_HEAD, no staged, branch already merged."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, merge=True)
    monkeypatch.chdir(repo)

    assert not (repo / ".git" / "MERGE_HEAD").exists()
    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo,
            check=False,
        ).returncode
        == 0
    ), "No staged changes"

    commit_before = last_commit_subject(repo)
    exit_code = None
    try:
        _phase4_merge_commit_and_precommit("test-branch")
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
    assert last_commit_subject(repo) == commit_before, "No commit (already merged)"


def test_validate_merge_valid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validation passes when slug is ancestor of HEAD."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, merge=True)
    monkeypatch.chdir(repo)

    exit_code = 0
    try:
        _validate_merge_result("test-branch")
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 0
    assert "Error" not in capsys.readouterr().out


def test_validate_merge_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validation fails when slug is NOT ancestor of HEAD."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo)  # not merged
    monkeypatch.chdir(repo)

    exit_code = 0
    try:
        _validate_merge_result("test-branch")
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 2
    assert "Error: branch test-branch not fully merged" in capsys.readouterr().out


def test_validate_merge_single_parent_warning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validation warns when HEAD has single parent (fast-forward)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    # Branch at same commit, then advance main → single-parent HEAD
    subprocess.run(
        ["git", "branch", "test-branch"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    (repo / "main-file.txt").write_text("main content")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "main commit"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(repo)

    with contextlib.suppress(SystemExit):
        _validate_merge_result("test-branch")

    assert "Warning: merge commit has 1 parent(s)" in capsys.readouterr().out


def test_merge_preserves_parent_repo_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Full merge preserves parent repo files and produces 2-parent commit."""
    parent_repo = tmp_path / "parent"
    parent_repo.mkdir()
    init_repo(parent_repo)

    # Create worktree branch with parent repo changes
    wt_dir = tmp_path / "wt" / "test"
    wt_dir.mkdir(parents=True)
    subprocess.run(
        ["git", "worktree", "add", "-b", "test-branch", str(wt_dir)],
        cwd=parent_repo,
        check=True,
        capture_output=True,
    )
    (wt_dir / "parent-change.txt").write_text("parent repo change")
    subprocess.run(["git", "add", "."], cwd=wt_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "worktree changes"],
        cwd=wt_dir,
        check=True,
        capture_output=True,
    )

    monkeypatch.chdir(parent_repo)
    _phase1_validate_clean_trees("test-branch")
    _phase3_merge_parent("test-branch")
    _phase4_merge_commit_and_precommit("test-branch")

    assert (parent_repo / "parent-change.txt").exists()

    parents = subprocess.run(
        ["git", "log", "-1", "--format=%p", "HEAD"],
        cwd=parent_repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert len(parents.split()) == 2

    assert (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", "test-branch", "HEAD"],
            cwd=parent_repo,
            check=False,
        ).returncode
        == 0
    )
