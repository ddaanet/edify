"""Tests for CLI analyze command."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.cli import cli
from edify.models import FeedbackItem, FeedbackType


def test_analyze_counts_and_categorizes(
    tmp_path: Path,
) -> None:
    """Analyze counts feedback items and categorizes them."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Don't do this",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Always use this",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="No, that's wrong",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:29.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="That's incorrect",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:30.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Before you commit, test it",
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--input", str(input_file)])

    assert "total:" in result.output or "Total:" in result.output
    assert "filtered:" in result.output or "Filtered:" in result.output


def test_analyze_filters_noise(
    tmp_path: Path,
) -> None:
    """Analyze filters out noise items correctly."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Substantive feedback 1",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="hi",  # Noise: short message
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Substantive feedback 2",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:29.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="<bash-stdout>output</bash-stdout>",  # Noise: bash output
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:30.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Substantive feedback 3",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:31.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="y",  # Noise: single char
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:32.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Substantive feedback 4",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:33.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Caveat: some message",  # Noise: system message
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--input", str(input_file)])

    # Total: 8, Filtered: 4 (removed 4 noise items)
    assert "total: 8" in result.output
    assert "filtered: 4" in result.output


def test_analyze_from_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Analyze reads from stdin when given - as input."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Feedback 1",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Feedback 2",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Feedback 3",
        ),
    ]

    json_input = json.dumps([item.model_dump(mode="json") for item in items])

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--input", "-"], input=json_input)

    # Total: 3, Filtered: 3 (no noise)
    assert "total: 3" in result.output
    assert "filtered: 3" in result.output


def test_analyze_json_format(
    tmp_path: Path,
) -> None:
    """Analyze outputs JSON format with --format json."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Don't do this",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="That's wrong",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Before testing",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:29.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Please review",
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["analyze", "--input", str(input_file), "--format", "json"]
    )

    output = json.loads(result.output)
    assert output["total"] == 4
    assert output["filtered"] == 4
    assert "categories" in output
    assert isinstance(output["categories"], dict)
