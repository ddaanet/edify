"""Tests for the when CLI command."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.when.cli import when_cmd
from claudeutils.when.resolver import ResolveError


def test_when_command_exists() -> None:
    """When command exists and responds to --help."""
    assert when_cmd is not None

    runner = CliRunner()
    result = runner.invoke(cli, ["when", "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_operator_prefix_stripped() -> None:
    """Operator prefix (when/how) stripped, bare trigger passed to resolver."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Test Result\n\nMocked content"

        # "when X" → strips prefix, passes bare trigger
        result = runner.invoke(cli, ["when", "when writing mock tests"])
        assert result.exit_code == 0
        mock_resolve.assert_called_once()
        assert mock_resolve.call_args[0][0] == "writing mock tests"

        mock_resolve.reset_mock()
        mock_resolve.return_value = "# Test Result\n\nMocked content"

        # "how X" → strips prefix
        result = runner.invoke(cli, ["when", "how encode paths"])
        assert result.exit_code == 0
        assert mock_resolve.call_args[0][0] == "encode paths"

        mock_resolve.reset_mock()
        mock_resolve.return_value = "# Test Result\n\nMocked content"

        # "WHEN X" → case-insensitive stripping
        result = runner.invoke(cli, ["when", "WHEN writing tests"])
        assert result.exit_code == 0
        assert mock_resolve.call_args[0][0] == "writing tests"


def test_bare_query_accepted() -> None:
    """Bare trigger (no operator prefix) passed directly to resolver."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Test Result\n\nMocked content"

        result = runner.invoke(cli, ["when", "writing mock tests"])
        assert result.exit_code == 0
        assert mock_resolve.call_args[0][0] == "writing mock tests"


def test_dot_prefix_preserved() -> None:
    """Dot prefix (section/file mode) preserved through operator stripping."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Mock Result\n\nMocked content"

        # "when .Section" → strips "when", preserves ".Section"
        result = runner.invoke(cli, ["when", "when .Section"])
        assert result.exit_code == 0
        assert mock_resolve.call_args[0][0] == ".Section"

        mock_resolve.reset_mock()
        mock_resolve.return_value = "# Mock Result\n\nMocked content"

        # "when ..file.md" → strips "when", preserves "..file.md"
        result = runner.invoke(cli, ["when", "when ..file.md"])
        assert result.exit_code == 0
        assert mock_resolve.call_args[0][0] == "..file.md"

    # No query args should error
    result = runner.invoke(cli, ["when"])
    assert result.exit_code != 0
    assert "No queries provided" in result.output


def test_cli_invokes_resolver(tmp_path: Path) -> None:
    """CLI invokes resolver and returns resolved content."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        iso_index = Path("agents") / "memory-index.md"
        iso_index.parent.mkdir(parents=True, exist_ok=True)
        iso_index.write_text("## testing\n\n/when writing mock tests | pattern\n")

        iso_decisions = Path("agents") / "decisions"
        iso_decisions.mkdir(parents=True, exist_ok=True)

        iso_testing_file = iso_decisions / "testing.md"
        iso_testing_file.write_text(
            "# Test Guide\n"
            "\n"
            "## When Writing Mock Tests\n"
            "\n"
            "Use mocks for external dependencies.\n"
        )

        result = runner.invoke(cli, ["when", "writing mock tests"])

    assert result.exit_code == 0
    assert "When Writing Mock Tests" in result.output


def test_batched_recall_multiple_queries() -> None:
    """Multiple queries produce batched output separated by ---."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# Result 1\n\nFirst content",
            "# Result 2\n\nSecond content",
        ]

        result = runner.invoke(
            cli, ["when", "when writing mock tests", "how encode paths"]
        )
        assert result.exit_code == 0
        assert mock_resolve.call_count == 2

        # Both calls pass bare trigger (operator stripped)
        assert mock_resolve.call_args_list[0][0][0] == "writing mock tests"
        assert mock_resolve.call_args_list[1][0][0] == "encode paths"

        assert "---" in result.output
        assert "# Result 1" in result.output
        assert "# Result 2" in result.output

    # Single query: no separator
    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Single Result\n\nContent"
        result = runner.invoke(cli, ["when", "writing mock tests"])
        assert result.exit_code == 0
        assert "---" not in result.output


