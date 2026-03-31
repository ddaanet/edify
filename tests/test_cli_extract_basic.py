"""Tests for CLI extract command - basic execution and session resolution."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.cli import cli
from edify.models import FeedbackItem, FeedbackType

from . import pytest_helpers


def test_extract_command_basic(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Extract command outputs JSON array to stdout."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-test-project"
    history_dir.mkdir(parents=True)
    (history_dir / f"{pytest_helpers.SESSION_ID_MAIN}.jsonl").write_text(
        '{"test": 1}\n'
    )

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=pytest_helpers.SESSION_ID_MAIN,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)
    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "e12d203f"])

    output = json.loads(result.output)
    assert isinstance(output, list)
    assert len(output) == 1


def test_extract_with_output_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract command with --output writes to file."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-test-project"
    history_dir.mkdir(parents=True)
    (history_dir / f"{pytest_helpers.SESSION_ID_MAIN}.jsonl").write_text(
        '{"test": 1}\n'
    )

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=pytest_helpers.SESSION_ID_MAIN,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return [feedback_item]

    output_file = tmp_path / "feedback.json"

    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)
    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    runner.invoke(cli, ["extract", "e12d203f", "--output", str(output_file)])

    # Verify file was written with valid JSON
    content = output_file.read_text()
    output = json.loads(content)
    assert isinstance(output, list)
    assert len(output) == 1


def test_extract_with_project_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract command respects --project flag."""
    history_dir = tmp_path / ".claude" / "projects" / "-custom"
    history_dir.mkdir(parents=True)

    session_id = "abc123de-f123-4567-89ab-cdef0123456a"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    called_with = []

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        called_with.append((sid, proj))
        return []

    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)
    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )

    runner = CliRunner()
    runner.invoke(cli, ["extract", "abc123", "--project", "/custom/path"])

    assert called_with == [(session_id, "/custom/path")]


def test_extract_full_session_id(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract with full session ID finds and extracts from session."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id = pytest_helpers.SESSION_ID_MAIN
    session_file = history_dir / f"{session_id}.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Test"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"'
        + session_id
        + '"}\n'
    )

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=session_id,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)
    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "e12d203f-ca65-44f0-9976-cb10b74514c1"])

    output = json.loads(result.output)
    assert len(output) == 1


def test_extract_partial_prefix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract with partial prefix finds matching session."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id = pytest_helpers.SESSION_ID_MAIN
    session_file = history_dir / f"{session_id}.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Test"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"'
        + session_id
        + '"}\n'
    )

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=session_id,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    called_with = []

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        called_with.append(sid)
        return [feedback_item]

    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)
    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    runner.invoke(cli, ["extract", "e12d203f"])

    # Should call extract with full session ID, not the prefix
    assert called_with == [session_id]


def test_extract_ambiguous_prefix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract with ambiguous prefix errors."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id1 = pytest_helpers.SESSION_ID_MAIN
    session_id2 = "e12d203f-aaaa-bbbb-cccc-dddddddddddd"

    (history_dir / f"{session_id1}.jsonl").write_text('{"test": 1}\n')
    (history_dir / f"{session_id2}.jsonl").write_text('{"test": 2}\n')

    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "e12d203f"])

    assert result.exit_code == 1


def test_extract_no_matching_session(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract with no matching session errors."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    monkeypatch.setattr(
        "edify.cli.get_project_history_dir",
        lambda p: history_dir,
    )
    monkeypatch.chdir(project_dir)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "zzzzzzz"])

    assert result.exit_code == 1
