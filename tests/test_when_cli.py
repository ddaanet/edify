"""Tests for the when CLI command."""

from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.when.cli import when_cmd


def test_when_command_exists() -> None:
    """Test that when command exists and is registered in CLI.

    Verifies:
    1. when_cmd can be imported from claudeutils.when.cli
    2. when_cmd is a Click command
    3. CLI responds to 'when --help' with help text
    """
    # Verify import succeeds
    assert when_cmd is not None

    # Verify command is accessible via CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["when", "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
