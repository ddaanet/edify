"""Tests for _recall resolve subcommand."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.when.resolver import ResolveError


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


def test_resolve_artifact_mode_any_failure_exits_1() -> None:
    """Artifact mode: any resolution failure exits 1 (strict semantics)."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create artifact with three entries
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

when first entry — annotation for first
when second entry — annotation for second
when third entry — annotation for third
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        with patch("claudeutils.recall_cli.cli.resolve") as mock_resolve:
            # First resolves successfully, second raises error, third resolves
            mock_resolve.side_effect = [
                "Content 1",
                ResolveError("second entry not found"),
                "Content 3",
            ]

            result = runner.invoke(cli, ["_recall", "resolve", str(artifact_path)])

            # Verify exit code 1 (any non-null failure in artifact mode)
            assert result.exit_code == 1

            # Verify resolver called for all three triggers
            assert mock_resolve.call_count == 3

            # Verify successful content is in output
            assert "Content 1" in result.output
            assert "Content 3" in result.output

            # Verify error message in output
            assert "second entry" in result.output
            assert "error" in result.output.lower()


def test_resolve_argument_mode_partial_success_exits_0() -> None:
    """Argument mode: ≥1 resolved content exits 0 (best-effort semantics)."""
    runner = CliRunner()
    with (
        runner.isolated_filesystem(),
        patch("claudeutils.recall_cli.cli.resolve") as mock_resolve,
    ):
        # First succeeds, second fails, third succeeds
        mock_resolve.side_effect = [
            "Content for first",
            ResolveError("second not found"),
            "Content for third",
        ]

        result = runner.invoke(
            cli,
            [
                "_recall",
                "resolve",
                "when first trigger",
                "when second trigger",
                "when third trigger",
            ],
        )

        # Verify exit code 0 (≥1 success)
        assert result.exit_code == 0

        # Verify resolver called for all three
        assert mock_resolve.call_count == 3

        # Verify successful content in output
        assert "Content for first" in result.output
        assert "Content for third" in result.output

        # Verify error message in output
        assert "second trigger" in result.output


def test_resolve_argument_mode_total_failure_exits_1() -> None:
    """Argument mode: zero resolved content exits 1 (best-effort semantics)."""
    runner = CliRunner()
    with (
        runner.isolated_filesystem(),
        patch("claudeutils.recall_cli.cli.resolve") as mock_resolve,
    ):
        # All three fail
        mock_resolve.side_effect = [
            ResolveError("first not found"),
            ResolveError("second not found"),
            ResolveError("third not found"),
        ]

        result = runner.invoke(
            cli,
            [
                "_recall",
                "resolve",
                "when first trigger",
                "when second trigger",
                "when third trigger",
            ],
        )

        # Verify exit code 1 (zero successes)
        assert result.exit_code == 1

        # Verify resolver called for all three
        assert mock_resolve.call_count == 3

        # Verify error messages in output
        assert "first trigger" in result.output
        assert "second trigger" in result.output
        assert "third trigger" in result.output


def test_resolve_null_entries_silent() -> None:
    """Null entries are silently skipped, not resolved or failed."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create artifact with one valid entry and one null entry
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

when real entry — has annotation
null — no relevant entries found
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        with patch("claudeutils.recall_cli.cli.resolve") as mock_resolve:
            # Only the real entry should be resolved
            mock_resolve.side_effect = [
                "Content for real entry",
            ]

            result = runner.invoke(cli, ["_recall", "resolve", str(artifact_path)])

            # Verify exit code 0
            assert result.exit_code == 0

            # Verify resolver called only once (null skipped)
            assert mock_resolve.call_count == 1

            # Verify resolved content in output
            assert "Content for real entry" in result.output


def test_resolve_dedup_content() -> None:
    """Identical content from different triggers appears once (dedup)."""
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

        with patch("claudeutils.recall_cli.cli.resolve") as mock_resolve:
            # Both resolve to the same content
            mock_resolve.side_effect = [
                "Shared content for both",
                "Shared content for both",
            ]

            result = runner.invoke(cli, ["_recall", "resolve", str(artifact_path)])

            # Verify exit code 0
            assert result.exit_code == 0

            # Verify resolver called for both
            assert mock_resolve.call_count == 2

            # Verify content appears only once in output (deduped)
            output_content = result.output
            count = output_content.count("Shared content for both")
            assert count == 1
