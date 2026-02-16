"""Tests for planstate inference module."""

from pathlib import Path

import pytest

from claudeutils.planstate import PlanState, infer_state, list_plans


def test_empty_directory_not_a_plan(tmp_path: Path) -> None:
    """Empty directories should not be treated as plans."""
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    empty_plan = plans_dir / "empty"
    empty_plan.mkdir()

    result = infer_state(empty_plan)
    assert result is None

    plans = list_plans(plans_dir)
    assert plans == []


@pytest.mark.parametrize(
    ("status", "create_artifacts", "expected_status", "expected_artifacts"),
    [
        (
            "requirements",
            ["requirements.md"],
            "requirements",
            {"requirements.md"},
        ),
        (
            "designed",
            ["requirements.md", "design.md"],
            "designed",
            {"requirements.md", "design.md"},
        ),
        (
            "planned",
            ["design.md", "runbook-phase-1.md", "runbook-phase-2.md"],
            "planned",
            {"design.md", "runbook-phase-1.md", "runbook-phase-2.md"},
        ),
        (
            "ready",
            ["design.md", "runbook-phase-1.md", "steps", "orchestrator-plan.md"],
            "ready",
            {"design.md", "runbook-phase-1.md", "steps", "orchestrator-plan.md"},
        ),
    ],
)
def test_status_priority_detection(
    tmp_path: Path,
    status: str,
    create_artifacts: list[str],
    expected_status: str,
    expected_artifacts: set[str],
) -> None:
    """Test status detection with priority chain.

    Priority order: ready > planned > designed > requirements
    """
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()

    for artifact in create_artifacts:
        artifact_path = plan_dir / artifact
        if artifact == "steps":
            artifact_path.mkdir()
        else:
            artifact_path.write_text("")

    result = infer_state(plan_dir)

    assert result is not None
    assert isinstance(result, PlanState)
    assert result.status == expected_status
    assert result.name == "test-plan"
    assert result.artifacts == expected_artifacts
