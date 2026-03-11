"""Tests for task plan reference validation."""

from pathlib import Path

from click.testing import CliRunner

from claudeutils.validation.cli import validate
from claudeutils.validation.task_plans import validate as validate_task_plans


def test_valid_plan_passes_invalid_fails(tmp_path: Path) -> None:
    """Valid plan references pass; missing plan references fail."""
    # Setup: Create session.md at agents/session.md under tmp_path
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    # Create a valid plan directory with requirements.md
    valid_plan_dir = tmp_path / "plans" / "valid-plan"
    valid_plan_dir.mkdir(parents=True)
    (valid_plan_dir / "requirements.md").write_text("# Valid Plan\n")

    # Create session.md with two tasks: one with valid plan ref, one without
    session_content = """# Session Handoff: 2026-03-11

## In-tree Tasks

- [ ] **Good task** — `\x60/design plans/valid-plan/requirements.md\x60 | sonnet
- [ ] **Bad task** — `\x60/design\x60 | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    # Call validate
    errors = validate_task_plans("agents/session.md", tmp_path)

    # Should have exactly 1 error mentioning "Bad task"
    assert len(errors) == 1
    assert "Bad task" in errors[0]


def test_terminal_tasks_exempt(tmp_path: Path) -> None:
    """Terminal tasks are exempt from plan reference validation."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    session_content = """# Session Handoff: 2026-03-11

## In-tree Tasks

- [x] **Done task** — `\x60/design\x60 | sonnet
- [-] **Canceled task** — `\x60/design\x60 | sonnet
- [†] **Failed task** — `\x60/design\x60 | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    errors = validate_task_plans("agents/session.md", tmp_path)

    assert errors == []


def test_slug_only_command(tmp_path: Path) -> None:
    """Slug-only commands like /orchestrate my-plan are extracted/validated."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    # Create a valid plan directory with requirements.md
    plan_dir = tmp_path / "plans" / "my-plan"
    plan_dir.mkdir(parents=True)
    (plan_dir / "requirements.md").write_text("# My Plan\n")

    session_content = """# Session Handoff: 2026-03-11

## Worktree Tasks

- [ ] **Slug task** — `\x60/orchestrate my-plan\x60 | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    errors = validate_task_plans("agents/session.md", tmp_path)

    assert errors == []


def test_nested_reports_path_not_false_positive(tmp_path: Path) -> None:
    """Plans/reports/ is a container dir, not a plan dir — no false positive."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    # Create plans/reports/ container (no recognized artifacts at this level)
    (tmp_path / "plans" / "reports").mkdir(parents=True)

    session_content = """# Session Handoff: 2026-03-11

## In-tree Tasks

- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    errors = validate_task_plans("agents/session.md", tmp_path)

    assert errors == []


def test_non_backtick_command_with_plan_path(tmp_path: Path) -> None:
    """Non-backtick command with plan path resolves plan from raw line.

    /deliverable-review without backtick wrapping should not false-positive.
    """
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    plan_dir = tmp_path / "plans" / "bootstrap-tag-support"
    plan_dir.mkdir(parents=True)
    (plan_dir / "brief.md").write_text("# Bootstrap\n")

    session_content = (
        "# Session Handoff: 2026-03-11\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Review bootstrap work**"
        " \u2014 `/deliverable-review plans/bootstrap-tag-support` | opus | restart\n"
    )
    (agents_dir / "session.md").write_text(session_content)

    errors = validate_task_plans("agents/session.md", tmp_path)

    assert errors == []


def test_cli_task_plans_command() -> None:
    """CLI task-plans command exists and is callable."""
    runner = CliRunner()

    # Just verify the command exists — actual validation tested via validate_task_plans
    result = runner.invoke(validate, ["task-plans", "--help"])
    assert result.exit_code == 0
    assert "task plan" in result.output.lower()
