"""Tests for statusline CLI model-specific formatting."""

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


def test_cli_dirty_git_status() -> None:
    """Test that dirty git status shows yellow emoji in line 1."""
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Opus 4"),
        workspace=WorkspaceInfo(current_dir="/Users/david/code/edify"),
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
        cost=CostInfo(total_cost_usd=1.23),
        version="1.0.0",
        session_id="test-session-127",
    )

    runner = CliRunner()

    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="feature/test", dirty=True)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=input_data.model_dump_json())

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        assert "🟡" in line1, "Line 1 should show yellow dot for dirty git"
        assert "feature/test" in line1, "Line 1 should contain branch name"


def test_cli_sonnet_model() -> None:
    """Test that Sonnet model displays silver medal emoji."""
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Sonnet 3.5"),
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
        cost=CostInfo(total_cost_usd=0.50),
        version="1.0.0",
        session_id="test-session-128",
    )

    runner = CliRunner()

    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=input_data.model_dump_json())

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        assert "🥈" in line1, "Line 1 should show silver medal for Sonnet"
        assert "Sonnet" in line1, "Line 1 should contain 'Sonnet'"


def test_cli_haiku_model() -> None:
    """Test that Haiku model displays bronze medal emoji."""
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Haiku 3"),
        workspace=WorkspaceInfo(current_dir="/Users/david/tmp"),
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
        cost=CostInfo(total_cost_usd=0.01),
        version="1.0.0",
        session_id="test-session-129",
    )

    runner = CliRunner()

    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=input_data.model_dump_json())

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        assert "🥉" in line1, "Line 1 should show bronze medal for Haiku"
        assert "Haiku" in line1, "Line 1 should contain 'Haiku'"


def test_cli_unknown_model() -> None:
    """Test that unknown model displays full name without emoji."""
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Unknown-Model-123"),
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
        session_id="test-session-130",
    )

    runner = CliRunner()

    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=input_data.model_dump_json())

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        assert "Unknown-Model-123" in line1, "Should display unknown model name"
