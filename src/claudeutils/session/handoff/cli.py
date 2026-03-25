"""CLI command for session handoff: _handoff subcommand."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from claudeutils.git import _fail
from claudeutils.git_cli import git_changes
from claudeutils.session.handoff.parse import (
    HandoffInput,
    HandoffInputError,
    parse_handoff_input,
)
from claudeutils.session.handoff.pipeline import (
    clear_state,
    load_state,
    overwrite_status,
    save_state,
    write_completed,
)


def _parse_or_fail(text: str) -> HandoffInput:
    """Parse handoff markdown or exit with code 2 on error."""
    try:
        return parse_handoff_input(text)
    except HandoffInputError as e:
        _fail(f"**Error:** {e}", code=2)


@click.command(name="handoff", hidden=True)
def handoff_cmd() -> None:
    """Write session handoff to session.md."""
    session_path = Path(os.environ.get("CLAUDEUTILS_SESSION_FILE", "agents/session.md"))

    stdin_text = sys.stdin.read().strip()
    state = None
    input_markdown = ""

    if stdin_text:
        handoff_input = _parse_or_fail(stdin_text)
        input_markdown = stdin_text
        save_state(stdin_text, step_reached="write_session")
    else:
        state = load_state()
        if state is None:
            _fail(
                "**Error:** No input on stdin and no state file",
                code=2,
            )
        handoff_input = _parse_or_fail(state.input_markdown)
        input_markdown = state.input_markdown

    # Resume path: skip writes if already at diagnostics step
    if state is None or state.step_reached != "diagnostics":
        try:
            overwrite_status(session_path, handoff_input.status_line)
            write_completed(session_path, handoff_input.completed_lines)
        except (OSError, ValueError) as e:
            _fail(f"**Error:** {e}", code=2)
        # Update step_reached after writes succeed
        save_state(input_markdown, step_reached="diagnostics")

    # Always emit diagnostics — tree is almost certainly dirty after writes
    git_output = git_changes()
    click.echo(f"**Git status:**\n\n```\n{git_output}\n```")

    clear_state()
