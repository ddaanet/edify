"""Integration tests for _recall CLI group."""

from click.testing import CliRunner

from claudeutils.cli import cli


def test_recall_group_hidden_from_help() -> None:
    """_recall group is hidden from --help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "_recall" not in result.output


def test_recall_group_accessible() -> None:
    """_recall group responds to --help when invoked directly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["_recall", "--help"])
    assert result.exit_code == 0
    assert "check" in result.output
    assert "resolve" in result.output
    assert "diff" in result.output


def test_existing_recall_command_unaffected() -> None:
    """Existing recall command (effectiveness analysis) still accessible."""
    runner = CliRunner()
    result = runner.invoke(cli, ["recall", "--help"])
    assert result.exit_code == 0
    # Should not contain _recall subcommands
    assert "diff" not in result.output
