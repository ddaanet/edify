"""Tests for _recall resolve subcommand."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.cli import cli


def test_resolve_artifact_mode_happy_path() -> None:
    """Resolve artifact mode: read, parse, resolve, output results."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create artifact with two entries
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

when first entry — annotation for first
when second entry — annotation for second
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        # Mock resolver to return distinct content for each trigger
        with patch("claudeutils.recall_cli.cli.resolve") as mock_resolve:
            mock_resolve.side_effect = [
                "# First Entry Resolved\nContent 1",
                "# Second Entry Resolved\nContent 2",
            ]

            result = runner.invoke(cli, ["_recall", "resolve", str(artifact_path)])

            # Verify exit code 0
            assert result.exit_code == 0

            # Verify resolver called with correct bare trigger strings
            assert mock_resolve.call_count == 2
            calls = [call.args for call in mock_resolve.call_args_list]
            assert calls[0][0] == "first entry"
            assert calls[1][0] == "second entry"

            # Verify output contains both resolved contents separated by ---
            assert "# First Entry Resolved" in result.output
            assert "Content 1" in result.output
            assert "# Second Entry Resolved" in result.output
            assert "Content 2" in result.output
            assert "---" in result.output


def test_resolve_argument_mode_happy_path() -> None:
    """Resolve argument mode: each arg is trigger, resolve, output results."""
    runner = CliRunner()
    with (
        runner.isolated_filesystem(),
        patch("claudeutils.recall_cli.cli.resolve") as mock_resolve,
    ):
        mock_resolve.side_effect = [
            "Content for mock tests",
            "Content for encode paths",
        ]

        # Arguments: triggers passed directly (not artifact paths)
        result = runner.invoke(
            cli,
            ["_recall", "resolve", "when writing mock tests", "how encode paths"],
        )

        # Verify exit code 0
        assert result.exit_code == 0

        # Verify resolver called with correct bare trigger strings
        assert mock_resolve.call_count == 2
        calls = [call.args for call in mock_resolve.call_args_list]
        assert calls[0][0] == "writing mock tests"
        assert calls[1][0] == "encode paths"

        # Verify output contains both resolved contents
        assert "Content for mock tests" in result.output
        assert "Content for encode paths" in result.output
        assert "---" in result.output
