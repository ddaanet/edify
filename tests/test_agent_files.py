"""Tests for agent file discovery."""

import logging
from pathlib import Path

import pytest

from edify.discovery import find_related_agent_files

# temp_project_dir fixture is provided by conftest.py


def test_find_agents_empty_directory(temp_project_dir: tuple[Path, Path]) -> None:
    """Empty directory returns empty list."""
    project, _history_dir = temp_project_dir
    result = find_related_agent_files("main-123", str(project))
    assert result == []


def test_find_agents_no_matching_session(temp_project_dir: tuple[Path, Path]) -> None:
    """No matching session returns empty list."""
    project, history_dir = temp_project_dir
    (history_dir / "agent-a1.jsonl").write_text(
        '{"type":"user","sessionId":"other-456","agentId":"a1",'
        '"message":{"content":"test"},"timestamp":"2025-12-16T10:00:00.000Z"}\n'
    )

    result = find_related_agent_files("main-123", str(project))
    assert result == []


def test_find_agents_single_match(temp_project_dir: tuple[Path, Path]) -> None:
    """Single matching agent file returns list with Path."""
    project, history_dir = temp_project_dir
    agent_file = history_dir / "agent-a1.jsonl"
    agent_file.write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a1",'
        '"message":{"content":"test"},"timestamp":"2025-12-16T10:00:00.000Z"}\n'
    )

    result = find_related_agent_files("main-123", str(project))
    assert result == [agent_file]


def test_find_agents_multiple_matches_filters_correctly(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Multiple agent files returns only matching ones."""
    project, history_dir = temp_project_dir
    agent_a1 = history_dir / "agent-a1.jsonl"
    agent_a1.write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a1",'
        '"message":{"content":"test"},"timestamp":"2025-12-16T10:00:00.000Z"}\n'
    )
    agent_a2 = history_dir / "agent-a2.jsonl"
    agent_a2.write_text(
        '{"type":"user","sessionId":"other-456","agentId":"a2",'
        '"message":{"content":"test"},"timestamp":"2025-12-16T10:05:00.000Z"}\n'
    )
    agent_a3 = history_dir / "agent-a3.jsonl"
    agent_a3.write_text(
        '{"type":"user","sessionId":"main-123","agentId":"a3",'
        '"message":{"content":"test"},"timestamp":"2025-12-16T10:10:00.000Z"}\n'
    )

    result = find_related_agent_files("main-123", str(project))
    assert result == [agent_a1, agent_a3]


def test_find_agents_empty_file(temp_project_dir: tuple[Path, Path]) -> None:
    """Empty file is skipped gracefully."""
    project, history_dir = temp_project_dir
    (history_dir / "agent-a1.jsonl").write_text("")

    result = find_related_agent_files("main-123", str(project))
    assert result == []


def test_find_agents_malformed_json(
    temp_project_dir: tuple[Path, Path], caplog: pytest.LogCaptureFixture
) -> None:
    """Malformed JSON is skipped with warning logged."""
    project, history_dir = temp_project_dir
    (history_dir / "agent-a1.jsonl").write_text("{invalid json")

    with caplog.at_level(logging.WARNING):
        result = find_related_agent_files("main-123", str(project))

    assert result == []
    assert any("malformed" in record.message.lower() for record in caplog.records)


def test_find_agents_missing_session_id_field(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Agent file missing sessionId field is skipped."""
    project, history_dir = temp_project_dir
    (history_dir / "agent-a1.jsonl").write_text(
        '{"type":"user","agentId":"a1",'
        '"message":{"content":"test"},"timestamp":"2025-12-16T10:00:00.000Z"}\n'
    )

    result = find_related_agent_files("main-123", str(project))
    assert result == []
