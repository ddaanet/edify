"""Session CLI commands: _handoff, _commit, _status."""

import click


@click.command(hidden=True)
def handoff_cmd() -> None:
    """Write session handoff to session.md."""
    raise NotImplementedError("_handoff not yet implemented")


@click.command(hidden=True)
def commit_cmd() -> None:
    """Commit staged changes via structured markdown input."""
    raise NotImplementedError("_commit not yet implemented")


@click.command(hidden=True)
def status_cmd() -> None:
    """Render STATUS output from session.md."""
    raise NotImplementedError("_status not yet implemented")
