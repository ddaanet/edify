"""CLI command for statusline."""

import sys

import click

from edify.account.state import get_account_state
from edify.statusline.api_usage import get_api_usage, get_switchback_time
from edify.statusline.context import (
    calculate_context_tokens,
    get_git_status,
    get_python_env,
    get_thinking_state,
)
from edify.statusline.display import StatuslineFormatter
from edify.statusline.models import StatuslineInput
from edify.statusline.plan_usage import get_plan_usage


def _format_usage_line(account_mode: str) -> str:
    """Format usage data based on account mode.

    Args:
        account_mode: Either 'plan' or 'api'.

    Returns:
        Formatted usage line string.
    """
    formatter = StatuslineFormatter()
    usage_line = ""

    if account_mode == "plan":
        plan_data = get_plan_usage()
        if plan_data:
            usage_line = formatter.format_plan_limits(plan_data)
    elif account_mode == "api":
        api_data = get_api_usage()
        if api_data:
            # Format API token counts by tier
            o_today = formatter.format_tokens(api_data.today_opus)
            s_today = formatter.format_tokens(api_data.today_sonnet)
            h_today = formatter.format_tokens(api_data.today_haiku)
            today_str = f"today: o{o_today} s{s_today} h{h_today}"
            o_week = formatter.format_tokens(api_data.week_opus)
            s_week = formatter.format_tokens(api_data.week_sonnet)
            h_week = formatter.format_tokens(api_data.week_haiku)
            week_str = f"week: o{o_week} s{s_week} h{h_week}"
            usage_line = f"{today_str} | {week_str}"

        # Add switchback time if available
        switchback_time = get_switchback_time()
        if switchback_time:
            if usage_line:
                usage_line = f"{usage_line} | switchback: {switchback_time}"
            else:
                usage_line = f"switchback: {switchback_time}"

    return usage_line


@click.command("statusline")
def statusline() -> None:
    """Display statusline reading JSON from stdin."""
    try:
        input_data = sys.stdin.read()

        if input_data.strip():
            parsed_input = StatuslineInput.model_validate_json(input_data)
            git_status = get_git_status()
            python_env = get_python_env()
            thinking_state = get_thinking_state()
            context_tokens = calculate_context_tokens(parsed_input)

            # Get account state and usage info
            account_state = get_account_state()
            usage_line = _format_usage_line(account_state.mode)

            # Format line 1 components
            formatter = StatuslineFormatter()
            formatted_model = formatter.format_model(
                parsed_input.model.display_name, thinking_enabled=thinking_state.enabled
            )
            formatted_dir = formatter.format_directory(
                parsed_input.workspace.current_dir
            )
            formatted_git = formatter.format_git_status(git_status)
            formatted_python = formatter.format_python_env(python_env)
            formatted_cost = formatter.format_cost(parsed_input.cost.total_cost_usd)
            formatted_context = formatter.format_context(context_tokens)

            # Build line 1 with double-space separator (matches shell)
            line1_parts = [formatted_model, formatted_dir, formatted_git]
            if formatted_python:
                line1_parts.append(formatted_python)
            line1_parts.extend([formatted_cost, formatted_context])
            line1 = "  ".join(line1_parts)

            # Format line 2: mode + usage info
            formatted_mode = formatter.format_mode(account_state.mode)
            line2 = formatted_mode
            if usage_line:
                line2 = f"{line2}  {usage_line}"

            click.echo(line1, color=True)
            click.echo(line2, color=True)
        else:
            click.echo("", color=True)
            click.echo("", color=True)
    except Exception as e:  # noqa: BLE001 - R5: Always exit 0, catch all exceptions
        click.echo(f"Error: {e}", err=True)
