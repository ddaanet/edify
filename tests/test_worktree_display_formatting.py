"""Tests for worktree display formatting (rich ls output)."""

from unittest import mock

from claudeutils.planstate.aggregation import AggregatedStatus, TreeInfo
from claudeutils.planstate.models import PlanState
from claudeutils.worktree.display import format_rich_ls


def test_format_rich_ls_renders_gate_lines() -> None:
    """Test that format_rich_ls renders Gate lines from aggregated data."""
    repo_path = "/fake/repo"
    wt_path = "/fake/repo/wt/test-wt"

    main_tree = TreeInfo(
        path=repo_path,
        branch="main",
        is_main=True,
        slug=None,
        latest_commit_timestamp=100,
        latest_commit_subject="initial",
        commits_since_handoff=0,
        is_dirty=False,
        task_summary=None,
    )
    wt_tree = TreeInfo(
        path=wt_path,
        branch="feature",
        is_main=False,
        slug="test-wt",
        latest_commit_timestamp=200,
        latest_commit_subject="add session",
        commits_since_handoff=5,
        is_dirty=True,
        task_summary="Fix bugs",
    )

    plan_with_gate = PlanState(
        name="gated-plan",
        status="designed",
        next_action="/runbook plans/gated-plan/design.md",
        gate="design vet stale — re-vet before planning",
        artifacts={"design.md"},
        tree_path=repo_path,
    )
    plan_without_gate = PlanState(
        name="normal-plan",
        status="planned",
        next_action="plugin/bin/prepare-runbook.py plans/normal-plan",
        gate=None,
        artifacts={"design.md", "runbook-phase-1.md"},
        tree_path=wt_path,
    )

    mock_aggregated = AggregatedStatus(
        plans=[plan_with_gate, plan_without_gate],
        trees=[wt_tree, main_tree],
    )
    with mock.patch(
        "claudeutils.worktree.display.aggregate_trees",
        return_value=mock_aggregated,
    ):
        output = format_rich_ls(repo_path, "")

    assert "  Gate: design vet stale — re-vet before planning" in output
    assert output.count("  Gate:") == 1
    assert "  Plan: gated-plan [designed]" in output
    assert "  Plan: normal-plan [planned]" in output

    # Verify tree headers use aggregated data
    assert "main (main)" in output
    assert "○  clean" in output
    assert "test-wt (feature)" in output
    assert "●" in output
    assert "5 commits since handoff" in output
