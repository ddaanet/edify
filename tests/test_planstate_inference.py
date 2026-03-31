"""Tests for planstate inference module."""

from pathlib import Path
from unittest.mock import Mock

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


def test_problem_md_not_recognized(tmp_path: Path) -> None:
    """problem.md is not a recognized artifact."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "problem.md").write_text("")

    result = infer_state(plan_dir)
    assert result is None


@pytest.mark.parametrize(
    ("create_artifacts", "expected_status", "expected_artifacts"),
    [
        (["requirements.md"], "requirements", {"requirements.md"}),
        pytest.param(
            ["outline.md"],
            "outlined",
            {"outline.md"},
            id="outlined-outline-only",
        ),
        pytest.param(
            ["requirements.md", "outline.md"],
            "outlined",
            {"requirements.md", "outline.md"},
            id="outlined-with-requirements",
        ),
        pytest.param(["brief.md"], "briefed", {"brief.md"}, id="briefed-brief-only"),
        pytest.param(
            ["brief.md", "classification.md"],
            "briefed",
            {"brief.md", "classification.md"},
            id="briefed-with-classification",
        ),
        pytest.param(
            ["brief.md", "requirements.md"],
            "requirements",
            {"brief.md", "requirements.md"},
            id="requirements-brief-plus-requirements",
        ),
        pytest.param(
            ["brief.md", "problem.md"],
            "briefed",
            {"brief.md"},
            id="briefed-with-unrecognized-problem",
        ),
        pytest.param(
            ["brief.md", "inline-plan.md"],
            "inline-planned",
            {"brief.md", "inline-plan.md"},
            id="inline-planned-brief-plus-inline-plan",
        ),
        pytest.param(
            ["inline-plan.md"],
            "inline-planned",
            {"inline-plan.md"},
            id="inline-planned-inline-plan-only",
        ),
        (
            ["requirements.md", "design.md"],
            "designed",
            {"requirements.md", "design.md"},
        ),
        pytest.param(
            ["requirements.md", "outline.md", "design.md"],
            "designed",
            {"requirements.md", "outline.md", "design.md"},
            id="designed-with-outline",
        ),
        (
            ["design.md", "runbook-phase-1.md", "runbook-phase-2.md"],
            "planned",
            {"design.md", "runbook-phase-1.md", "runbook-phase-2.md"},
        ),
        (
            ["design.md", "runbook-phase-1.md", "steps", "orchestrator-plan.md"],
            "ready",
            {"design.md", "runbook-phase-1.md", "steps", "orchestrator-plan.md"},
        ),
    ],
)
def test_status_priority_detection(
    tmp_path: Path,
    create_artifacts: list[str],
    expected_status: str,
    expected_artifacts: set[str],
) -> None:
    """Test status detection with priority chain."""
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


@pytest.mark.parametrize(
    ("create_artifacts", "expected_next_action"),
    [
        (["brief.md"], "/design plans/test-plan/brief.md"),
        (["requirements.md"], "/design plans/test-plan/requirements.md"),
        (["requirements.md", "outline.md"], "/design plans/test-plan/outline.md"),
        (["requirements.md", "design.md"], "/runbook plans/test-plan/design.md"),
        (["inline-plan.md"], "/inline plans/test-plan"),
        (
            ["design.md", "runbook-phase-1.md", "runbook-phase-2.md"],
            "plugin/bin/prepare-runbook.py plans/test-plan",
        ),
        (
            ["design.md", "runbook-phase-1.md", "steps", "orchestrator-plan.md"],
            "/orchestrate test-plan",
        ),
    ],
)
def test_next_action_derivation(
    tmp_path: Path,
    create_artifacts: list[str],
    expected_next_action: str,
) -> None:
    """Test next_action derivation from status."""
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
    assert result.next_action == expected_next_action


def test_list_plans_directory_scanning(tmp_path: Path) -> None:
    """Test list_plans scans, excludes reports and empty dirs."""
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()

    plan_a = plans_dir / "plan-a"
    plan_a.mkdir()
    (plan_a / "requirements.md").write_text("")

    plan_b = plans_dir / "plan-b"
    plan_b.mkdir()
    (plan_b / "design.md").write_text("")

    reports_dir = plans_dir / "reports"
    reports_dir.mkdir()

    empty_dir = plans_dir / "empty-dir"
    empty_dir.mkdir()

    result = list_plans(plans_dir)

    assert len(result) == 2
    assert [ps.name for ps in result] == ["plan-a", "plan-b"]

    result_names = {ps.name for ps in result}
    assert "reports" not in result_names
    assert "empty-dir" not in result_names

    empty_result = list_plans(tmp_path / "nonexistent")
    assert empty_result == []


@pytest.mark.parametrize(
    ("stale_sources", "expected_gate"),
    [
        (
            ["design.md"],
            "design vet stale — re-vet before planning",
        ),
        (
            ["runbook-outline.md"],
            "runbook outline vet stale — re-review before expansion",
        ),
        (
            ["runbook-phase-2.md"],
            "phase 2 vet stale — re-review",
        ),
        (
            ["outline.md"],
            "outline vet stale — re-review before design",
        ),
        # Priority: design wins over all others
        (
            ["outline.md", "design.md", "runbook-phase-1.md"],
            "design vet stale — re-vet before planning",
        ),
        # Priority: runbook-outline wins over phase and outline
        (
            ["outline.md", "runbook-outline.md", "runbook-phase-3.md"],
            "runbook outline vet stale — re-review before expansion",
        ),
        # Priority: phase wins over outline
        (
            ["outline.md", "runbook-phase-1.md"],
            "phase 1 vet stale — re-review",
        ),
        # No stale sources → no gate
        (
            [],
            None,
        ),
    ],
)
def test_gate_priority_chain(
    tmp_path: Path,
    stale_sources: list[str],
    expected_gate: str | None,
) -> None:
    """Test gate priority: design > runbook outline > phase-level > outline."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "design.md").write_text("")

    mock_chains = [Mock(source=src, stale=True) for src in stale_sources]
    # Add a non-stale chain to verify it's ignored
    mock_chains.append(Mock(source="requirements.md", stale=False))

    mock_vet_status = Mock()
    mock_vet_status.chains = mock_chains

    result = infer_state(plan_dir, vet_status_func=lambda _: mock_vet_status)

    assert result is not None
    assert result.gate == expected_gate


def test_gate_attachment_with_mock(tmp_path: Path) -> None:
    """Test gate field attachment from mock VetStatus."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    (plan_dir / "design.md").write_text("")

    result = infer_state(plan_dir)
    assert result is not None
    assert result.gate is None

    mock_vet_status = Mock()
    mock_vet_status.chains = [Mock(source="design.md", stale=True)]

    result = infer_state(plan_dir, vet_status_func=lambda _: mock_vet_status)
    assert result is not None
    assert result.gate == "design vet stale — re-vet before planning"
