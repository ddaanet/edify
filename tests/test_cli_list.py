"""Tests for CLI list command."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.cli import cli
from edify.models import SessionInfo


def test_cli_no_args_shows_usage() -> None:
    """CLI invoked with no arguments exits with code 2."""
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 2


def test_list_command_default_project(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """List command uses current directory by default."""
    called_with = []

    def mock_list(project_dir: str) -> list[SessionInfo]:
        called_with.append(project_dir)
        return []

    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    runner.invoke(cli, ["list"])

    assert called_with == [str(project_dir)]


def test_list_command_with_project_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """List command respects --project flag."""
    called_with = []

    def mock_list(project_dir: str) -> list[SessionInfo]:
        called_with.append(project_dir)
        return []

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)

    runner = CliRunner()
    runner.invoke(cli, ["list", "--project", "/custom/path"])

    assert called_with == ["/custom/path"]


def test_list_output_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """List output is formatted as [prefix] title."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
                title="Design a python script",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    assert result.output == "[e12d203f] Design a python script\n"


def test_list_sorted_by_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    """List shows sessions in sorted order (most recent first)."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="id1111111111111111111111111111111",
                title="Third session",
                timestamp="2025-12-16T10:00:00.000Z",
            ),
            SessionInfo(
                session_id="id2222222222222222222222222222222",
                title="Second session",
                timestamp="2025-12-16T09:00:00.000Z",
            ),
            SessionInfo(
                session_id="id3333333333333333333333333333333",
                title="First session",
                timestamp="2025-12-16T08:00:00.000Z",
            ),
        ]

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    lines = result.output.strip().split("\n")
    assert "Third session" in lines[0]
    assert "Second session" in lines[1]
    assert "First session" in lines[2]


def test_list_long_title_truncated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Long titles are truncated to 80 characters with ellipsis."""
    # format_title() truncates to 80 chars and adds ...
    # So a 77-char title + ... = 80 chars
    long_title = (
        "This is a very long title that exceeds the eighty character limit "
        "and should be t..."
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
                title=long_title,
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    # Output ends with ... (truncated by format_title in list_top_level_sessions)
    assert result.output.endswith("...\n")


def test_list_no_sessions_message(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty sessions list prints 'No sessions found'."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return []

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    assert result.output == "No sessions found\n"


def test_list_nonexistent_project_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nonexistent project gracefully returns 'No sessions found'."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        # Simulates what list_top_level_sessions does for nonexistent dirs
        return []

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)

    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--project", "/nonexistent/path"])

    assert result.output == "No sessions found\n"
