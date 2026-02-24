"""Tests for _append_lifecycle_delivered function."""

from pathlib import Path

from claudeutils.worktree.merge import _append_lifecycle_delivered


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
