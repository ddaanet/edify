"""Tests for CLI collect command."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.cli import cli
from edify.models import FeedbackItem, FeedbackType, SessionInfo


def test_collect_single_session_with_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collect extracts feedback from single session."""
    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        feedback_type=FeedbackType.MESSAGE,
        content="This is feedback",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
                title="Test session",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)

    runner = CliRunner()
    result = runner.invoke(cli, ["collect"])

    output = json.loads(result.output)
    assert isinstance(output, list)
    assert len(output) == 1
    assert output[0]["content"] == "This is feedback"


def test_collect_multiple_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collect aggregates feedback from multiple sessions."""
    feedback_1 = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Feedback from session 1",
    )
    feedback_2 = FeedbackItem(
        timestamp="2025-12-16T09:39:26.932Z",
        session_id="session2",
        feedback_type=FeedbackType.MESSAGE,
        content="Feedback from session 2",
    )
    feedback_3 = FeedbackItem(
        timestamp="2025-12-16T10:39:26.932Z",
        session_id="session3",
        feedback_type=FeedbackType.MESSAGE,
        content="Feedback from session 3",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Session 1",
                timestamp="2025-12-16T08:39:26.932Z",
            ),
            SessionInfo(
                session_id="session2",
                title="Session 2",
                timestamp="2025-12-16T09:39:26.932Z",
            ),
            SessionInfo(
                session_id="session3",
                title="Session 3",
                timestamp="2025-12-16T10:39:26.932Z",
            ),
        ]

    feedback_by_session = {
        "session1": [feedback_1],
        "session2": [feedback_2],
        "session3": [feedback_3],
    }

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return feedback_by_session.get(session_id, [])

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)

    runner = CliRunner()
    result = runner.invoke(cli, ["collect"])

    output = json.loads(result.output)
    assert isinstance(output, list)
    assert len(output) == 3
    assert output[0]["content"] == "Feedback from session 1"
    assert output[1]["content"] == "Feedback from session 2"
    assert output[2]["content"] == "Feedback from session 3"


def test_collect_with_subagents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collect includes feedback from nested sub-agents."""
    # Main session has 2 feedback items
    main_1 = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Main feedback 1",
    )
    main_2 = FeedbackItem(
        timestamp="2025-12-16T08:39:27.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Main feedback 2",
    )
    # Sub-agent has 2 feedback items
    sub_1 = FeedbackItem(
        timestamp="2025-12-16T08:39:28.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Subagent feedback 1",
        agent_id="agent1",
    )
    sub_2 = FeedbackItem(
        timestamp="2025-12-16T08:39:29.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Subagent feedback 2",
        agent_id="agent1",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Session with subagents",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        # extract_feedback_recursively returns main + subagent feedback
        return [main_1, main_2, sub_1, sub_2]

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)

    runner = CliRunner()
    result = runner.invoke(cli, ["collect"])

    output = json.loads(result.output)
    assert isinstance(output, list)
    assert len(output) == 4
    assert output[0]["content"] == "Main feedback 1"
    assert output[1]["content"] == "Main feedback 2"
    assert output[2]["content"] == "Subagent feedback 1"
    assert output[3]["content"] == "Subagent feedback 2"


def test_collect_skips_malformed_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collect skips malformed sessions and logs warning."""
    valid_feedback = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Valid feedback",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Valid session",
                timestamp="2025-12-16T08:39:26.932Z",
            ),
            SessionInfo(
                session_id="session2",
                title="Malformed session",
                timestamp="2025-12-16T09:39:26.932Z",
            ),
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        if session_id == "session1":
            return [valid_feedback]
        # Simulate extraction error for malformed session
        raise ValueError("Malformed data")

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)

    runner = CliRunner()
    result = runner.invoke(cli, ["collect"])

    # The warning message is on one line, JSON output is on another
    # Try to extract just the JSON part by finding the [ character
    output_lines = result.output.split("\n")
    json_output = None
    for line in output_lines:
        if line.strip().startswith("["):
            json_output = line
            break

    if json_output:
        output = json.loads(json_output)
        assert len(output) == 1
        assert output[0]["content"] == "Valid feedback"
    else:
        # If no JSON found, this is an error
        raise AssertionError(f"Could not find JSON in output: {result.output}")

    # Check for warning in the output
    assert "Warning" in result.output or "warning" in result.output.lower()


def test_collect_output_to_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Collect writes JSON to file with --output flag."""
    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )
    output_file = tmp_path / "output.json"

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Test session",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr("edify.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("edify.cli.extract_feedback_recursively", mock_extract)

    runner = CliRunner()
    result = runner.invoke(cli, ["collect", "--output", str(output_file)])

    # Verify file was written
    assert output_file.exists()
    output = json.loads(output_file.read_text())
    assert len(output) == 1
    assert output[0]["content"] == "Test feedback"

    # Verify nothing printed to stdout
    assert result.output == ""
