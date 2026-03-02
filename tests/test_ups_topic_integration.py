"""Integration tests for topic injection into UserPromptSubmit hook."""

from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from tests.ups_hook_helpers import call_hook


@pytest.fixture
def tmp_memory_index(tmp_path: Path) -> Path:
    """Create memory-index with fixture entries pointing to decision file."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Create decision file with test sections
    decision_file = agents_dir / "test-decisions.md"
    decision_file.write_text("""
# Test Decisions

## When testing hook integration

This is test decision content for hook integration testing. It contains detailed
information about how the hook should work with the topic detector.

## When recall system works

Details about how the recall system works and its components. This section has
specific implementation notes.
""")

    # Create memory-index referencing the decision file
    index_file = agents_dir / "memory-index.md"
    index_file.write_text("""
## agents/test-decisions.md

testing hook integration — decision about hook testing
recall system works — how recall system integrates
""")

    return index_file


def test_hook_topic_injection_end_to_end(
    tmp_path: Path, monkeypatch: MonkeyPatch, tmp_memory_index: Path
) -> None:
    """End-to-end: prompt with keywords match additionalContext with decision."""
    # Setup
    tmp_dir = tmp_memory_index.parent.parent
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_dir))

    # Create tmp directory for cache
    tmp_cache_dir = tmp_dir / "tmp"
    tmp_cache_dir.mkdir(exist_ok=True)

    # Call hook with prompt containing keywords that match memory-index entries
    prompt = "testing hook integration"
    result = call_hook(prompt)

    # Assertions
    assert result != {}, "Hook should produce output for matching keywords"
    assert "hookSpecificOutput" in result
    assert "additionalContext" in result["hookSpecificOutput"]

    additional_context = result["hookSpecificOutput"]["additionalContext"]

    # Should contain resolved decision content
    assert "test decision content" in additional_context

    # systemMessage should contain topic marker
    assert "systemMessage" in result
    system_message = result["systemMessage"]
    assert "topic" in system_message.lower()


def test_topic_injection_additive_with_commands(
    tmp_path: Path, monkeypatch: MonkeyPatch, tmp_memory_index: Path
) -> None:
    """Topic injection works additively with command expansion.

    Both features fire independently and contribute to output:
    - Command "s" expands to status instructions in additionalContext
    - Topic keywords match memory-index entries, resolve to decision content
    - Both features visible in systemMessage (joined by " | ")
    """
    # Setup
    tmp_dir = tmp_memory_index.parent.parent
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_dir))

    # Create tmp directory for cache
    tmp_cache_dir = tmp_dir / "tmp"
    tmp_cache_dir.mkdir(exist_ok=True)

    # Call hook with prompt: command "s" + topic keywords on separate lines
    # Command "s" triggers status expansion
    # Keywords "recall" matches memory-index entry "recall system works"
    prompt = "s\nhow does recall work"
    result = call_hook(prompt)

    # Verify output structure
    assert result != {}, "Hook should produce output with command + topic"
    assert "hookSpecificOutput" in result
    assert "additionalContext" in result["hookSpecificOutput"]

    additional_context = result["hookSpecificOutput"]["additionalContext"]

    # additionalContext should contain BOTH features:
    # 1. Command expansion: "s" command text (contains "status" or "#status")
    # 2. Topic decision: resolved section body (contains "recall system")
    assert "[#status]" in additional_context or "#status" in additional_context, (
        "additionalContext missing command expansion"
    )
    assert (
        "recall system" in additional_context.lower()
        or "implementation" in additional_context.lower()
    ), "additionalContext missing topic decision content"

    # systemMessage should show both features are active
    # Both should be joined by "|" separator
    assert "systemMessage" in result
    system_message = result["systemMessage"]
    assert " | " in system_message, (
        "systemMessage missing separator — features not both present"
    )
    # Verify both features visible
    assert "status" in system_message.lower() or "s" in system_message.lower(), (
        "systemMessage missing command indicator"
    )
    assert "topic" in system_message.lower() or "recall" in system_message.lower(), (
        "systemMessage missing topic indicator"
    )


def test_topic_injection_silent_on_no_match(
    tmp_path: Path, monkeypatch: MonkeyPatch, tmp_memory_index: Path
) -> None:
    """Hook passes through silently when no keywords match memory-index.

    Verifies no-match case: prompt with unrelated keywords produces no topic output.
    Hook returns empty dict or output without topic content.
    """
    tmp_dir = tmp_memory_index.parent.parent
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_dir))

    tmp_cache_dir = tmp_dir / "tmp"
    tmp_cache_dir.mkdir(exist_ok=True)

    result = call_hook("hello world")

    # No topic content in additionalContext
    additional_context = result.get("hookSpecificOutput", {}).get(
        "additionalContext", ""
    )
    assert "topic" not in additional_context.lower(), (
        "additionalContext should not contain topic content on no-match"
    )

    # No topic marker in systemMessage
    system_message = result.get("systemMessage", "")
    assert "topic" not in system_message.lower(), (
        "systemMessage should not mention topic on no-match"
    )
