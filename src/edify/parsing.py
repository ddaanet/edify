"""Message parsing and feedback extraction utilities."""

import json
from pathlib import Path
from typing import Any

from .models import FeedbackItem, FeedbackType


def extract_content_text(content: str | list[dict[str, Any]]) -> str:
    """Extract text from string or array content."""
    if isinstance(content, str):
        return content
    # If it's a list, find first dict with type="text" and extract text field
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if isinstance(text, str):
                    return text
    return ""


def format_title(text: str) -> str:
    """Handle newlines and truncation in titles."""
    # Replace newlines with spaces
    text = text.replace("\n", " ")
    # Truncate to 80 chars if needed
    if len(text) > 80:
        text = text[:77] + "..."
    return text


def is_trivial(text: str) -> bool:
    """Determine whether user feedback should be filtered as trivial.

    Filters out:
    - Empty strings or whitespace only
    - Single characters
    - Short affirmations: y, n, k, g, ok, go, yes, no, continue, proceed,
      sure, okay, resume
    - Slash commands (starting with /)

    Args:
        text: User feedback text to evaluate

    Returns:
        True if text is trivial (should be filtered), False if substantive
    """
    stripped = text.strip()

    # Empty or whitespace only
    if not stripped:
        return True

    # Single character
    if len(stripped) == 1:
        return True

    # Slash command
    if stripped.startswith("/"):
        return True

    # Trivial keywords
    trivial_keywords = {
        "y",
        "n",
        "k",
        "g",
        "ok",
        "go",
        "yes",
        "no",
        "continue",
        "proceed",
        "sure",
        "okay",
        "resume",
    }

    return stripped.lower() in trivial_keywords


def extract_feedback_from_entry(entry: dict[str, Any]) -> FeedbackItem | None:
    """Extract non-trivial user feedback from a conversation entry.

    Args:
        entry: A conversation entry dict from a session JSONL file

    Returns:
        FeedbackItem if feedback is found, None otherwise
    """
    # Only process user messages
    if entry.get("type") != "user":
        return None

    # Extract content from message
    message = entry.get("message", {})
    content = message.get("content", "")

    # Check for tool denial (error in tool_result)
    if isinstance(content, list) and len(content) > 0:
        item = content[0]
        if isinstance(item, dict) and item.get("is_error") is True:
            error_content = item.get("content", "")
            tool_use_id = item.get("tool_use_id")
            return FeedbackItem(
                timestamp=entry.get("timestamp", ""),
                session_id=entry.get("sessionId", ""),
                feedback_type=FeedbackType.TOOL_DENIAL,
                content=error_content,
                agent_id=entry.get("agentId"),
                slug=entry.get("slug"),
                tool_use_id=tool_use_id,
            )

    # Extract text for regular messages
    text = extract_content_text(content)

    # Check for request interruption
    if "[Request interrupted" in text:
        return FeedbackItem(
            timestamp=entry.get("timestamp", ""),
            session_id=entry.get("sessionId", ""),
            feedback_type=FeedbackType.INTERRUPTION,
            content=text,
            agent_id=entry.get("agentId"),
            slug=entry.get("slug"),
        )

    # Filter trivial messages
    if is_trivial(text):
        return None

    # Create FeedbackItem for substantive messages
    return FeedbackItem(
        timestamp=entry.get("timestamp", ""),
        session_id=entry.get("sessionId", ""),
        feedback_type=FeedbackType.MESSAGE,
        content=text,
        agent_id=entry.get("agentId"),
        slug=entry.get("slug"),
    )


def _extract_feedback_from_file(file_path: Path) -> list[FeedbackItem]:
    """Extract feedback items from a single JSONL file.

    Args:
        file_path: Path to JSONL file

    Returns:
        List of FeedbackItem objects extracted from file
    """
    feedback: list[FeedbackItem] = []
    for line in file_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            entry = json.loads(line)
            result = extract_feedback_from_entry(entry)
            if result:
                feedback.append(result)
        except json.JSONDecodeError:
            continue
    return feedback
