"""Tests for planstate inference lifecycle.md status detection."""

from pathlib import Path

import pytest

from claudeutils.planstate import infer_state


def test_lifecycle_status_detection(tmp_path: Path) -> None:
    """Lifecycle.md status overrides pre-ready artifact detection."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()

    (plan_dir / "design.md").write_text("")

    lifecycle_content = "2026-02-20 review-pending — /orchestrate\n"
    (plan_dir / "lifecycle.md").write_text(lifecycle_content)

    result = infer_state(plan_dir)

    assert result is not None
    assert result.status == "review-pending"
    assert "lifecycle.md" in result.artifacts


@pytest.mark.parametrize(
    ("state", "lifecycle_content", "expected_next_action"),
    [
        (
            "review-pending",
            "2026-02-20 review-pending — /orchestrate\n",
            "/deliverable-review plans/test-plan",
        ),
        (
            "rework",
            "2026-02-20 rework — /deliverable-review\n",
            "",
        ),
        (
            "reviewed",
            "2026-02-20 reviewed — /deliverable-review\n",
            "",
        ),
        (
            "delivered",
            "2026-02-20 delivered — _worktree merge\n",
            "",
        ),
    ],
)
def test_next_action_post_ready_states(
    tmp_path: Path,
    state: str,
    lifecycle_content: str,
    expected_next_action: str,
) -> None:
    """Test next_action derivation for post-ready states."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "design.md").write_text("")
    (plan_dir / "lifecycle.md").write_text(lifecycle_content)

    result = infer_state(plan_dir)

    assert result is not None
    assert result.status == state
    assert result.next_action == expected_next_action


def test_lifecycle_overrides_ready_state(tmp_path: Path) -> None:
    """Test that lifecycle.md status overrides ready-state artifacts."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()

    (plan_dir / "design.md").write_text("")
    (plan_dir / "runbook-phase-1.md").write_text("")
    (plan_dir / "steps").mkdir()
    (plan_dir / "orchestrator-plan.md").write_text("")

    lifecycle_content = "2026-02-21 delivered — _worktree merge\n"
    (plan_dir / "lifecycle.md").write_text(lifecycle_content)

    result = infer_state(plan_dir)

    assert result is not None
    assert result.status == "delivered"  # NOT "ready"
    assert "lifecycle.md" in result.artifacts
    assert "steps" in result.artifacts
    assert "orchestrator-plan.md" in result.artifacts


def test_lifecycle_review_loop_last_entry_wins(tmp_path: Path) -> None:
    """Test review loop: last entry determines status."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "design.md").write_text("")
    lifecycle_content = (
        "2026-02-20 review-pending — /orchestrate\n"
        "2026-02-20 rework — /deliverable-review\n"
        "2026-02-21 review-pending — /deliverable-review\n"
        "2026-02-21 reviewed — /deliverable-review\n"
    )
    (plan_dir / "lifecycle.md").write_text(lifecycle_content)

    result = infer_state(plan_dir)

    assert result is not None
    assert result.status == "reviewed"  # Last entry wins
    assert result.next_action == ""  # Reviewed → empty, per D-5
    assert "lifecycle.md" in result.artifacts


@pytest.mark.parametrize(
    ("lifecycle_content", "expected_status"),
    [
        ("", "designed"),  # empty_file: falls back to pre-ready
        ("garbage not a valid line", "designed"),  # malformed_last_line: falls back
        ("2026-02-20 unknown-state — source", "designed"),  # invalid_state: falls back
        (
            "2026-02-20 reviewed — /deliverable-review\n\n\n",
            "reviewed",
        ),  # trailing_newlines: stripped, last valid line wins
    ],
)
def test_lifecycle_edge_cases(
    tmp_path: Path, lifecycle_content: str, expected_status: str
) -> None:
    """Test edge cases: invalid lifecycle content falls back to pre-ready."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "design.md").write_text("")
    (plan_dir / "lifecycle.md").write_text(lifecycle_content)

    result = infer_state(plan_dir)

    assert result is not None
    assert result.status == expected_status
