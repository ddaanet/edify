"""Tests for tool call extraction from JSONL."""

from pathlib import Path

from edify.recall.tool_calls import ToolCall, extract_tool_calls_from_session


def test_extract_tool_calls_empty_file(tmp_path: Path) -> None:
    """Empty JSONL file returns empty list."""
    session_file = tmp_path / "empty.jsonl"
    session_file.write_text("")

    result = extract_tool_calls_from_session(session_file)
    assert result == []


def test_extract_tool_calls_no_assistant_entries(tmp_path: Path) -> None:
    """File with only user entries returns empty list."""
    session_file = tmp_path / "users_only.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Hello"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_tool_calls_from_session(session_file)
    assert result == []


def test_extract_tool_calls_single_read(tmp_path: Path) -> None:
    """Extract single Read tool call."""
    session_file = tmp_path / "single_read.jsonl"
    session_file.write_text(
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"toolu_01abc","name":"Read","input":{"file_path":"/path/to/file.md"}}]},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_tool_calls_from_session(session_file)
    assert len(result) == 1
    assert result[0].tool_name == "Read"
    assert result[0].tool_id == "toolu_01abc"
    assert result[0].input["file_path"] == "/path/to/file.md"
    assert result[0].session_id == "main-123"


def test_extract_tool_calls_multiple_tools_per_entry(tmp_path: Path) -> None:
    """Extract multiple tool calls from single assistant entry."""
    session_file = tmp_path / "multi_tools.jsonl"
    session_file.write_text(
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"toolu_01","name":"Grep","input":{"path":"/path"}},{"type":"tool_use",'
        '"id":"toolu_02","name":"Read","input":{"file_path":"/file.md"}}]},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_tool_calls_from_session(session_file)
    assert len(result) == 2
    assert result[0].tool_name == "Grep"
    assert result[1].tool_name == "Read"


def test_extract_tool_calls_sorted_by_timestamp(tmp_path: Path) -> None:
    """Tool calls are sorted by timestamp."""
    session_file = tmp_path / "sorted.jsonl"
    session_file.write_text(
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"toolu_02","name":"Read","input":{"file_path":"/b.md"}}]},'
        '"timestamp":"2025-12-16T10:00:05.000Z","sessionId":"main-123"}\n'
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"toolu_01","name":"Read","input":{"file_path":"/a.md"}}]},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_tool_calls_from_session(session_file)
    assert result[0].tool_id == "toolu_01"
    assert result[1].tool_id == "toolu_02"


def test_extract_tool_calls_malformed_json(tmp_path: Path) -> None:
    """Malformed JSON is skipped with warning."""
    session_file = tmp_path / "malformed.jsonl"
    session_file.write_text(
        "not valid json\n"
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"toolu_01","name":"Read","input":{"file_path":"/good.md"}}]},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_tool_calls_from_session(session_file)
    assert len(result) == 1
    assert result[0].tool_name == "Read"


def test_extract_tool_calls_different_tools(tmp_path: Path) -> None:
    """Extract different tool types."""
    session_file = tmp_path / "different_tools.jsonl"
    session_file.write_text(
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"read_1","name":"Read","input":{"file_path":"/file.md"}},{"type":"tool_use",'
        '"id":"grep_1","name":"Grep","input":{"path":"/dir"}},{"type":"tool_use",'
        '"id":"glob_1","name":"Glob","input":{"path":"**/*.py"}},{"type":"tool_use",'
        '"id":"write_1","name":"Write","input":{"file_path":"/new.txt"}}]},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_tool_calls_from_session(session_file)
    assert len(result) == 4
    tool_names = {tc.tool_name for tc in result}
    assert tool_names == {"Read", "Grep", "Glob", "Write"}


def test_extract_tool_calls_nonexistent_file() -> None:
    """Nonexistent file returns empty list."""
    result = extract_tool_calls_from_session(Path("/nonexistent/file.jsonl"))
    assert result == []


def test_tool_call_model_validation() -> None:
    """ToolCall model validates fields."""
    tool_call = ToolCall(
        tool_name="Read",
        tool_id="toolu_01abc",
        input={"file_path": "/path/to/file"},
        timestamp="2025-12-16T10:00:00.000Z",
        session_id="main-123",
    )

    assert tool_call.tool_name == "Read"
    assert tool_call.tool_id == "toolu_01abc"
    assert tool_call.session_id == "main-123"
