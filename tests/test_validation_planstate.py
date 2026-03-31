"""Tests for planstate validation."""

from pathlib import Path

from click.testing import CliRunner

from edify.validation.cli import validate
from edify.validation.planstate import validate as validate_planstate


def test_validator_detects_missing_artifacts(tmp_path: Path) -> None:
    """Plan directory with no recognized artifacts returns error."""
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "empty-plan").mkdir()

    errors = validate_planstate(tmp_path)
    assert len(errors) == 1
    assert "empty-plan" in errors[0]
    assert "no recognized artifacts" in errors[0]


def test_missing_artifacts_excludes_reports(tmp_path: Path) -> None:
    """Plans/reports/ is not treated as a plan."""
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "reports").mkdir()

    errors = validate_planstate(tmp_path)
    assert errors == []


def test_classification_only_recognized(tmp_path: Path) -> None:
    """Plan with only classification.md is recognized."""
    plans = tmp_path / "plans"
    plan = plans / "classified-plan"
    plan.mkdir(parents=True)
    (plan / "classification.md").write_text("# Classification\n")

    errors = validate_planstate(tmp_path)
    assert errors == []


def test_empty_plans_dir(tmp_path: Path) -> None:
    """Empty plans/ directory produces no errors."""
    plans = tmp_path / "plans"
    plans.mkdir()

    errors = validate_planstate(tmp_path)
    assert errors == []


def test_validator_checks_steps_without_runbook_phases(tmp_path: Path) -> None:
    """Plan with steps/ but no runbook-phase-*.md returns error."""
    plans = tmp_path / "plans"
    plan = plans / "bad-plan"
    plan.mkdir(parents=True)
    (plan / "steps").mkdir()
    (plan / "design.md").write_text("# Design")

    errors = validate_planstate(tmp_path)
    assert any("steps/ without runbook-phase" in e for e in errors)


def test_validator_checks_orchestrator_without_steps(tmp_path: Path) -> None:
    """Plan with orchestrator-plan.md but no steps/ returns error."""
    plans = tmp_path / "plans"
    plan = plans / "incomplete-plan"
    plan.mkdir(parents=True)
    (plan / "orchestrator-plan.md").write_text("# Plan")
    (plan / "runbook-phase-1.md").write_text("# Phase 1")

    errors = validate_planstate(tmp_path)
    assert any("orchestrator-plan.md without steps/" in e for e in errors)


def test_consistent_artifacts_pass(tmp_path: Path) -> None:
    """Plan with consistent ready-state artifacts passes."""
    plans = tmp_path / "plans"
    plan = plans / "good-plan"
    plan.mkdir(parents=True)
    (plan / "steps").mkdir()
    (plan / "orchestrator-plan.md").write_text("# Plan")
    (plan / "runbook-phase-1.md").write_text("# Phase 1")
    (plan / "design.md").write_text("# Design")

    errors = validate_planstate(tmp_path)
    assert errors == []


def test_validator_warns_on_archive_orphans(tmp_path: Path) -> None:
    """Archived plan with existing directory returns warning."""
    plans = tmp_path / "plans"
    (plans / "old-plan").mkdir(parents=True)
    (plans / "old-plan" / "requirements.md").write_text("# Req")

    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "plan-archive.md").write_text(
        "# Plan Archive\n\n## old-plan\n\nSummary.\n"
    )

    errors = validate_planstate(tmp_path)
    assert any("archived but directory still exists" in e for e in errors)


def test_archive_without_directory_is_valid(tmp_path: Path) -> None:
    """Archived plan without directory is the expected state."""
    plans = tmp_path / "plans"
    plans.mkdir()

    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "plan-archive.md").write_text(
        "# Plan Archive\n\n## deleted-plan\n\nSummary.\n"
    )

    errors = validate_planstate(tmp_path)
    assert errors == []


def test_cli_integration_planstate_subcommand(tmp_path: Path) -> None:
    """CLI planstate subcommand exists and runs."""
    plans = tmp_path / "plans"
    (plans / "empty-plan").mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(validate, ["planstate"], catch_exceptions=False)
    # Runs against real project root, not tmp_path
    # Just verify the subcommand exists and doesn't crash
    assert result.exit_code in (0, 1)
