"""Tests for the validation CLI command group."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.cli import cli


def test_validate_all_validators(tmp_path: Path) -> None:
    """Test that 'claudeutils validate' runs all validators."""
    runner = CliRunner()

    # Mock all validator functions to return no errors
    with (
        patch("claudeutils.validation.cli.validate_learnings", return_value=[]),
        patch("claudeutils.validation.cli.validate_memory_index", return_value=[]),
        patch("claudeutils.validation.cli.validate_tasks", return_value=[]),
        patch("claudeutils.validation.cli.validate_decision_files", return_value=[]),
        patch("claudeutils.validation.cli.validate_planstate", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 0


def test_validate_learnings_subcommand(tmp_path: Path) -> None:
    """Test that 'claudeutils validate learnings' runs only learnings validator.

    Verifies individual subcommand execution.
    """
    runner = CliRunner()

    with (
        patch("claudeutils.validation.cli.validate_learnings", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "learnings"])

    assert result.exit_code == 0


def test_validate_memory_index_subcommand(tmp_path: Path) -> None:
    """Test memory-index validator subcommand.

    Verifies 'claudeutils validate memory-index' runs only the memory-index
    validator.
    """
    runner = CliRunner()

    with (
        patch("claudeutils.validation.cli.validate_memory_index", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "memory-index"])

    assert result.exit_code == 0


def test_validate_tasks_subcommand(tmp_path: Path) -> None:
    """Test that 'claudeutils validate tasks' runs only tasks validator."""
    runner = CliRunner()

    with (
        patch("claudeutils.validation.cli.validate_tasks", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "tasks"])

    assert result.exit_code == 0


def test_validate_decisions_subcommand(tmp_path: Path) -> None:
    """Test that 'claudeutils validate decisions' runs only decisions validator.

    Verifies individual subcommand execution.
    """
    runner = CliRunner()

    with (
        patch("claudeutils.validation.cli.validate_decision_files", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "decisions"])

    assert result.exit_code == 0


def test_validate_planstate_subcommand(tmp_path: Path) -> None:
    """Test 'claudeutils validate planstate' subcommand."""
    runner = CliRunner()

    with (
        patch("claudeutils.validation.cli.validate_planstate", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "planstate"])

    assert result.exit_code == 0


def test_validate_exit_code_1_on_failure(tmp_path: Path) -> None:
    """Test that exit code is 1 when validation fails."""
    runner = CliRunner()

    with (
        patch(
            "claudeutils.validation.cli.validate_learnings",
            return_value=["Error: title too long"],
        ),
        patch("claudeutils.validation.cli.validate_memory_index", return_value=[]),
        patch("claudeutils.validation.cli.validate_tasks", return_value=[]),
        patch("claudeutils.validation.cli.validate_decision_files", return_value=[]),
        patch("claudeutils.validation.cli.validate_planstate", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 1


def test_validate_error_output_to_stderr(tmp_path: Path) -> None:
    """Test that errors are output to stderr."""
    runner = CliRunner()

    with (
        patch(
            "claudeutils.validation.cli.validate_learnings",
            return_value=["agents/learnings.md:5: title too long"],
        ),
        patch("claudeutils.validation.cli.validate_memory_index", return_value=[]),
        patch("claudeutils.validation.cli.validate_tasks", return_value=[]),
        patch("claudeutils.validation.cli.validate_decision_files", return_value=[]),
        patch("claudeutils.validation.cli.validate_planstate", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 1
    assert "Error (learnings):" in result.output
    assert "title too long" in result.output


def test_validate_subcommand_exit_code_1_on_failure(tmp_path: Path) -> None:
    """Test that subcommand exits with code 1 when validation fails."""
    runner = CliRunner()

    with (
        patch(
            "claudeutils.validation.cli.validate_learnings",
            return_value=["agents/learnings.md:5: title too long"],
        ),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "learnings"])

    assert result.exit_code == 1
    assert "title too long" in result.output


def test_validate_subcommand_exit_code_0_on_success(tmp_path: Path) -> None:
    """Test that subcommand exits with code 0 when validation passes."""
    runner = CliRunner()

    with (
        patch("claudeutils.validation.cli.validate_learnings", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate", "learnings"])

    assert result.exit_code == 0


def test_validate_all_mode_multiple_errors(tmp_path: Path) -> None:
    """Test 'validate all' collects errors from multiple validators.

    Verifies error aggregation across validators.
    """
    runner = CliRunner()

    with (
        patch(
            "claudeutils.validation.cli.validate_learnings",
            return_value=["agents/learnings.md:5: title too long"],
        ),
        patch(
            "claudeutils.validation.cli.validate_memory_index",
            return_value=["agents/memory-index.md:10: orphan entry"],
        ),
        patch("claudeutils.validation.cli.validate_tasks", return_value=[]),
        patch("claudeutils.validation.cli.validate_decision_files", return_value=[]),
        patch("claudeutils.validation.cli.validate_planstate", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 1
    assert "Error (learnings):" in result.output
    assert "Error (memory-index):" in result.output
    assert "title too long" in result.output
    assert "orphan entry" in result.output


def test_validate_all_mode_no_short_circuit(tmp_path: Path) -> None:
    """Test that 'validate all' doesn't short-circuit after first failure.

    Verifies all validators run even when early validators fail.
    """
    runner = CliRunner()
    call_count = {"count": 0}

    def mock_learnings_validator(*args: object, **kwargs: object) -> list[str]:
        call_count["count"] += 1
        return ["error"]

    def mock_memory_index_validator(*args: object, **kwargs: object) -> list[str]:
        call_count["count"] += 1
        return ["error"]

    with (
        patch(
            "claudeutils.validation.cli.validate_learnings",
            side_effect=mock_learnings_validator,
        ),
        patch(
            "claudeutils.validation.cli.validate_memory_index",
            side_effect=mock_memory_index_validator,
        ),
        patch("claudeutils.validation.cli.validate_tasks", return_value=[]),
        patch("claudeutils.validation.cli.validate_decision_files", return_value=[]),
        patch("claudeutils.validation.cli.validate_planstate", return_value=[]),
        patch("claudeutils.validation.cli.find_project_root", return_value=tmp_path),
    ):
        result = runner.invoke(cli, ["validate"])

    assert result.exit_code == 1
    # Verify both validators were called (not short-circuited)
    assert call_count["count"] >= 2
