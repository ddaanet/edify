"""Tests for session and agent file discovery."""

import json
import tempfile
from pathlib import Path

from edify.discovery import find_sub_agent_ids, list_top_level_sessions

# temp_project_dir fixture is provided by conftest.py


def test_list_sessions_basic_discovery(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Discover all UUID-named session files."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"First"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "a1b2c3d4-1234-5678-9abc-def012345678.jsonl").write_text(
        '{"type":"user","message":{"content":"Second"},"timestamp":"2025-12-16T11:00:00.000Z","sessionId":"a1b2c3d4-1234-5678-9abc-def012345678"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions) == 2


def test_list_sessions_filters_agents(temp_project_dir: tuple[Path, Path]) -> None:
    """Exclude agent-*.jsonl files."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Main"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "agent-a6755ed.jsonl").write_text(
        '{"type":"user","message":{"content":"Agent"},"timestamp":"2025-12-16T10:05:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions) == 1
    assert sessions[0].session_id == "e12d203f-ca65-44f0-9976-cb10b74514c1"


def test_list_sessions_sorted_by_timestamp(temp_project_dir: tuple[Path, Path]) -> None:
    """Show most recent session first."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Middle"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "a1b2c3d4-1234-5678-9abc-def012345678.jsonl").write_text(
        '{"type":"user","message":{"content":"Latest"},"timestamp":"2025-12-16T12:00:00.000Z","sessionId":"a1b2c3d4-1234-5678-9abc-def012345678"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Latest"
    assert sessions[1].title == "Middle"


def test_list_sessions_extracts_title_from_string_content(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Handle content as string."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Design a python script"},'
        '"timestamp":"2025-12-16T10:00:00.000Z",'
        '"sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Design a python script"


def test_list_sessions_extracts_title_from_array_content(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Handle content as array with text blocks."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":[{"type":"text",'
        '"text":"Help me with this"}]},"timestamp":"2025-12-16T10:00:00.000Z",'
        '"sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Help me with this"


def test_list_sessions_truncates_long_titles(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Truncate titles longer than 80 chars with ..."""
    project, history_dir = temp_project_dir

    long_text = "A" * 100
    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        f'{{"type":"user","message":{{"content":"{long_text}"}},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions[0].title) == 80
    assert sessions[0].title == ("A" * 77 + "...")


def test_list_sessions_handles_newlines_in_title(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Replace newlines with spaces in multi-line messages."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Line one\\nLine two"},'
        '"timestamp":"2025-12-16T10:00:00.000Z",'
        '"sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Line one Line two"


def test_find_sub_agent_ids_successful_tasks() -> None:
    """Extract agent IDs from successful Task tool completions."""
    entries = [
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ae9906a",
                "content": [],
                "totalDurationMs": 5000,
            },
            "timestamp": "2025-12-16T08:47:19.855Z",
            "sessionId": "main-session-id",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": "Agent completed",
                        "tool_use_id": "toolu_abc123",
                    }
                ],
            },
        },
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ad67fd8",
                "content": [],
                "totalDurationMs": 3000,
            },
            "timestamp": "2025-12-16T08:48:00.000Z",
            "sessionId": "main-session-id",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": "Agent completed",
                        "tool_use_id": "toolu_xyz789",
                    }
                ],
            },
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == ["ae9906a", "ad67fd8"]


def test_find_sub_agent_ids_no_tasks() -> None:
    """Session with no Task calls returns empty list."""
    entries = [
        {
            "type": "user",
            "message": {"role": "user", "content": "Design a script"},
            "timestamp": "2025-12-16T08:39:26.932Z",
            "sessionId": "main-session-id",
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": "I'll help you design a script",
            },
            "timestamp": "2025-12-16T08:39:27.000Z",
            "sessionId": "main-session-id",
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == []


def test_find_sub_agent_ids_duplicates_deduplicated() -> None:
    """Duplicate agent IDs are deduplicated."""
    entries = [
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ae9906a",
                "content": [],
                "totalDurationMs": 5000,
            },
            "timestamp": "2025-12-16T08:47:19.855Z",
            "sessionId": "main-session-id",
            "message": {"role": "user", "content": []},
        },
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ae9906a",
                "content": [],
                "totalDurationMs": 3000,
            },
            "timestamp": "2025-12-16T08:48:00.000Z",
            "sessionId": "main-session-id",
            "message": {"role": "user", "content": []},
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == ["ae9906a"]


def test_find_sub_agent_ids_interrupted_task_ignored() -> None:
    """Interrupted Task (string toolUseResult) is ignored."""
    entries = [
        {
            "type": "user",
            "toolUseResult": "Error: [Request interrupted by user for tool use]",
            "timestamp": "2025-12-16T08:43:43.872Z",
            "sessionId": "main-session-id",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": "[Request interrupted by user for tool use]",
                        "is_error": True,
                        "tool_use_id": "toolu_xyz789",
                    }
                ],
            },
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == []
