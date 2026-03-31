"""Tests for plan ordering by session.md task position."""

from unittest import mock

from edify.planstate.aggregation import AggregatedStatus, TreeInfo
from edify.planstate.models import PlanState
from edify.worktree.display import format_rich_ls
from edify.worktree.session import (
    TaskBlock,
    _extract_plan_from_block,
    extract_plan_order,
)

# --- _extract_plan_from_block ---


def test_extract_plan_from_continuation_line() -> None:
    """Plan: in continuation line is the primary extraction."""
    block = TaskBlock(
        name="Runbook recall expansion",
        lines=[
            (
                "- [ ] **Runbook recall expansion**"
                " — `/design plans/runbook-recall-expansion"
                "/requirements.md` | sonnet"
            ),
            "  - Plan: runbook-recall-expansion | Status: requirements",
        ],
        section="In-tree Tasks",
    )
    assert _extract_plan_from_block(block) == "runbook-recall-expansion"


def test_extract_plan_from_command_path() -> None:
    """Plans/<name>/ in backtick command is fallback."""
    block = TaskBlock(
        name="Design session scraping",
        lines=[
            (
                "- [ ] **Design session scraping**"
                " — `/design plans/session-scraping"
                "/requirements.md` | sonnet"
            ),
        ],
        section="In-tree Tasks",
    )
    assert _extract_plan_from_block(block) == "session-scraping"


def test_extract_plan_from_orchestrate_command() -> None:
    """/orchestrate <name> in backtick command is fallback."""
    block = TaskBlock(
        name="Orchestrate evolution",
        lines=[
            (
                "- [ ] **Orchestrate evolution**"
                " — `/orchestrate orchestrate-evolution`"
                " | sonnet | restart"
            ),
            "  - 14 steps: 12 TDD cycles (sonnet)",
        ],
        section="In-tree Tasks",
    )
    assert _extract_plan_from_block(block) == "orchestrate-evolution"


def test_extract_plan_returns_none_for_no_plan() -> None:
    """Tasks without plan references return None."""
    block = TaskBlock(
        name="Agentic prose terminology",
        lines=[
            (
                "- [ ] **Agentic prose terminology**"
                ' — replace "LLM prose" variants | sonnet'
            ),
        ],
        section="In-tree Tasks",
    )
    assert _extract_plan_from_block(block) is None


def test_extract_plan_continuation_takes_priority() -> None:
    """Plan: in continuation wins over plans/ in command."""
    block = TaskBlock(
        name="Fix planstate detector",
        lines=[
            (
                "- [ ] **Fix planstate detector**"
                " — `/design plans/fix-planstate-detector"
                "/requirements.md` | sonnet"
            ),
            "  - Plan: fix-planstate-detector | Status: requirements",
        ],
        section="In-tree Tasks",
    )
    assert _extract_plan_from_block(block) == "fix-planstate-detector"


# --- extract_plan_order ---


def test_extract_plan_order_preserves_document_order() -> None:
    """Plans ordered by task position in session.md."""
    content = """\
# Session

## In-tree Tasks

- [ ] **Orchestrate evolution** — `/orchestrate orchestrate-evolution` | sonnet
  - Plan: orchestrate-evolution | Status: ready
- [ ] **Task classification** — `/runbook plans/task-classification/outline.md` | sonnet
  - Plan: task-classification | Status: designed
- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements

## Worktree Tasks

- [ ] **Session scraping** — `/design plans/session-scraping/requirements.md` | sonnet
"""
    order = extract_plan_order(content)
    assert order == {
        "orchestrate-evolution": 0,
        "task-classification": 1,
        "codebase-sweep": 2,
        "session-scraping": 3,
    }


def test_extract_plan_order_skips_tasks_without_plans() -> None:
    """Tasks without plan references don't affect position numbering."""
    content = """\
# Session

## In-tree Tasks

- [ ] **Alpha plan** — `/design plans/alpha/requirements.md` | sonnet
  - Plan: alpha | Status: requirements
- [ ] **No plan task** — replace stuff | sonnet
- [ ] **Beta plan** — `/orchestrate beta` | sonnet
"""
    order = extract_plan_order(content)
    assert order == {"alpha": 0, "beta": 1}


