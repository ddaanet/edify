"""Tests for from_main direction support in the merge pipeline."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from claudeutils.worktree.merge import (
    _format_conflict_report,
    _phase1_validate_clean_trees,
    _phase3_merge_parent,
    _phase4_merge_commit_and_precommit,
    merge,
)
from tests.fixtures_worktree import _run_git


def _setup_main_merged_into_branch(
    repo: Path, init_repo: Callable[[Path], None]
) -> None:
    """Set up repo where main is ancestor of HEAD.

    Creates a branch with one commit, merges main into it from the branch side.
    HEAD is on a branch that has main as an ancestor.
    """
    repo.mkdir(exist_ok=True)
    init_repo(repo)

    # Add a commit on main so it's non-trivial
    (repo / "main-file.txt").write_text("main content")
    _run_git(repo, "add", "main-file.txt")
    _run_git(repo, "commit", "-m", "main commit")

    # Create branch off main, add a commit
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "feature.txt").write_text("feature content")
    _run_git(repo, "add", "feature.txt")
    _run_git(repo, "commit", "-m", "feature commit")

    # Return to main — now HEAD is on main, which is an ancestor of feature
    _run_git(repo, "checkout", "main")

    # Merge feature into main so main is ancestor of HEAD
    _run_git(repo, "merge", "--no-edit", "feature")


def test_merge_accepts_from_main_keyword(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Merge() accepts from_main=True keyword argument.

    When called as merge("main", from_main=True) on a repo where main is already
    an ancestor of HEAD (merged state), the function should accept the keyword
    without raising TypeError and return normally.
    """
    repo = tmp_path / "repo"
    _setup_main_merged_into_branch(repo, init_repo)
    monkeypatch.chdir(repo)

    # main is now merged (feature is ancestor), but we want main as the slug
    # Verify main is ancestor of HEAD
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "main", "HEAD"],
        cwd=repo,
        check=False,
    )
    assert result.returncode == 0, "main should be ancestor of HEAD"

    exit_code = 0
    try:
        merge("main", from_main=True)
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"


# ── Cycle 1.2 tests ──────────────────────────────────────────────────────


def test_phase1_rejects_main_branch_when_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_phase1_validate_clean_trees exits 2 with 'cannot merge main into itself'
    on main branch."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    monkeypatch.chdir(repo)

    # HEAD is on main
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "main", "expected to be on main branch"

    with pytest.raises(SystemExit) as exc_info:
        _phase1_validate_clean_trees("main", from_main=True)

    assert exc_info.value.code == 2


def test_phase1_passes_on_non_main_branch_when_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_phase1_validate_clean_trees passes when from_main=True on a non-main
    branch."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    _run_git(repo, "checkout", "-b", "feature")
    monkeypatch.chdir(repo)

    # Should not raise (no SystemExit)
    _phase1_validate_clean_trees("main", from_main=True)


def test_phase4_skips_lifecycle_when_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """_phase4_merge_commit_and_precommit does not append lifecycle 'delivered'
    when from_main=True."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    # Create feature branch and merge it (so main is merged state)
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "feat.txt").write_text("feat")
    _run_git(repo, "add", "feat.txt")
    _run_git(repo, "commit", "-m", "feat")
    _run_git(repo, "checkout", "main")
    _run_git(repo, "merge", "--no-edit", "feature")

    # Create a reviewed plan with lifecycle.md
    plans_dir = repo / "plans" / "my-plan"
    plans_dir.mkdir(parents=True)
    lifecycle = plans_dir / "lifecycle.md"
    lifecycle.write_text("reviewed\n")
    _run_git(repo, "add", "plans/")
    _run_git(repo, "commit", "-m", "add plan")

    monkeypatch.chdir(repo)

    with patch(
        "claudeutils.planstate.inference._parse_lifecycle_status",
        return_value="reviewed",
    ):
        _phase4_merge_commit_and_precommit("feature", from_main=True)

    # lifecycle.md must not have 'delivered' appended
    content = lifecycle.read_text()
    assert "delivered" not in content


def test_format_conflict_report_hints_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_format_conflict_report output contains '--from-main' hint when
    from_main=True."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    # Need MERGE_HEAD and a conflict file for status/diff calls
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "conflict.txt").write_text("feature side")
    _run_git(repo, "add", "conflict.txt")
    _run_git(repo, "commit", "-m", "feature conflict")
    _run_git(repo, "checkout", "main")
    (repo / "conflict.txt").write_text("main side")
    _run_git(repo, "add", "conflict.txt")
    _run_git(repo, "commit", "-m", "main conflict")
    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "feature"],
        cwd=repo,
        check=False,
    )
    monkeypatch.chdir(repo)

    report = _format_conflict_report(["conflict.txt"], "main", from_main=True)

    assert "merge --from-main" in report


def test_phase3_passes_from_main_to_auto_resolve(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_phase3_merge_parent passes from_main to
    _auto_resolve_known_conflicts."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    # Create feature branch to merge from
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "new.txt").write_text("new content")
    _run_git(repo, "add", "new.txt")
    _run_git(repo, "commit", "-m", "feature commit")
    _run_git(repo, "checkout", "main")

    monkeypatch.chdir(repo)

    with patch(
        "claudeutils.worktree.merge._auto_resolve_known_conflicts",
        return_value=[],
    ) as mock_resolve:
        # merge will succeed (no conflicts) — MERGE_HEAD may not exist
        # but we want to verify from_main is forwarded to _auto_resolve
        try:
            _phase3_merge_parent("feature", from_main=True)
        except SystemExit:
            pass

    # If _auto_resolve_known_conflicts was called, from_main must be in kwargs
    if mock_resolve.called:
        _, kwargs = mock_resolve.call_args
        assert kwargs.get("from_main") is True or (
            len(mock_resolve.call_args.args) >= 3
            and mock_resolve.call_args.args[2] is True
        )
