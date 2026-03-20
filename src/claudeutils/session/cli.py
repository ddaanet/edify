"""Session CLI commands: _handoff, _commit, _status."""

import click

from claudeutils.session.handoff.cli import handoff_cmd
from claudeutils.session.status.cli import status_cmd

__all__ = ["commit_cmd", "handoff_cmd", "status_cmd"]


@click.command(hidden=True)
def commit_cmd() -> None:
    """Commit staged changes via structured markdown input."""
    raise NotImplementedError("_commit not yet implemented")