def test_extract_plan_order_deduplicates() -> None:
    """First occurrence wins when plan referenced by multiple tasks."""
    content = """\
# Session

## In-tree Tasks

- [ ] **First ref** — `/design plans/shared-plan/requirements.md` | sonnet
  - Plan: shared-plan | Status: requirements
- [ ] **Second ref** — `/runbook plans/shared-plan/outline.md` | sonnet
  - Plan: shared-plan | Status: outlined
"""
    order = extract_plan_order(content)
    assert order == {"shared-plan": 0}


def test_extract_plan_order_empty_session() -> None:
    """Empty or minimal session.md returns empty ordering."""
    assert extract_plan_order("# Session\n") == {}
    assert extract_plan_order("") == {}


# --- format_rich_ls ordering integration ---


def test_plans_ordered_by_session_position() -> None:
    """Plans render in session.md task order, not alphabetically."""
    repo_path = "/fake/repo"

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

    # Plans deliberately in non-alphabetical order to match session.md ordering
    plan_z = PlanState(
        name="zulu-plan",
        status="requirements",
        next_action="/design plans/zulu-plan/requirements.md",
        gate=None,
        artifacts={"requirements.md"},
        tree_path=repo_path,
    )
    plan_a = PlanState(
        name="alpha-plan",
        status="designed",
        next_action="/runbook plans/alpha-plan/design.md",
        gate=None,
        artifacts={"design.md"},
        tree_path=repo_path,
    )
    plan_m = PlanState(
        name="mike-plan",
        status="ready",
        next_action="/orchestrate mike-plan",
        gate=None,
        artifacts={"steps", "orchestrator-plan.md"},
        tree_path=repo_path,
    )

    # Session order: zulu first, then alpha, then mike
    mock_aggregated = AggregatedStatus(
        plans=[plan_z, plan_a, plan_m],
        trees=[main_tree],
    )

    with mock.patch(
        "edify.worktree.display.aggregate_trees",
        return_value=mock_aggregated,
    ):
        output = format_rich_ls(repo_path, "")

    lines = output.strip().split("\n")
    plan_lines = [line for line in lines if line.strip().startswith("Plan:")]

    assert len(plan_lines) == 3
    assert "zulu-plan" in plan_lines[0]
    assert "alpha-plan" in plan_lines[1]
    assert "mike-plan" in plan_lines[2]


def test_unmatched_plans_sort_alphabetically_after_matched() -> None:
    """Plans not in session.md appear after matched plans, alphabetically."""
    repo_path = "/fake/repo"

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

    # ordered-plan is position 0 in session order
    # bravo-orphan and alpha-orphan have no session reference → alphabetical at end
    ordered = PlanState(
        name="ordered-plan",
        status="designed",
        next_action="/runbook plans/ordered-plan/design.md",
        gate=None,
        artifacts={"design.md"},
        tree_path=repo_path,
    )
    bravo = PlanState(
        name="bravo-orphan",
        status="requirements",
        next_action="/design plans/bravo-orphan/requirements.md",
        gate=None,
        artifacts={"requirements.md"},
        tree_path=repo_path,
    )
    alpha = PlanState(
        name="alpha-orphan",
        status="requirements",
        next_action="/design plans/alpha-orphan/requirements.md",
        gate=None,
        artifacts={"requirements.md"},
        tree_path=repo_path,
    )

    mock_aggregated = AggregatedStatus(
        plans=[ordered, alpha, bravo],
        trees=[main_tree],
    )

    with mock.patch(
        "edify.worktree.display.aggregate_trees",
        return_value=mock_aggregated,
    ):
        output = format_rich_ls(repo_path, "")

    lines = output.strip().split("\n")
    plan_lines = [line for line in lines if line.strip().startswith("Plan:")]

    assert len(plan_lines) == 3
    assert "ordered-plan" in plan_lines[0]
    assert "alpha-orphan" in plan_lines[1]
    assert "bravo-orphan" in plan_lines[2]
