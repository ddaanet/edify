"""CLI command for when memory recall."""

import click


@click.command(name="when")
@click.argument("operator")
@click.argument("query")
def when_cmd(operator: str, query: str) -> None:
    """Query memory index with fuzzy matching operators.

    OPERATOR: Matching operator (fuzzy, exact, section, file)
    QUERY: Search query
    """
    click.echo(f"Operator: {operator}, Query: {query}")
