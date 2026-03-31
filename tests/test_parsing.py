"""Tests for message parsing and feedback extraction."""

import pytest
from pydantic import ValidationError

from edify.models import FeedbackItem, FeedbackType
from edify.parsing import (
    extract_feedback_from_entry,
    is_trivial,
)

from . import pytest_helpers as helpers


def test_is_trivial_empty_string() -> None:
    """Empty string is trivial."""
    assert is_trivial("") is True


def test_is_trivial_whitespace_only() -> None:
    """Whitespace-only strings are trivial."""
    assert is_trivial(" ") is True
    assert is_trivial("   ") is True
    assert is_trivial("\t") is True
    assert is_trivial("\n") is True
    assert is_trivial(" \t\n ") is True


def test_is_trivial_single_character() -> None:
    """Any single character is trivial."""
    assert is_trivial("a") is True
    assert is_trivial("z") is True
    assert is_trivial("1") is True
    assert is_trivial("!") is True
    assert is_trivial(" x ") is True  # Single char with whitespace


def test_is_trivial_yes_no_variants() -> None:
    """Yes/no variations are trivial (case-insensitive)."""
    assert is_trivial("y") is True
    assert is_trivial("Y") is True
    assert is_trivial("n") is True
    assert is_trivial("N") is True
    assert is_trivial("yes") is True
    assert is_trivial("YES") is True
    assert is_trivial("no") is True
    assert is_trivial("No") is True


def test_is_trivial_keywords_with_whitespace() -> None:
    """Trivial keywords with leading/trailing whitespace."""
    for text in [" continue ", "\tok\t", "  yes  ", "\nresume\n"]:
        assert is_trivial(text) is True


def test_is_trivial_slash_commands() -> None:
    """Slash commands are trivial."""
    for text in ["/model", "/clear", "/help", "/commit", " /model "]:
        assert is_trivial(text) is True


def test_is_trivial_substantive_messages() -> None:
    """Substantive messages are NOT trivial."""
    for text in [
        "Design a python script",
        "Help me with this bug",
        "yesterday",  # Contains 'y' but not exact match
        "yes I think that works",  # Contains keyword with other text
    ]:
        assert is_trivial(text) is False


def test_is_trivial_exact_match_only() -> None:
    """Case insensitivity applies only to exact keyword matches."""
    # Exact matches are trivial
    for text in ["YeS", "OK", "ContinUE"]:
        assert is_trivial(text) is True

    # Keywords + extra text are NOT trivial
    for text in ["Yes please", "OK done", "continue with this"]:
        assert is_trivial(text) is False


def test_extract_feedback_non_user_message() -> None:
    """Non-user messages (type=assistant) return None."""
    entry = {
        "type": "assistant",
        "message": {"role": "assistant", "content": "Some response"},
        "timestamp": helpers.TS_BASE,
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    assert extract_feedback_from_entry(entry) is None


def test_extract_feedback_trivial_message() -> None:
    """Trivial user messages return None."""
    entry = {
        "type": "user",
        "message": {"role": "user", "content": "resume"},
        "timestamp": "2025-12-16T08:43:52.198Z",
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    assert extract_feedback_from_entry(entry) is None


def test_extract_feedback_substantive_message() -> None:
    """Substantive user messages return FeedbackItem."""
    content = "Design a python script to extract user feedback"
    entry = {
        "type": "user",
        "message": {"role": "user", "content": content},
        "timestamp": "2025-12-16T08:39:26.932Z",
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    expected = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id=helpers.SESSION_ID_MAIN,
        feedback_type=FeedbackType.MESSAGE,
        content=content,
    )
    assert extract_feedback_from_entry(entry) == expected


def test_extract_feedback_tool_denial_main_session() -> None:
    """Tool denial in main session returns FeedbackItem."""
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "is_error": True,
                    "content": "[Request interrupted by user for tool use]",
                    "tool_use_id": "toolu_01Q9nwwXaokrfKdLpUDCLHt7",
                }
            ],
        },
        "timestamp": "2025-12-16T08:43:43.872Z",
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.feedback_type == FeedbackType.TOOL_DENIAL
    assert result.tool_use_id == "toolu_01Q9nwwXaokrfKdLpUDCLHt7"
    assert result.content == "[Request interrupted by user for tool use]"
    assert result.agent_id is None


def test_extract_feedback_tool_denial_subagent() -> None:
    """Tool denial in sub-agent includes agentId and slug."""
    denial_msg = (
        "The user doesn't want to proceed with this tool use. "
        "The tool use was rejected (eg. if it was a file edit, the "
        "new_string was NOT written to the file). STOP what you are "
        "doing and wait for the user to tell you how to proceed."
    )
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "content": denial_msg,
                    "is_error": True,
                    "tool_use_id": "toolu_0165cVNnbPXQCt22gTrTXnQq",
                }
            ],
        },
        "timestamp": "2025-12-16T08:43:43.789Z",
        "sessionId": helpers.SESSION_ID_MAIN,
        "agentId": "a6755ed",
        "slug": "fluffy-cuddling-forest",
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.feedback_type == FeedbackType.TOOL_DENIAL
    assert result.agent_id == "a6755ed"
    assert result.slug == "fluffy-cuddling-forest"
    assert result.content == denial_msg


def test_extract_feedback_request_interruption() -> None:
    """Request interruption returns FeedbackItem with INTERRUPTION type."""
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {"type": "text", "text": "[Request interrupted by user for tool use]"}
            ],
        },
        "timestamp": "2025-12-16T08:43:43.872Z",
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.feedback_type == FeedbackType.INTERRUPTION
    assert "[Request interrupted" in result.content


def test_extract_feedback_missing_session_id() -> None:
    """Missing sessionId field returns FeedbackItem with empty string."""
    entry = {
        "type": "user",
        "message": {"role": "user", "content": "Design a python script"},
        "timestamp": "2025-12-16T08:39:26.932Z",
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.session_id == ""


def test_extract_feedback_malformed_content_empty_list() -> None:
    """Tool result with empty content list returns None."""
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [],
        },
        "timestamp": "2025-12-16T08:39:26.932Z",
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    assert extract_feedback_from_entry(entry) is None


def test_extract_feedback_pydantic_validation_error() -> None:
    """Invalid timestamp format raises ValidationError."""
    entry = {
        "type": "user",
        "message": {"role": "user", "content": "Design a script"},
        "timestamp": 12345,  # Invalid: should be string
        "sessionId": helpers.SESSION_ID_MAIN,
    }
    with pytest.raises(ValidationError):
        extract_feedback_from_entry(entry)
