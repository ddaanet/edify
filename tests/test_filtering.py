"""Tests for the filtering module."""

from edify.filtering import categorize_feedback, filter_feedback, is_noise
from edify.models import FeedbackItem, FeedbackType


def test_is_noise_command_output_detected() -> None:
    """Test that command output markers are detected as noise."""
    content = "<command-name>/clear</command-name>"
    assert is_noise(content) is True


def test_is_noise_bash_output_detected() -> None:
    """Test that bash output markers are detected as noise."""
    content = "<bash-stdout>test output</bash-stdout>"
    assert is_noise(content) is True


def test_is_noise_system_message_detected() -> None:
    """Test that system message markers are detected as noise."""
    content = "Caveat: The messages below"
    assert is_noise(content) is True


def test_is_noise_short_message_detected() -> None:
    """Test that short messages (< 10 chars) are detected as noise."""
    content = "hello"
    assert is_noise(content) is True


def test_categorize_instruction() -> None:
    """Test that instruction content is categorized correctly."""
    item = FeedbackItem(
        timestamp="2025-01-01T00:00:00Z",
        session_id="test-session",
        feedback_type=FeedbackType.MESSAGE,
        content="Don't use git add -A",
    )
    assert categorize_feedback(item) == "instructions"


def test_categorize_correction() -> None:
    """Test that correction content is categorized correctly."""
    item = FeedbackItem(
        timestamp="2025-01-01T00:00:00Z",
        session_id="test-session",
        feedback_type=FeedbackType.MESSAGE,
        content="No, that's the wrong approach",
    )
    assert categorize_feedback(item) == "corrections"


def test_categorize_process() -> None:
    """Test that process content is categorized correctly."""
    item = FeedbackItem(
        timestamp="2025-01-01T00:00:00Z",
        session_id="test-session",
        feedback_type=FeedbackType.MESSAGE,
        content="Before committing, run the tests",
    )
    assert categorize_feedback(item) == "process"


def test_categorize_code_review() -> None:
    """Test that code review content is categorized correctly."""
    item = FeedbackItem(
        timestamp="2025-01-01T00:00:00Z",
        session_id="test-session",
        feedback_type=FeedbackType.MESSAGE,
        content="Please review this refactored code",
    )
    assert categorize_feedback(item) == "code_review"


def test_filter_feedback_removes_noise() -> None:
    """Test that filter_feedback removes noise items."""
    items = [
        FeedbackItem(
            timestamp="2025-01-01T00:00:00Z",
            session_id="test-session",
            feedback_type=FeedbackType.MESSAGE,
            content="<command-name>/clear</command-name>",
        ),
        FeedbackItem(
            timestamp="2025-01-01T00:00:01Z",
            session_id="test-session",
            feedback_type=FeedbackType.MESSAGE,
            content="This is substantive feedback",
        ),
        FeedbackItem(
            timestamp="2025-01-01T00:00:02Z",
            session_id="test-session",
            feedback_type=FeedbackType.MESSAGE,
            content="More substantive feedback here",
        ),
    ]
    result = filter_feedback(items)
    assert len(result) == 2


def test_filter_feedback_preserves_order() -> None:
    """Test that filter_feedback preserves original order."""
    items = [
        FeedbackItem(
            timestamp="2025-01-01T00:00:00Z",
            session_id="test-session",
            feedback_type=FeedbackType.MESSAGE,
            content="First feedback",
        ),
        FeedbackItem(
            timestamp="2025-01-01T00:00:01Z",
            session_id="test-session",
            feedback_type=FeedbackType.MESSAGE,
            content="hi",
        ),
        FeedbackItem(
            timestamp="2025-01-01T00:00:02Z",
            session_id="test-session",
            feedback_type=FeedbackType.MESSAGE,
            content="Second feedback",
        ),
    ]
    result = filter_feedback(items)
    assert result[0].content == "First feedback"
    assert result[1].content == "Second feedback"
