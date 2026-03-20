"""CLI command for session handoff: _handoff subcommand."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import click

from claudeutils.git import _fail
from claudeutils.session.handoff.context import PrecommitResult, format_diagnostics
from claudeutils.session.handoff.parse import HandoffInputError, parse_handoff_input
from claudeutils.session.handoff.pipeline import (
    clear_state,
    load_state,
    overwrite_status,
    save_state,
    write_completed,
)


def _run_precommit() -> PrecommitResult:
    """Run ``just precommit`` and return result.

    Patchable in tests.
    """
    result = subprocess.run(
        ["just", "precommit"], capture_output=True, text=True, check=False
    )
    return PrecommitResult(
        passed=result.returncode == 0,
        output=result.stdout.strip(),
    )


@click.command(name="handoff", hidden=True)
def handoff_cmd() -> None:
    """Write session handoff to session.md."""
    session_path = Path(os.environ.get("CLAUDEUTILS_SESSION_FILE", "agents/session.md"))

    stdin_text = sys.stdin.read().strip()

    if stdin_text:
        try:
            handoff_input = parse_handoff_input(stdin_text)
        except HandoffInputError as e:
            _fail(f"**Error:** {e}", code=2)
        save_state(stdin_text, step="write_session")
    else:
        state = load_state()
        if state is None:
            _fail(
                "**Error:** No input on stdin and no state file",
                code=2,
            )
        try:
            handoff_input = parse_handoff_input(state.input_markdown)
        except HandoffInputError as e:
            _fail(f"**Error:** {e}", code=2)

    overwrite_status(session_path, handoff_input.status_line)
    write_completed(session_path, handoff_input.completed_lines)

    precommit_result = _run_precommit()

    git_output: str | None = None
    if precommit_result.passed:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        git_output = result.stdout.strip() or None

    diagnostics = format_diagnostics(
        precommit_result,
        git_output=git_output,
        learnings_age_days=None,
    )
    click.echo(diagnostics)

    if not precommit_result.passed:
        sys.exit(1)

    clear_state()
