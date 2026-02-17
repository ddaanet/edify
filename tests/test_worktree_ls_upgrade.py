"""Test upgrade of worktree ls command with --porcelain flag."""

from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_porcelain_flag_exists() -> None:
    """Verify --porcelain flag exists and is boolean."""
    runner = CliRunner()

    # Test that --porcelain flag is recognized
    result = runner.invoke(worktree, ["ls", "--porcelain"])
    assert result.exit_code == 0, f"Expected success, got: {result.output}"

    # Test that --help shows the --porcelain flag
    help_result = runner.invoke(worktree, ["ls", "--help"])
    assert "--porcelain" in help_result.output, "Flag should appear in help text"
