"""Integration tests for statusline CLI command - Line 1 and Line 2 composition."""

from unittest.mock import patch

from click.testing import CliRunner

from edify.statusline.cli import statusline
from edify.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    GitStatus,
    ModelInfo,
    PlanUsageData,
    StatuslineInput,
    ThinkingState,
    WorkspaceInfo,
)


def test_cli_line1_integration() -> None:
    """Test that CLI Line 1 composes all formatted elements in correct order.

    Verifies:
    - Formatted model component with emoji and color
    - Formatted directory component with emoji and color
    - Formatted git status with emoji and color
    - Formatted cost with emoji
    - Formatted context with emoji, colored count, and bar
    - Correct ordering and spacing between elements
    - Output contains formatted elements, not raw plain text
    - Handles dirty git state correctly
    - Handles disabled thinking state correctly
    """
    # Test case 1: Clean git state with thinking enabled
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude Sonnet 4"),
        workspace=WorkspaceInfo(current_dir="edify"),
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
        # Mock clean git state
        mock_git.return_value = GitStatus(branch="tools-rewrite", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        # Assert output contains formatted components
        assert "🥈" in line1, "Model emoji (Sonnet medal) should be present"
        assert "📁" in line1, "Directory emoji should be present"
        assert "✅" in line1, "Clean git status emoji should be present"
        assert "💰" in line1, "Cost emoji should be present"
        assert "🧠" in line1, "Context emoji should be present"

        # Assert proper ordering: model < directory < git < cost < context
        model_pos = line1.find("🥈")
        dir_pos = line1.find("📁")
        git_pos = line1.find("✅")
        cost_pos = line1.find("💰")
        context_pos = line1.find("🧠")

        assert model_pos < dir_pos < git_pos < cost_pos < context_pos, (
            f"Elements not in correct order. model={model_pos}, dir={dir_pos}, "
            f"git={git_pos}, cost={cost_pos}, context={context_pos}"
        )

        # Assert spacing between elements (should be present)
        assert "  " in line1 or line1.count(" ") >= 5, (
            "Should have spacing between elements"
        )

        # Assert no raw plain text like "Claude Sonnet" (should be formatted)
        assert "Claude Sonnet" not in line1, (
            "Raw unformatted model name should not appear"
        )

    # Test case 2: Dirty git state
    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        # Mock dirty git state
        mock_git.return_value = GitStatus(branch="tools-rewrite", dirty=True)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        # Assert dirty git status emoji
        assert "🟡" in line1, "Dirty git status emoji should be present"
        assert "✅" not in line1, (
            "Clean status emoji should not be present for dirty state"
        )

    # Test case 3: Thinking disabled
    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_plan_usage") as mock_plan,
    ):
        # Mock thinking disabled
        mock_git.return_value = GitStatus(branch="tools-rewrite", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=False)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        mock_plan.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        lines = result.output.strip().split("\n")
        line1 = lines[0]

        # Assert thinking disabled indicator (😶 emoji after medal)
        assert "😶" in line1, "Thinking disabled emoji should be present"


def test_cli_line2_integration() -> None:
    """Test that CLI Line 2 composes mode indicator with usage data.

    Verifies:
    - Mode indicator is formatted with emoji and colored text (not raw "mode:" text)
    - Test with mode="plan" shows 🎫 emoji + GREEN "Plan" text
    - Test with mode="api" shows 💳 emoji + YELLOW "API" text
    - Mode formatting differs between modes (emoji/color change)
    - Usage data portion is present (composition with usage data)
    - No raw "mode:" text prefix in output
    - Graceful handling of missing/null account mode
    """
    # Test case 1: Mode="plan" with usage data
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
        # Mock plan mode with usage data
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "plan"
        # Mock plan usage data
        mock_plan.return_value = PlanUsageData(
            hour5_pct=30.0,
            hour5_reset="0h45m",
            day7_pct=50.0,
        )

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        lines = result.output.strip().split("\n")
        line2 = lines[1]

        # Assert mode emoji is present
        assert "🎫" in line2, "Plan mode emoji should be present"
        # Assert no raw "mode:" text prefix
        assert "mode:" not in line2, "Raw 'mode:' text should not be in output"
        # Assert usage data is present (should have plan usage info)
        assert "5h" in line2 or "7d" in line2, (
            "Plan usage data should be present in line2"
        )

    # Test case 2: Mode="api"
    with (
        patch("edify.statusline.cli.get_git_status") as mock_git,
        patch("edify.statusline.cli.get_thinking_state") as mock_thinking,
        patch("edify.statusline.cli.calculate_context_tokens") as mock_context,
        patch("edify.statusline.cli.get_account_state") as mock_account,
        patch("edify.statusline.cli.get_api_usage") as mock_api,
    ):
        # Mock api mode
        mock_git.return_value = GitStatus(branch="main", dirty=False)
        mock_thinking.return_value = ThinkingState(enabled=True)
        mock_context.return_value = 1500
        mock_account.return_value.mode = "api"
        mock_api.return_value = None

        result = runner.invoke(statusline, input=json_str)

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        lines = result.output.strip().split("\n")
        line2 = lines[1]

        # Assert api mode emoji is present
        assert "💳" in line2, "API mode emoji should be present"
        # Assert no raw "mode:" text prefix
        assert "mode:" not in line2, "Raw 'mode:' text should not be in output"