def test_cli_error_handling() -> None:
    """Exit code 1 and diagnostic output for resolver errors."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        iso_index = Path("agents") / "memory-index.md"
        iso_index.parent.mkdir(parents=True, exist_ok=True)
        iso_index.write_text("## testing\n\n/when writing tests | tests\n")

        iso_decisions = Path("agents") / "decisions"
        iso_decisions.mkdir(parents=True, exist_ok=True)

        iso_testing_file = iso_decisions / "testing.md"
        iso_testing_file.write_text(
            "# Test Guide\n\n## When Writing Tests\n\nUse tests for coverage.\n"
        )

        # Nonexistent trigger
        result = runner.invoke(cli, ["when", "nonexistent trigger"])
        assert result.exit_code == 1
        assert "Did you mean:" in result.output

        # Nonexistent section
        result = runner.invoke(cli, ["when", ".NotExist"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

        # Nonexistent file
        result = runner.invoke(cli, ["when", "..nonexistent.md"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


def test_batch_accumulates_errors() -> None:
    """Batch prints successes first, then errors to stdout, exit 1."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# Result 1\n\nFirst content",
            ResolveError("No match for 'nonexistent'"),
        ]

        result = runner.invoke(cli, ["when", "writing mock tests", "nonexistent"])
        assert result.exit_code == 1
        assert "# Result 1" in result.output
        assert "First content" in result.output
        assert "No match for 'nonexistent'" in result.output
        success_pos = result.output.index("Result 1")
        error_pos = result.output.index("No match")
        assert success_pos < error_pos


def test_batch_all_succeed_exit_zero() -> None:
    """Batch with all successes exits 0."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# Result 1\n\nFirst",
            "# Result 2\n\nSecond",
        ]

        result = runner.invoke(cli, ["when", "query one", "query two"])
        assert result.exit_code == 0
        assert "Result 1" in result.output
        assert "Result 2" in result.output


def test_dedup_identical_results() -> None:
    """Duplicate resolved results are emitted once."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        # Two different queries resolve to the same content
        mock_resolve.side_effect = [
            "# Same Entry\n\nContent here",
            "# Same Entry\n\nContent here",
        ]

        result = runner.invoke(cli, ["when", "query one", "query two"])
        assert result.exit_code == 0
        assert result.output.count("# Same Entry") == 1
        assert "---" not in result.output


def test_dedup_preserves_distinct() -> None:
    """Distinct resolved results are all emitted."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# Entry A\n\nFirst",
            "# Entry A\n\nFirst",
            "# Entry B\n\nSecond",
        ]

        result = runner.invoke(cli, ["when", "q1", "q2", "q3"])
        assert result.exit_code == 0
        assert result.output.count("# Entry A") == 1
        assert result.output.count("# Entry B") == 1
        assert "---" in result.output


def test_stdin_queries() -> None:
    """Queries read from stdin (one per line)."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Result\n\nContent"

        result = runner.invoke(cli, ["when"], input="writing mock tests\n")
        assert result.exit_code == 0
        assert "# Result" in result.output
        mock_resolve.assert_called_once()
        assert mock_resolve.call_args[0][0] == "writing mock tests"


def test_stdin_multiple_lines() -> None:
    """Multiple stdin lines produce multiple queries."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# Result 1\n\nFirst",
            "# Result 2\n\nSecond",
        ]

        result = runner.invoke(cli, ["when"], input="query one\nquery two\n")
        assert result.exit_code == 0
        assert mock_resolve.call_count == 2
        assert "---" in result.output


def test_stdin_skips_blank_lines() -> None:
    """Blank lines in stdin are ignored."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Result\n\nContent"

        result = runner.invoke(cli, ["when"], input="\n  \nactual query\n\n")
        assert result.exit_code == 0
        mock_resolve.assert_called_once()


def test_stdin_combined_with_args() -> None:
    """Stdin queries combined with CLI arg queries."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# From Args\n\nArg content",
            "# From Stdin\n\nStdin content",
        ]

        result = runner.invoke(cli, ["when", "arg query"], input="stdin query\n")
        assert result.exit_code == 0
        assert mock_resolve.call_count == 2
        assert "# From Args" in result.output
        assert "# From Stdin" in result.output


def test_stdin_strips_operator_prefix() -> None:
    """Operator prefix stripped from stdin queries too."""
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Result\n\nContent"

        result = runner.invoke(cli, ["when"], input="when writing tests\n")
        assert result.exit_code == 0
        assert mock_resolve.call_args[0][0] == "writing tests"


def test_no_queries_error() -> None:
    """Error when no queries from args or stdin."""
    runner = CliRunner()
    result = runner.invoke(cli, ["when"])
    assert result.exit_code != 0
    assert "No queries provided" in result.output
