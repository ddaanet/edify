"""Tests for statusline CLI command."""

from unittest.mock import patch

from click.testing import CliRunner

from edify.statusline.cli import statusline
from edify.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    GitStatus,
    ModelInfo,
    StatuslineInput,
    ThinkingState,
    WorkspaceInfo,
)


def test_statusline_parses_json() -> None:
    """Test that statusline CLI parses JSON stdin into StatuslineInput model."""
    # Build valid StatuslineInput JSON
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    result = runner.invoke(statusline, input=json_str)

    # Should parse without error (exit code 0)
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    # Should complete without raising a validation exception
    assert result.exception is None, f"JSON parsing failed: {result.exception}"


def test_statusline_calls_context_functions() -> None:
    """Test that statusline() calls all three context functions."""
    # Build valid StatuslineInput JSON
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
    ):
        result = runner.invoke(statusline, input=json_str)

        # All three functions should be called
        assert mock_git.called, "get_git_status() was not called"
        assert mock_thinking.called, "get_thinking_state() was not called"
        assert mock_context.called, "calculate_context_tokens() was not called"
        # Should exit successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"


def test_statusline_routes_to_plan_usage() -> None:
    """Test statusline() calls get_account_state and routes to plan_usage.

    When mode=plan, get_plan_usage() should be called and get_api_usage() should
    not be called.
    """
    # Build valid StatuslineInput JSON
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    with (
        patch("edify.statusline.cli.get_git_status"),
        patch("edify.statusline.cli.get_thinking_state"),
        patch("edify.statusline.cli.calculate_context_tokens"),
        patch("edify.statusline.cli.get_account_state") as mock_state,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
        patch("edify.statusline.cli.get_api_usage") as mock_api,
    ):
        # Mock get_account_state to return mode="plan"
        mock_state.return_value.mode = "plan"

        result = runner.invoke(statusline, input=json_str)

        # Verify get_plan_usage was called
        assert mock_plan.called, "get_plan_usage() was not called"
        # Verify get_api_usage was NOT called
        assert not mock_api.called, (
            "get_api_usage() should not be called when mode=plan"
        )
        # Should exit successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"


def test_statusline_outputs_two_lines() -> None:
    """Test that statusline() formats and outputs two lines with real data."""
    # Build valid StatuslineInput JSON with all required fields
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        # Provide proper mock return values
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        # Should exit successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        # Output should contain two lines
        lines = result.output.strip().split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}: {lines}"
        # Each line should have content (not empty)
        assert lines[0].strip(), "Line 1 is empty"
        assert lines[1].strip(), "Line 2 is empty"


def test_statusline_exits_zero_on_error() -> None:
    """Test that statusline CLI exits with code 0 even when an exception occurs.

    Mocks one of the data functions to raise an exception and verifies:
    1. CLI exits with code 0 (not 1)
    2. Error message is logged to stderr
    """
    # Build valid StatuslineInput JSON
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code"),
        transcript_path="/path/to/transcript.md",
        context_window=ContextWindowInfo(
            current_usage=ContextUsage(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
            context_window_size=200000,
        ),
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="test-session-123",
    )

    json_str = input_data.model_dump_json()

    runner = CliRunner()
    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state"),
        patch("edify.statusline.cli.calculate_context_tokens"),
        patch("edify.statusline.cli.get_account_state"),
        patch("edify.statusline.cli.get_plan_usage"),
    ):
        # Mock get_git_status to raise an exception
        mock_git.side_effect = Exception("Test error: git command failed")

        result = runner.invoke(statusline, input=json_str)

        # Must exit with code 0 (not 1)
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"
        )
        # Error message must be in output (stderr via click.echo(err=True))
        assert "Error:" in result.output, (
            f"Error message should be present in output. Output: '{result.output}'"
        )
