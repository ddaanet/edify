"""Test CLI version option."""

from click.testing import CliRunner

from edify import __version__
from edify.cli import cli


def test_version_flag_displays_version() -> None:
    """Test that --version displays the correct version.

    When: edify --version is called
    Then: Output contains version number and program name, exit code is 0
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output
    assert "edify" in result.output.lower()
