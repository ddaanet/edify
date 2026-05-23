"""Command-line interface for edify."""

import json
import logging
import re
import sys
from pathlib import Path

import click

from edify.discovery import list_top_level_sessions
from edify.exceptions import ClaudeUtilsError
from edify.extraction import extract_feedback_recursively
from edify.markdown import process_file
from edify.paths import get_project_history_dir
from edify.tokens_cli import handle_tokens


def find_session_by_prefix(prefix: str, project_dir: str) -> str:
    """Find unique session ID matching prefix."""
    history_dir = get_project_history_dir(project_dir)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
    )

    matches = []
    if history_dir.exists():
        for file_path in history_dir.glob("*.jsonl"):
            if not uuid_pattern.match(file_path.name):
                continue
            session_id = file_path.name.replace(".jsonl", "")
            if session_id.startswith(prefix):
                matches.append(session_id)

    if len(matches) == 0:
        msg = f"No session found with prefix '{prefix}'"
        raise ValueError(msg)
    if len(matches) > 1:
        msg = f"Multiple sessions match prefix '{prefix}'"
        raise ValueError(msg)

    return matches[0]


@click.version_option(package_name="edify-cli", message="%(package)s %(version)s")
@click.group(help="Edify CLI: session scraping, token counting, markdown processing")
def cli() -> None:
    """Command-line interface entry point."""
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )


@cli.command("list", help="List top-level sessions")
@click.option("--project", default=None, help="Project directory")
def list_sessions(project: str | None) -> None:
    """List sessions in project history."""
    project = project or str(Path.cwd())
    sessions = list_top_level_sessions(project)
    if not sessions:
        print("No sessions found")
    else:
        for session in sessions:
            print(f"[{session.session_id[:8]}] {session.title}")


@cli.command(help="Extract feedback from session")
@click.argument("session_prefix")
@click.option("--project", default=None, help="Project directory")
@click.option("--output", help="Output file path")
def extract(session_prefix: str, project: str | None, output: str | None) -> None:
    """Extract feedback from session by prefix."""
    project = project or str(Path.cwd())
    try:
        session_id = find_session_by_prefix(session_prefix, project)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    feedback = extract_feedback_recursively(session_id, project)
    json_output = json.dumps([item.model_dump(mode="json") for item in feedback])
    (Path(output).write_text if output else print)(json_output)


@cli.command(help="Batch collect feedback from all sessions")
@click.option("--project", default=None, help="Project directory")
@click.option("--output", help="Output file path")
def collect(project: str | None, output: str | None) -> None:
    """Collect feedback from all project sessions."""
    project = project or str(Path.cwd())
    sessions = list_top_level_sessions(project)
    all_feedback = []
    for session in sessions:
        try:
            feedback = extract_feedback_recursively(session.session_id, project)
            all_feedback.extend(feedback)
        except (ValueError, OSError, RuntimeError) as e:
            print(
                f"Warning: Failed to extract from {session.session_id}: {e}",
                file=sys.stderr,
            )
    json_output = json.dumps([item.model_dump(mode="json") for item in all_feedback])
    (Path(output).write_text if output else print)(json_output)


@cli.command(help="Count tokens in one or more files using Anthropic API")
@click.option(
    "--model",
    default="sonnet",
    show_default=True,
    metavar="{haiku,sonnet,opus}",
    help="Model to use for token counting",
)
@click.argument("files", nargs=-1, required=True, metavar="FILE...")
@click.option(
    "--json", "json_output", is_flag=True, help="Output JSON format instead of text"
)
def tokens(model: str, files: tuple[str, ...], *, json_output: bool) -> None:
    """Count tokens in files via Anthropic API."""
    handle_tokens(model, list(files), json_output=json_output)


@cli.command(help="Process markdown files")
def markdown() -> None:
    """Process markdown files from stdin."""
    files = [line.strip() for line in sys.stdin if line.strip()]
    errors: list[str] = []
    valid_files: list[Path] = []

    for filepath_str in files:
        filepath = Path(filepath_str)
        if filepath.suffix != ".md":
            errors.append(f"Error: {filepath_str} is not a markdown file")
        elif not filepath.exists():
            errors.append(f"Error: {filepath_str} does not exist")
        else:
            valid_files.append(filepath)

    for filepath in valid_files:
        try:
            if process_file(filepath):
                print(str(filepath))
        except ClaudeUtilsError as e:
            errors.append(str(e))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)


main = cli  # Entry point alias
