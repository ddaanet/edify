"""CLI command for when memory recall."""

import os
import sys
from pathlib import Path

import click

from claudeutils.when.resolver import ResolveError, resolve


@click.command(name="when")
@click.argument("operator", type=click.Choice(["when", "how"]))
@click.argument("query", nargs=-1, required=True)
def when_cmd(operator: str, query: tuple[str, ...]) -> None:
    """Query memory index with fuzzy matching operators.

    OPERATOR: when or how
    QUERY: Search query (multiple words joined with spaces)
    """
    query_str = " ".join(query)

    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = project_root / "agents" / "memory-index.md"
    decisions_dir = project_root / "agents" / "decisions"

    try:
        result = resolve(operator, query_str, str(index_path), str(decisions_dir))
        click.echo(result)
    except ResolveError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
