"""CLI command for when memory recall."""

import os
from pathlib import Path

import click

from claudeutils.when.resolver import resolve


@click.command(name="when")
@click.argument("operator", type=click.Choice(["when", "how"]))
@click.argument("query", nargs=-1, required=True)
def when_cmd(operator: str, query: tuple[str, ...]) -> None:  # noqa: ARG001
    """Query memory index with fuzzy matching operators.

    OPERATOR: when or how
    QUERY: Search query (multiple words joined with spaces)
    """
    query_str = " ".join(query)

    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = project_root / "agents" / "memory-index.md"
    decisions_dir = project_root / "agents" / "decisions"

    result = resolve(query_str, str(index_path), str(decisions_dir))
    click.echo(result)
