"""Extract tool calls from session JSONL files."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolCall(BaseModel):
    """Tool call extracted from assistant JSONL entry."""

    tool_name: str  # "Read", "Grep", "Glob", "Bash", "Write", etc.
    tool_id: str  # tool_use id for correlation
    input: dict[str, Any]  # tool-specific arguments
    timestamp: str  # ISO 8601
    session_id: str


def _parse_json_line(
    line_text: str, line_num: int, session_file_name: str
) -> dict[str, Any] | None:
    """Parse a JSON line with error handling.

    Args:
        line_text: Text content of the line
        line_num: Line number for error messages
        session_file_name: Session file name for logging

    Returns:
        Parsed JSON dict or None if parsing fails
    """
    try:
        result: dict[str, Any] = json.loads(line_text)
    except json.JSONDecodeError as e:
        logger.warning(
            "Malformed JSON in %s line %d: %s", session_file_name, line_num, e
        )
        return None
    else:
        return result


def _extract_tool_call_from_block(
    content_block: dict[str, Any],
    timestamp: str,
    session_id: str,
    line_num: int,
    session_file_name: str,
) -> ToolCall | None:
    """Extract a ToolCall from a tool_use content block.

    Args:
        content_block: Content block dictionary
        timestamp: Timestamp from entry
        session_id: Session ID from entry
        line_num: Line number for error messages
        session_file_name: Session file name for logging

    Returns:
        ToolCall object or None if extraction fails
    """
    if content_block.get("type") != "tool_use":
        return None

    tool_name = content_block.get("name")
    tool_id = content_block.get("id")
    input_data = content_block.get("input", {})

    if not tool_name or not tool_id:
        logger.warning(
            "Incomplete tool_use block in %s line %d", session_file_name, line_num
        )
        return None

    try:
        return ToolCall(
            tool_name=tool_name,
            tool_id=tool_id,
            input=input_data,
            timestamp=timestamp,
            session_id=session_id,
        )
    except (ValueError, KeyError) as e:
        logger.warning(
            "Failed to create ToolCall in %s line %d: %s",
            session_file_name,
            line_num,
            e,
        )
        return None


def extract_tool_calls_from_session(session_file: Path) -> list[ToolCall]:
    """Extract all tool calls from a session JSONL file.

    Processes each line, looking for assistant entries with tool_use content blocks.
    Skips malformed entries and logs warnings for graceful degradation.

    Args:
        session_file: Path to session JSONL file

    Returns:
        List of ToolCall objects sorted by timestamp
    """
    tool_calls: list[ToolCall] = []

    try:
        with session_file.open() as f:
            for line_num, current_line in enumerate(f, 1):
                stripped_line = current_line.strip()
                if not stripped_line:
                    continue

                entry = _parse_json_line(stripped_line, line_num, session_file.name)
                if entry is None:
                    continue

                # Only process assistant entries
                if entry.get("type") != "assistant":
                    continue

                # Extract timestamp and session_id
                timestamp = entry.get("timestamp", "")
                session_id = entry.get("sessionId", "")

                # Process content array looking for tool_use blocks
                message = entry.get("message", {})
                content = message.get("content", [])
                if not isinstance(content, list):
                    continue

                for content_block in content:
                    if not isinstance(content_block, dict):
                        continue

                    tool_call = _extract_tool_call_from_block(
                        content_block,
                        timestamp,
                        session_id,
                        line_num,
                        session_file.name,
                    )
                    if tool_call:
                        tool_calls.append(tool_call)

    except OSError as e:
        logger.warning("Failed to read %s: %s", session_file, e)
        return []

    # Sort by timestamp
    tool_calls.sort(key=lambda tc: tc.timestamp)

    return tool_calls
