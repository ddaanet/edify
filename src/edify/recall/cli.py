"""CLI command for memory index recall analysis."""

import sys
from pathlib import Path

import click

from edify.discovery import list_top_level_sessions
from edify.models import SessionInfo
from edify.paths import get_project_history_dir
from edify.recall.index_parser import IndexEntry, parse_memory_index
from edify.recall.recall import RecallAnalysis, calculate_recall
from edify.recall.relevance import RelevanceScore, find_relevant_entries
from edify.recall.report import generate_json_report, generate_markdown_report
from edify.recall.tool_calls import ToolCall, extract_tool_calls_from_session
from edify.recall.topics import extract_session_topics


def _validate_inputs(
    index: str,
    index_entries: list[IndexEntry],
    all_sessions: list[SessionInfo],
) -> tuple[Path, bool]:
    """Validate inputs and return index path and validation status.

    Args:
        index: Path to index file as string
        index_entries: Parsed index entries
        all_sessions: List of session info objects

    Returns:
        Tuple of (index_path, validation_passed)
    """
    index_path = Path(index)
    if not index_path.exists():
        click.echo(f"Error: Index file not found: {index}", err=True)
        return index_path, False

    if not index_entries:
        click.echo("Error: No index entries parsed from index file", err=True)
        return index_path, False

    if not all_sessions:
        click.echo("Error: No sessions found in project history", err=True)
        return index_path, False

    return index_path, True


def _extract_session_data(
    analyzed_sessions: list[SessionInfo],
    history_dir: Path,
    index_entries: list[IndexEntry],
    threshold: float,
) -> tuple[dict[str, list[ToolCall]], dict[str, list[RelevanceScore]]]:
    """Extract tool calls and relevant entries from sessions.

    Args:
        analyzed_sessions: List of session info to process
        history_dir: Path to session history directory
        index_entries: Parsed index entries
        threshold: Relevance threshold

    Returns:
        Tuple of (sessions_data, relevant_entries) dicts
    """
    sessions_data = {}
    relevant_entries = {}

    for session_info in analyzed_sessions:
        session_file = history_dir / f"{session_info.session_id}.jsonl"
        if not session_file.exists():
            continue

        # Extract tool calls
        tool_calls = extract_tool_calls_from_session(session_file)
        sessions_data[session_info.session_id] = tool_calls

        # Extract topics
        topics = extract_session_topics(session_file)
        if topics:
            # Find relevant entries
            relevant = find_relevant_entries(
                session_info.session_id, topics, index_entries, threshold
            )
            if relevant:
                relevant_entries[session_info.session_id] = relevant

    return sessions_data, relevant_entries


def _generate_and_output_report(
    analysis: RecallAnalysis, output_format: str, output: str | None
) -> None:
    """Generate report and write to output destination.

    Args:
        analysis: RecallAnalysis object
        output_format: Format type (json or markdown)
        output: Optional output file path
    """
    if output_format == "json":
        report_content = generate_json_report(analysis)
    else:
        report_content = generate_markdown_report(analysis)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content)
        click.echo(f"Report written to {output}")
    else:
        click.echo(report_content)


@click.command()
@click.option(
    "--index",
    required=True,
    type=click.Path(exists=True),
    help="Path to memory-index.md",
)
@click.option(
    "--sessions",
    default=30,
    type=int,
    help="Number of recent sessions to analyze (default: 30)",
)
@click.option(
    "--baseline-before",
    "_baseline_before",
    default=None,
    type=str,
    help="ISO date cutoff for baseline sessions (format: YYYY-MM-DD)",
)
@click.option(
    "--threshold",
    default=0.3,
    type=float,
    help="Relevance threshold (default: 0.3)",
)
@click.option(
    "--output-format",
    default="markdown",
    type=click.Choice(["markdown", "json"]),
    help="Output format (default: markdown)",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Write report to file (default: stdout)",
)
def recall(
    index: str,
    sessions: int,
    _baseline_before: str | None,
    threshold: float,
    output_format: str,
    output: str | None,
) -> None:
    """Analyze memory index recall effectiveness.

    Runs recall analysis on local session history to measure whether agents
    consult relevant memory index entries when working on related topics.
    """
    try:
        # Parse memory index
        index_entries = parse_memory_index(Path(index))

        # Get project directory and list sessions
        project_dir = str(Path.cwd())
        all_sessions = list_top_level_sessions(project_dir)

        # Validate inputs
        _, valid = _validate_inputs(index, index_entries, all_sessions)
        if not valid:
            sys.exit(1)

        click.echo(f"Parsed {len(index_entries)} index entries")
        click.echo(f"Found {len(all_sessions)} sessions")

        # Limit to requested number
        analyzed_sessions = all_sessions[:sessions]
        click.echo(f"Analyzing {len(analyzed_sessions)} sessions")

        # Get history directory
        history_dir = get_project_history_dir(project_dir)

        # Extract session data
        sessions_data, relevant_entries = _extract_session_data(
            analyzed_sessions, history_dir, index_entries, threshold
        )

        if not relevant_entries:
            click.echo("Warning: No relevant entries found in sessions", err=True)

        # Calculate recall metrics
        analysis = calculate_recall(sessions_data, relevant_entries, index_entries)

        # Generate and output report
        _generate_and_output_report(analysis, output_format, output)

    except (OSError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
