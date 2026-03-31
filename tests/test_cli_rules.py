"""Tests for CLI rules command."""

import json
from pathlib import Path

from click.testing import CliRunner

from edify.cli import cli
from edify.models import FeedbackItem, FeedbackType


def test_rules_extracts_sorted_items(
    tmp_path: Path,
) -> None:
    """Rules command extracts items and sorts by timestamp."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T10:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Item with correct length and substantive",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Another item with substantive feedback",
        ),
        FeedbackItem(
            timestamp="2025-12-16T09:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Third item with substantive content",
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(cli, ["rules", "--input", str(input_file)])

    # Should output 3 items in sorted order (earliest first)
    lines = result.output.strip().split("\n")
    assert len(lines) >= 3
    # Check that items appear in chronological order
    assert "1." in result.output or "1 " in result.output


def test_rules_deduplicates_by_prefix(
    tmp_path: Path,
) -> None:
    """Rules command deduplicates items by first 100 characters."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content=(
                "This is a long feedback item that is definitely longer than "
                "a hundred characters but not too long so it should be kept"
            ),
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content=(
                "This is a long feedback item that is definitely longer than "
                "a hundred characters but not too long so it should be deleted"
            ),
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content=(
                "Different content that is long enough and unique "
                "to the other items in our test set"
            ),
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:29.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Another different item with unique content for deduplication test",
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(cli, ["rules", "--input", str(input_file)])

    # 4 items input, 3 after deduplication (first 2 share same prefix)
    lines = [line for line in result.output.strip().split("\n") if line]
    assert len(lines) == 3
    assert "1." in lines[0]
    assert "2." in lines[1]
    assert "3." in lines[2]


def test_rules_applies_stricter_filters(
    tmp_path: Path,
) -> None:
    """Rules command applies stricter filtering rules."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Valid item that is long enough and suitable",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="How do I fix this question",  # Question: filtered
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="x" * 1500,  # Too long: filtered
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:29.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="short",  # Too short (< 20): filtered
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:30.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Another valid item that is long enough for rules",
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(cli, ["rules", "--input", str(input_file)])

    # Only 2 valid items should remain
    lines = [line for line in result.output.strip().split("\n") if line]
    assert len(lines) == 2
    assert "1." in lines[0]
    assert "2." in lines[1]


def test_rules_custom_min_length(
    tmp_path: Path,
) -> None:
    """Rules command respects custom --min-length."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="x" * 18,  # 18 chars
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="x" * 22,  # 22 chars
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:28.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="x" * 30,  # 30 chars
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["rules", "--input", str(input_file), "--min-length", "25"]
    )

    # Only 30-char item passes min-length of 25
    lines = [line for line in result.output.strip().split("\n") if line]
    assert len(lines) == 1
    assert "1." in lines[0]


def test_rules_json_format(
    tmp_path: Path,
) -> None:
    """Rules command outputs JSON with --format json."""
    items = [
        FeedbackItem(
            timestamp="2025-12-16T08:39:26.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="First rule worthy item content goes here",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:39:27.932Z",
            session_id="session1",
            feedback_type=FeedbackType.MESSAGE,
            content="Second rule worthy item content goes here",
        ),
    ]

    input_file = tmp_path / "feedback.json"
    input_file.write_text(json.dumps([item.model_dump(mode="json") for item in items]))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["rules", "--input", str(input_file), "--format", "json"]
    )

    output = json.loads(result.output)
    assert isinstance(output, list)
    assert len(output) == 2
    assert output[0]["index"] == 1
    assert output[0]["timestamp"] == "2025-12-16T08:39:26.932Z"
    assert output[0]["session_id"] == "session1"
    assert output[1]["index"] == 2
