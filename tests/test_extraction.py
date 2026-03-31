"""Tests for recursive feedback extraction."""

from pathlib import Path

import pytest

from edify.extraction import extract_feedback_recursively

# temp_history_dir fixture is provided by conftest.py


def test_extract_recursive_missing_project_directory() -> None:
    """Missing project directory raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        extract_feedback_recursively("main-123", "/nonexistent/path")


def test_extract_recursive_no_messages_no_agents(
    temp_history_dir: tuple[Path, Path],
) -> None:
    """Session with only assistant messages and no agents returns empty list."""
    project, history_dir = temp_history_dir
    # Create session file with only assistant messages
    (history_dir / "main-123.jsonl").write_text(
        '{"type":"assistant","message":{"content":"Hello"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_feedback_recursively("main-123", str(project))
    assert result == []


def test_extract_recursive_top_level_only(
    temp_history_dir: tuple[Path, Path],
) -> None:
    """Session with user messages and no agents returns feedback items."""
    project, history_dir = temp_history_dir
    # Create session file with 2 user messages
    (history_dir / "main-123.jsonl").write_text(
        '{"type":"user","message":{"content":"First message"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
        '{"type":"user","message":{"content":"Second message"},'
        '"timestamp":"2025-12-16T11:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_feedback_recursively("main-123", str(project))
    assert len(result) == 2
    assert result[0].content == "First message"
    assert result[1].content == "Second message"
    assert result[0].timestamp == "2025-12-16T10:00:00.000Z"
    assert result[1].timestamp == "2025-12-16T11:00:00.000Z"


def test_extract_recursive_one_level_of_agents(
    temp_history_dir: tuple[Path, Path],
) -> None:
    """Extract feedback from main session and one agent."""
    project, history_dir = temp_history_dir
    # Create main session with 1 user message
    (history_dir / "main-123.jsonl").write_text(
        '{"type":"user","message":{"content":"Main message"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )
    # Create agent file with 1 user message
    (history_dir / "agent-a1.jsonl").write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a1",'
        '"message":{"content":"Agent message"},'
        '"timestamp":"2025-12-16T10:05:00.000Z"}\n'
    )

    result = extract_feedback_recursively("main-123", str(project))
    assert len(result) == 2
    assert result[0].content == "Main message"
    assert result[1].content == "Agent message"


def test_extract_recursive_multiple_agents_same_level(
    temp_history_dir: tuple[Path, Path],
) -> None:
    """Extract feedback from main session and multiple agents."""
    project, history_dir = temp_history_dir
    # Create main session with 1 user message
    (history_dir / "main-123.jsonl").write_text(
        '{"type":"user","message":{"content":"Main message"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )
    # Create 2 agent files
    (history_dir / "agent-a1.jsonl").write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a1",'
        '"message":{"content":"Agent 1 message"},'
        '"timestamp":"2025-12-16T10:05:00.000Z"}\n'
    )
    (history_dir / "agent-a2.jsonl").write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a2",'
        '"message":{"content":"Agent 2 message"},'
        '"timestamp":"2025-12-16T10:10:00.000Z"}\n'
    )

    result = extract_feedback_recursively("main-123", str(project))
    assert len(result) == 3
    assert result[0].content == "Main message"
    assert result[1].content == "Agent 1 message"
    assert result[2].content == "Agent 2 message"


def test_extract_recursive_nested_agents(
    temp_history_dir: tuple[Path, Path],
) -> None:
    """Extract feedback with nested agent hierarchy."""
    project, history_dir = temp_history_dir
    # Create main session with 1 user message
    (history_dir / "main-123.jsonl").write_text(
        '{"type":"user","message":{"content":"Main message"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )
    # Create agent a1 with sessionId=main-123
    (history_dir / "agent-a1.jsonl").write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a1",'
        '"message":{"content":"Agent 1 message"},'
        '"timestamp":"2025-12-16T10:05:00.000Z"}\n'
    )
    # Create agent a2 with sessionId=a1 (nested!)
    (history_dir / "agent-a2.jsonl").write_text(
        '{"type":"user","sessionId":"a1","agentId":"a2",'
        '"message":{"content":"Agent 2 message"},'
        '"timestamp":"2025-12-16T10:10:00.000Z"}\n'
    )

    result = extract_feedback_recursively("main-123", str(project))
    assert len(result) == 3
    assert result[0].content == "Main message"
    assert result[1].content == "Agent 1 message"
    assert result[2].content == "Agent 2 message"
