"""Tests for the statusline CLI command."""

from click.testing import CliRunner

from edify.cli import cli
from edify.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    ModelInfo,
    StatuslineInput,
    WorkspaceInfo,
)


def test_statusline_reads_stdin() -> None:
    """Test that statusline command reads JSON from stdin."""
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
    result = runner.invoke(cli, ["statusline"], input=json_str)
    # The command should exist and return exit code 0
    assert result.exit_code == 0
