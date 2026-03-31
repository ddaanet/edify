"""Tests for StatuslineInput model - Claude Code JSON schema parsing."""

from typing import Any

from edify.statusline.models import ContextUsage, StatuslineInput


def test_parse_valid_json() -> None:
    """StatuslineInput parses valid Claude Code JSON into model with 8 fields.

    Validates that the Pydantic model correctly parses Claude Code stdin JSON
    with all required fields: model.display_name, workspace.current_dir,
    transcript_path, context_window.current_usage, context_window.context_window_size,
    cost.total_cost_usd, version, session_id.
    """
    json_data: dict[str, Any] = {
        "model": {"display_name": "Claude 3.5 Sonnet"},
        "workspace": {"current_dir": "/Users/david/code/edify"},
        "transcript_path": "/Users/david/.claude/sessions/session-123/transcript.json",
        "context_window": {
            "current_usage": {
                "input_tokens": 1500,
                "output_tokens": 500,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
            "context_window_size": 200000,
        },
        "cost": {"total_cost_usd": 0.12},
        "version": "2026-01-15",
        "session_id": "session-abc123",
    }

    # Parse JSON into model
    input_model = StatuslineInput(**json_data)

    # Verify all 8 fields are present and correct
    assert input_model.model.display_name == "Claude 3.5 Sonnet"
    assert input_model.workspace.current_dir == "/Users/david/code/edify"
    assert (
        input_model.transcript_path
        == "/Users/david/.claude/sessions/session-123/transcript.json"
    )
    assert input_model.context_window.current_usage is not None
    assert input_model.context_window.current_usage.input_tokens == 1500
    assert input_model.context_window.current_usage.output_tokens == 500
    assert input_model.context_window.current_usage.cache_creation_input_tokens == 0
    assert input_model.context_window.current_usage.cache_read_input_tokens == 0
    assert input_model.context_window.context_window_size == 200000
    assert input_model.cost.total_cost_usd == 0.12
    assert input_model.version == "2026-01-15"
    assert input_model.session_id == "session-abc123"


def test_parse_null_current_usage() -> None:
    """StatuslineInput parses JSON with current_usage=null without error.

    Validates that current_usage field is optional and accepts null values,
    supporting resume session case where usage data may not be available (per
    R2).
    """
    json_data: dict[str, Any] = {
        "model": {"display_name": "Claude 3.5 Sonnet"},
        "workspace": {"current_dir": "/Users/david/code/edify"},
        "transcript_path": "/Users/david/.claude/sessions/session-123/transcript.json",
        "context_window": {
            "current_usage": None,
            "context_window_size": 200000,
        },
        "cost": {"total_cost_usd": 0.12},
        "version": "2026-01-15",
        "session_id": "session-abc123",
    }

    # Parse JSON with null current_usage
    input_model = StatuslineInput(**json_data)

    # Verify model parses and current_usage is None
    assert input_model.context_window.current_usage is None
    assert input_model.context_window.context_window_size == 200000


def test_context_usage_has_four_token_fields() -> None:
    """ContextUsage has 4 token fields and can sum them correctly.

    Validates that ContextUsage model has all 4 token fields:
    input_tokens, output_tokens, cache_creation_input_tokens,
    cache_read_input_tokens. Confirms all fields are present and accessible,
    supporting token accounting (per R2).
    """
    usage_data: dict[str, Any] = {
        "input_tokens": 1000,
        "output_tokens": 500,
        "cache_creation_input_tokens": 200,
        "cache_read_input_tokens": 300,
    }

    # Instantiate ContextUsage to verify all fields exist
    usage = ContextUsage(**usage_data)

    # Verify all 4 token fields are present and accessible
    assert usage.input_tokens == 1000
    assert usage.output_tokens == 500
    assert usage.cache_creation_input_tokens == 200
    assert usage.cache_read_input_tokens == 300

    # Verify fields can be summed (total token accounting)
    total_tokens = (
        usage.input_tokens
        + usage.output_tokens
        + usage.cache_creation_input_tokens
        + usage.cache_read_input_tokens
    )
    assert total_tokens == 2000
