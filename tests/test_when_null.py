"""Tests for null mode in when CLI."""

from pathlib import Path

from click.testing import CliRunner

from edify.cli import cli


def test_null_query_exits_silently() -> None:
    """Null query is a D+B gate anchor — exit 0, empty output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["when", "null"])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_null_mixed_with_real_queries() -> None:
    """Null entries filtered; real queries resolve normally."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        iso_index = Path("agents") / "memory-index.md"
        iso_index.parent.mkdir(parents=True, exist_ok=True)
        iso_index.write_text("## testing\n\n/when writing mock tests | pattern\n")

        iso_decisions = Path("agents") / "decisions"
        iso_decisions.mkdir(parents=True, exist_ok=True)
        (iso_decisions / "testing.md").write_text(
            "# Test Guide\n"
            "\n"
            "## When Writing Mock Tests\n"
            "\n"
            "Use mocks for external dependencies.\n"
        )

        result = runner.invoke(cli, ["when", "null", "when writing mock tests"])

    assert result.exit_code == 0
    assert "When Writing Mock Tests" in result.output
    # "null" must not appear as a resolved result — only the real query resolves
    output_lines = [ln.strip() for ln in result.output.splitlines() if ln.strip()]
    assert not any(ln == "null" for ln in output_lines)


def test_when_null_operator_prefix() -> None:
    """Operator-prefixed null is filtered ('when null' → 'null')."""
    runner = CliRunner()
    result = runner.invoke(cli, ["when", "when null"])
    assert result.exit_code == 0
    assert result.output.strip() == ""
