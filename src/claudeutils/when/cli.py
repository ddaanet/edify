"""CLI command for when memory recall."""

import os
import sys
from pathlib import Path

import click

from claudeutils.when.resolver import ResolveError, resolve

VALID_OPERATORS = {"when", "how"}


def _parse_operator_query(arg: str) -> tuple[str, str] | None:
    """Parse operator prefix from a query string.

    Args:
        arg: A query string like "when writing mock tests" or "how encode paths"

    Returns:
        (operator, query) tuple, or None if arg has no valid operator prefix
    """
    parts = arg.split(" ", 1)
    if len(parts) >= 2 and parts[0] in VALID_OPERATORS:
        return parts[0], parts[1]
    return None


@click.command(name="when")
@click.argument("queries", nargs=-1, required=True)
def when_cmd(queries: tuple[str, ...]) -> None:
    """Query memory index with fuzzy matching operators.

    QUERIES: One or more queries, each prefixed with operator (when/how).
    Examples: "when writing mock tests", "how encode paths"
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = project_root / "agents" / "memory-index.md"
    decisions_dir = project_root / "agents" / "decisions"

    for arg in queries:
        parsed = _parse_operator_query(arg)
        if parsed is None:
            operators = ", ".join(sorted(VALID_OPERATORS))
            msg = f"Error: Query must start with a valid operator ({operators})."
            click.echo(msg, err=True)
            sys.exit(1)
        operator, query_str = parsed

        try:
            result = resolve(operator, query_str, str(index_path), str(decisions_dir))
            click.echo(result)
        except ResolveError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
