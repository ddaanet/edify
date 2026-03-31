"""Session CLI commands: _handoff, _commit, _status."""

import sys

import click

from edify.git import _fail
from edify.session.commit import CommitInputError, parse_commit_input
from edify.session.commit_gate import CleanFileError
from edify.session.commit_pipeline import commit_pipeline
from edify.session.handoff.cli import handoff_cmd
from edify.session.status.cli import status_cmd

__all__ = ["commit_cmd", "handoff_cmd", "status_cmd"]


@click.command(hidden=True)
def commit_cmd() -> None:
    """Commit staged changes via structured markdown input."""
    stdin_text = sys.stdin.read().strip()
    if not stdin_text:
        _fail("**Error:** Missing required section: ## Files", code=2)

    try:
        ci = parse_commit_input(stdin_text)
    except CommitInputError as e:
        _fail(f"**Error:** {e}", code=2)

    try:
        result = commit_pipeline(ci)
    except CleanFileError as e:
        _fail(str(e), code=2)
    except CommitInputError as e:
        _fail(f"**Error:** {e}", code=2)

    click.echo(result.output)

    if not result.success:
        raise SystemExit(1)
