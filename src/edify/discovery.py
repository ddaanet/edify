"""Session and agent file discovery utilities."""

import json
import logging
import re
from pathlib import Path

from .models import FeedbackItem, SessionInfo
from .parsing import (
    extract_content_text,
    extract_feedback_from_entry,
    format_title,
)
from .paths import get_project_history_dir

logger = logging.getLogger(__name__)


def list_top_level_sessions(project_dir: str) -> list[SessionInfo]:
    """List sessions sorted by timestamp with extracted titles."""
    history_dir = get_project_history_dir(project_dir)
    sessions = []

    # UUID regex pattern
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
    )

    # List all .jsonl files in the history directory
    if not history_dir.exists():
        return []

    for file_path in history_dir.glob("*.jsonl"):
        # Filter by UUID pattern
        if not uuid_pattern.match(file_path.name):
            continue

        # Extract session_id from filename
        session_id = file_path.name.replace(".jsonl", "")

        # Read first line and parse JSON
        try:
            with file_path.open() as f:
                first_line = f.readline().strip()
                if not first_line:
                    continue
                data = json.loads(first_line)
        except (json.JSONDecodeError, OSError):
            continue

        # Extract content and format title
        message = data.get("message", {})
        content = message.get("content", "")
        title = extract_content_text(content)
        title = format_title(title)

        # Extract timestamp
        timestamp = data.get("timestamp", "")

        sessions.append(
            SessionInfo(session_id=session_id, title=title, timestamp=timestamp)
        )

    # Sort by timestamp descending (most recent first)
    sessions.sort(key=lambda s: s.timestamp, reverse=True)

    return sessions


def find_sub_agent_ids(session_file: Path) -> list[str]:
    """Extract all sub-agent IDs from a session JSONL file.

    Scans for entries with successful Task tool completions that contain
    an agentId in the toolUseResult field.

    Args:
        session_file: Path to session JSONL file

    Returns:
        List of unique agent IDs (deduplicated, in order of first occurrence)
    """
    agent_ids = []
    seen: set[str] = set()

    with session_file.open() as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Check if entry has toolUseResult as a dict (successful completion)
            tool_result = entry.get("toolUseResult")
            if isinstance(tool_result, dict) and "agentId" in tool_result:
                agent_id = tool_result["agentId"]
                if agent_id not in seen:
                    agent_ids.append(agent_id)
                    seen.add(agent_id)

    return agent_ids


def find_related_agent_files(session_id: str, project_dir: str) -> list[Path]:
    """Find all agent files related to a session.

    Scans the project history directory for all agent-*.jsonl files that
    reference the given session ID. Returns agents regardless of completion status.

    Args:
        session_id: The session ID to search for
        project_dir: The project directory path

    Returns:
        List of Path objects to matching agent files
    """
    history_dir = get_project_history_dir(project_dir)
    matching_files = []

    for agent_file in sorted(history_dir.glob("agent-*.jsonl")):
        try:
            first_line = agent_file.read_text().split("\n")[0].strip()
            if not first_line:
                continue
            entry = json.loads(first_line)
            if entry.get("sessionId") == session_id:
                matching_files.append(agent_file)
        except json.JSONDecodeError:
            logger.warning("Malformed JSON in %s", agent_file)
            continue
        except OSError:
            continue

    return matching_files


def _process_agent_file(agent_file: Path) -> tuple[list[FeedbackItem], str | None]:
    """Extract feedback and agent ID from an agent file.

    Args:
        agent_file: Path to agent JSONL file

    Returns:
        Tuple of (feedback items, agent ID)
    """
    feedback: list[FeedbackItem] = []
    agent_id: str | None = None

    for line in agent_file.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            entry = json.loads(line)
            # Track agent ID from first entry
            if agent_id is None:
                agent_id = entry.get("agentId")
            # Extract feedback from agent file
            result = extract_feedback_from_entry(entry)
            if result:
                feedback.append(result)
        except json.JSONDecodeError:
            continue

    return feedback, agent_id
