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

    if stdin_text:
        handoff_input = _parse_or_fail(stdin_text)
        save_state(stdin_text)
    else:
        state = load_state()
        if state is None:
            _fail(
                "**Error:** No input on stdin and no state file",
                code=2,
            )
        handoff_input = _parse_or_fail(state.input_markdown)

    overwrite_status(session_path, handoff_input.status_line)
    write_completed(session_path, handoff_input.completed_lines)

    git_output = git_changes()
    if git_output:
        click.echo(f"**Git status:**\n\n```\n{git_output}\n```")

    clear_state()
