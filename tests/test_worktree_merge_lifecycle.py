"""Tests for _append_lifecycle_delivered function and merge integration."""

from collections.abc import Callable
from pathlib import Path

import pytest

from edify.worktree.merge import _append_lifecycle_delivered, merge
from tests.fixtures_worktree import make_repo_with_branch


def test_append_lifecycle_delivered_appends_entry(tmp_path: Path) -> None:
    """Test: _append_lifecycle_delivered appends delivered entry to lifecycle.md."""
    plans_dir = tmp_path / "plans"
    plan_dir = plans_dir / "my-plan"
    plan_dir.mkdir(parents=True)

    lifecycle_file = plan_dir / "lifecycle.md"
    lifecycle_file.write_text("2026-02-20 reviewed — /deliverable-review\n")

    _append_lifecycle_delivered(plans_dir)

    lines = [line for line in lifecycle_file.read_text().split("\n") if line]
    assert len(lines) == 2
    assert "delivered" in lines[-1]
    assert "_worktree merge" in lines[-1]


def test_append_lifecycle_delivered_skips_non_reviewed(tmp_path: Path) -> None:
    """Test: _append_lifecycle_delivered skips non-reviewed plans."""
    plans_dir = tmp_path / "plans"
    plan_dir = plans_dir / "my-plan"
    plan_dir.mkdir(parents=True)

    lifecycle_file = plan_dir / "lifecycle.md"
    lifecycle_file.write_text("2026-02-20 review-pending — /orchestrate\n")
    original_content = lifecycle_file.read_text()

    _append_lifecycle_delivered(plans_dir)

    assert lifecycle_file.read_text() == original_content


def test_append_lifecycle_delivered_graceful_missing_plans_dir(tmp_path: Path) -> None:
    """Test: _append_lifecycle_delivered handles missing plans_dir gracefully."""
    nonexistent_dir = tmp_path / "no-such-plans"

    _append_lifecycle_delivered(nonexistent_dir)

    # No exception raised, call completes normally


def test_append_lifecycle_delivered_skips_plan_without_lifecycle(
    tmp_path: Path,
) -> None:
    """Test: _append_lifecycle_delivered skips plan directories without lifecycle.md."""
    plans_dir = tmp_path / "plans"
    plan_dir = plans_dir / "my-plan"
    plan_dir.mkdir(parents=True)
    # plan_dir exists but has no lifecycle.md

    _append_lifecycle_delivered(plans_dir)

    # No lifecycle.md created — function only appends to existing reviewed files
    assert not (plan_dir / "lifecycle.md").exists()


def test_merge_appends_lifecycle_delivered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Test: merge() appends delivered entry to lifecycle.md for a reviewed plan."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, branch="test-branch")
    monkeypatch.chdir(repo)

    plans_dir = repo / "plans"
    plan_dir = plans_dir / "my-plan"
    plan_dir.mkdir(parents=True)
    lifecycle = plan_dir / "lifecycle.md"
    lifecycle.write_text("2026-02-20 reviewed — /deliverable-review\n")

    merge("test-branch")

    lines = [line for line in lifecycle.read_text().splitlines() if line.strip()]
    assert len(lines) == 2
    assert "delivered" in lines[-1]
    assert "_worktree merge" in lines[-1]
