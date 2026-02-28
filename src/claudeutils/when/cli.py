"""CLI command for when memory recall."""

import os
import sys
from pathlib import Path

import click

from claudeutils.when.resolver import ResolveError, resolve

VALID_OPERATORS = {"when", "how"}


def _strip_operator(arg: str) -> str:
    """Strip optional operator prefix (when/how), return bare trigger."""
    parts = arg.split(" ", 1)
    if len(parts) >= 2 and parts[0].lower() in VALID_OPERATORS:
        return parts[1]
    return arg


def _collect_queries(args: tuple[str, ...]) -> list[str]:
    """Collect queries from CLI args and stdin.

    Args first, then stdin lines (if piped). Blank stdin lines skipped.
    """
    queries = list(args or [])

    if not sys.stdin.isatty():
        for line in sys.stdin:
            stripped = line.strip()
            if stripped:
                queries.append(stripped)

    return queries


def _resolve_queries(
    queries: list[str], index_path: str, decisions_dir: str
) -> tuple[list[str], list[str]]:
    """Resolve queries, deduplicating results."""
    results: list[str] = []
    seen: set[str] = set()
    errors: list[str] = []

    for query in queries:
        query_str = _strip_operator(query)
        if not query_str.strip():
            errors.append(f"Error: Empty query body in '{query}'.")
            continue

        try:
            result = resolve(query_str, index_path, decisions_dir)
            if result not in seen:
                seen.add(result)
                results.append(result)
        except ResolveError as e:
            errors.append(str(e))

    return results, errors


@click.command(name="when")
@click.argument("queries", nargs=-1, required=False)
def when_cmd(queries: tuple[str, ...]) -> None:
    """Query memory index with fuzzy matching.

    QUERIES: One or more trigger queries (args and/or stdin, one per line).
    Operator prefix (when/how) is optional.
    "null" is reserved as a D+B gate anchor (silent exit 0, no output).
    Examples: "writing mock tests", "when writing mock tests", "how encode paths"
    """
    all_queries = _collect_queries(queries)

    if not all_queries:
        raise click.UsageError("No queries provided")  # noqa: TRY003 — Click API

    # "null" is a reserved gate anchor — silently skip it so D+B gates have
    # an equal-cost negative path (no output, exit 0).
    active_queries = [q for q in all_queries if _strip_operator(q) != "null"]
    if not active_queries:
        return

    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = str(project_root / "agents" / "memory-index.md")
    decisions_dir = str(project_root / "agents" / "decisions")

    results, errors = _resolve_queries(active_queries, index_path, decisions_dir)

    if results:
        click.echo("\n---\n".join(results))

    if errors:
        for err in errors:
            click.echo(err)
        sys.exit(1)
