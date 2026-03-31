"""Recursive feedback extraction from sessions and agents."""

from .discovery import _process_agent_file, find_related_agent_files
from .models import FeedbackItem
from .parsing import _extract_feedback_from_file
from .paths import get_project_history_dir


def extract_feedback_recursively(
    session_id: str, project_dir: str
) -> list[FeedbackItem]:
    """Extract feedback from a session and all sub-agent sessions.

    Recursively extracts feedback from the given session and all agents
    spawned from that session, building a complete tree of feedback.

    Args:
        session_id: The session ID to extract from
        project_dir: The project directory path

    Returns:
        List of FeedbackItem objects sorted by timestamp

    Raises:
        FileNotFoundError: If the history directory does not exist
    """
    history_dir = get_project_history_dir(project_dir)
    if not history_dir.exists():
        msg = f"History directory not found: {history_dir}"
        raise FileNotFoundError(msg)

    feedback: list[FeedbackItem] = []

    # Extract from main session file
    session_file = history_dir / f"{session_id}.jsonl"
    if session_file.exists():
        feedback.extend(_extract_feedback_from_file(session_file))

    # Find and recursively process related agent files
    agent_files = find_related_agent_files(session_id, project_dir)
    for agent_file in agent_files:
        agent_feedback, agent_id = _process_agent_file(agent_file)
        feedback.extend(agent_feedback)

        # Recursively process agents spawned by this agent
        if agent_id:
            feedback.extend(extract_feedback_recursively(agent_id, project_dir))

    return sorted(feedback, key=lambda x: x.timestamp)
