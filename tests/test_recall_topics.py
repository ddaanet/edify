"""Tests for session topic extraction."""

from pathlib import Path

from edify.recall.topics import extract_session_topics


def test_extract_topics_empty_session(tmp_path: Path) -> None:
    """Empty session file returns empty keyword set."""
    session_file = tmp_path / "empty.jsonl"
    session_file.write_text("")

    result = extract_session_topics(session_file)
    assert result == set()


def test_extract_topics_no_user_messages(tmp_path: Path) -> None:
    """Session with only assistant messages returns empty set."""
    session_file = tmp_path / "no_users.jsonl"
    session_file.write_text(
        '{"type":"assistant","message":{"content":"Response"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)
    assert result == set()


def test_extract_topics_trivial_messages(tmp_path: Path) -> None:
    """Trivial messages (yes, no, etc.) are filtered out."""
    session_file = tmp_path / "trivial.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"yes"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
        '{"type":"user","message":{"content":"k"},'
        '"timestamp":"2025-12-16T10:00:01.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)
    assert result == set()


def test_extract_topics_single_message(tmp_path: Path) -> None:
    """Extract keywords from single user message."""
    session_file = tmp_path / "single_msg.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Design a python script for testing"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    # Should include: design, python, script, testing
    # Should exclude: a, for (stopwords)
    assert "design" in result
    assert "python" in result
    assert "script" in result
    assert "testing" in result
    assert "a" not in result
    assert "for" not in result


def test_extract_topics_multiple_messages(tmp_path: Path) -> None:
    """Extract keywords from multiple user messages."""
    session_file = tmp_path / "multi_msg.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"First message about testing"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
        '{"type":"user","message":{"content":"Second message about refactoring"},'
        '"timestamp":"2025-12-16T10:00:01.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    assert "testing" in result
    assert "refactoring" in result


def test_extract_topics_array_content(tmp_path: Path) -> None:
    """Extract from array-format message content."""
    session_file = tmp_path / "array_content.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":[{"type":"text",'
        '"text":"Parse this JSON data"}]},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    assert "parse" in result
    assert "json" in result
    assert "data" in result


def test_extract_topics_lowercase_normalization(tmp_path: Path) -> None:
    """Keywords are normalized to lowercase."""
    session_file = tmp_path / "case_test.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Design Testing Python"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    assert "design" in result
    assert "Design" not in result
    assert "testing" in result
    assert "python" in result


def test_extract_topics_filters_noise_words(tmp_path: Path) -> None:
    """Session noise words are filtered out."""
    session_file = tmp_path / "noise.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Can you please help me with testing"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    # Should include: testing
    # Should exclude: can, please, help, with, you (stopwords/noise)
    assert "testing" in result
    assert "can" not in result
    assert "please" not in result
    assert "help" not in result


def test_extract_topics_nonexistent_file() -> None:
    """Nonexistent file returns empty set."""
    result = extract_session_topics(Path("/nonexistent/file.jsonl"))
    assert result == set()


def test_extract_topics_slash_commands(tmp_path: Path) -> None:
    """Slash commands are filtered as trivial."""
    session_file = tmp_path / "slash_cmds.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"/design"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
        '{"type":"user","message":{"content":"Implement feature"},'
        '"timestamp":"2025-12-16T10:00:01.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    # Only "Implement feature" should be processed
    assert "implement" in result
    assert "feature" in result
    # Slash command should be completely filtered out


def test_extract_topics_punctuation_tokenization(tmp_path: Path) -> None:
    """Punctuation is handled correctly in tokenization."""
    session_file = tmp_path / "punct.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Test: parsing, tokenization-logic"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}\n'
    )

    result = extract_session_topics(session_file)

    # All words should be tokenized separately
    assert "test" in result
    assert "parsing" in result
    assert "tokenization" in result
    assert "logic" in result
    # Punctuation should not appear as keywords
    assert ":" not in result
    assert "," not in result
