"""Command-line interface for claudeutils."""

import json
import logging
import re
import sys
from pathlib import Path
from typing import cast

import click

from claudeutils.account.cli import account
from claudeutils.compose import compose, load_config
from claudeutils.discovery import list_top_level_sessions
from claudeutils.exceptions import ClaudeUtilsError
from claudeutils.extraction import extract_feedback_recursively
from claudeutils.filtering import categorize_feedback, filter_feedback
from claudeutils.markdown import process_file
from claudeutils.model.cli import model
from claudeutils.models import FeedbackItem
from claudeutils.paths import get_project_history_dir
from claudeutils.recall.cli import recall
from claudeutils.statusline.cli import statusline
from claudeutils.tokens_cli import handle_tokens
from claudeutils.validation.cli import validate
from claudeutils.worktree.cli import worktree


def _handle_compose_error(e: Exception) -> None:
    """Handle compose errors and exit with appropriate code."""
    if isinstance(e, FileNotFoundError):
        error_msg = str(e)
        if "Fragment not found" in error_msg:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)
        else:
            click.echo(f"Error: Configuration file not found: {e}", err=True)
            sys.exit(4)
    elif isinstance(e, ValueError):
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    elif isinstance(e, (TypeError, OSError)):
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)


def _show_compose_plan(config_file: str, config: dict[str, object]) -> None:
    """Display compose plan in dry-run mode."""
    click.echo("Dry-run mode - plan:")
    click.echo(f"  Config: {config_file}")
    fragments_list = config.get("fragments", [])
    frag_count = len(fragments_list) if isinstance(fragments_list, list) else 0
    click.echo(f"  Fragments: {frag_count} file(s)")
    click.echo(f"  Output: {config.get('output', 'N/A')}")


def _filter_rule_items(
    items: list[FeedbackItem], min_length: int
) -> list[FeedbackItem]:
    """Filter and deduplicate feedback items for rules extraction."""
    filtered_items = filter_feedback(items)
    rule_items = [
        item
        for item in filtered_items
        if not (
            (
                item.content.lower().startswith("how ")
                or item.content.lower().startswith("claude code:")
            )
            or len(item.content) < min_length
            or len(item.content) > 1000
        )
    ]

    # Sort and deduplicate
    rule_items.sort(key=lambda x: x.timestamp)
    seen_prefixes: set[str] = set()
    deduped_items = []
    for item in rule_items:
        prefix = item.content[:100].lower()
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            deduped_items.append(item)
    return deduped_items


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


@click.version_option(package_name="claudeutils", message="%(package)s %(version)s")
@click.group(
    help="Extract feedback from Claude Code sessions",
    epilog=(
        "Pipeline: collect -> analyze -> rules. Use collect to gather all "
        "feedback, analyze to filter and categorize, rules to extract "
        "actionable items."
    ),
)
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


cli.add_command(account)
cli.add_command(model)
cli.add_command(recall)
cli.add_command(statusline)
cli.add_command(validate)
cli.add_command(worktree)


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


@cli.command(help="Analyze feedback items")
@click.option(
    "--input", "input_path", required=True, help="Input JSON file, or '-' for stdin"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def analyze(input_path: str, output_format: str) -> None:
    """Analyze and categorize feedback."""
    json_text = sys.stdin.read() if input_path == "-" else Path(input_path).read_text()
    items = [FeedbackItem.model_validate(item) for item in json.loads(json_text)]
    filtered_items = filter_feedback(items)
    categories: dict[str, int] = {}
    for item in filtered_items:
        category = categorize_feedback(item)
        categories[category] = categories.get(category, 0) + 1
    if output_format == "json":
        print(
            json.dumps(
                {
                    "total": len(items),
                    "filtered": len(filtered_items),
                    "categories": categories,
                }
            )
        )
    else:
        print(f"total: {len(items)}\nfiltered: {len(filtered_items)}\ncategories:")
        for category, count in categories.items():
            print(f"  {category}: {count}")


@cli.command(help="Extract rule-worthy feedback items")
@click.option(
    "--input", "input_path", required=True, help="Input JSON file, or '-' for stdin"
)
@click.option(
    "--min-length",
    type=int,
    default=20,
    help="Minimum length for rule-worthy items (default: 20)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def rules(input_path: str, min_length: int, output_format: str) -> None:
    """Extract actionable rules from feedback."""
    json_text = sys.stdin.read() if input_path == "-" else Path(input_path).read_text()
    items = [FeedbackItem.model_validate(item) for item in json.loads(json_text)]
    deduped_items = _filter_rule_items(items, min_length)
    if output_format == "json":
        output = [
            {
                "index": i + 1,
                "timestamp": item.timestamp,
                "session_id": item.session_id,
                "content": item.content,
            }
            for i, item in enumerate(deduped_items)
        ]
        print(json.dumps(output))
    else:
        for i, item in enumerate(deduped_items, 1):
            print(f"{i}. {item.content}")


@cli.command(
    help="Count tokens in files using Anthropic API (requires ANTHROPIC_API_KEY)"
)
@click.argument("model", metavar="{haiku,sonnet,opus}")
@click.argument("files", nargs=-1, required=True, metavar="FILE")
@click.option(
    "--json", "json_output", is_flag=True, help="Output JSON format instead of text"
)
def tokens(model: str, files: tuple[str, ...], *, json_output: bool) -> None:
    """Count tokens in files via Anthropic API."""
    handle_tokens(model, list(files), json_output=json_output)


@cli.command(
    help="Compose markdown from YAML configuration",
    epilog=(
        "Load composition configuration from YAML file and compose markdown "
        "fragments into a single output file. Supports header adjustment, "
        "custom separators, and strict/warn validation modes."
    ),
)
@click.argument("config_file", type=click.Path())
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Override output path from config",
)
@click.option(
    "--validate",
    type=click.Choice(["strict", "warn"]),
    default="strict",
    help="Validation mode for missing fragments",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed output",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show plan without writing",
)
def compose_command(
    config_file: str,
    output: str | None,
    validate: str,
    verbose: bool,  # noqa: FBT001
    dry_run: bool,  # noqa: FBT001
) -> None:
    """Compose markdown from configuration."""
    config_path = Path(config_file)
    if not config_path.exists():
        click.echo(f"Error: Configuration file not found: {config_file}", err=True)
        sys.exit(4)

    try:
        # Load configuration
        if verbose:
            click.echo(f"Loading config from {config_file}")

        config = load_config(config_file)

        # Override output if specified
        if output:
            config["output"] = output

        # Show plan if dry-run
        if dry_run:
            _show_compose_plan(config_file, config)
            return

        # Extract config values with type narrowing
        fragments_val = cast("list[Path | str]", config.get("fragments", []))
        output_val = cast("Path | str", config["output"])
        title_val = cast("str | None", config.get("title"))
        adjust_headers_val = cast("bool", config.get("adjust_headers", False))
        separator_val = cast("str", config.get("separator", "---"))

        # Compose the document
        compose(
            fragments=fragments_val,
            output=output_val,
            title=title_val,
            adjust_headers=adjust_headers_val,
            separator=separator_val,
            validate_mode=validate,
        )

        if verbose:
            click.echo(f"Successfully composed to {config.get('output')}")

    except (FileNotFoundError, ValueError, TypeError, OSError) as e:
        _handle_compose_error(e)


@cli.command(help="Process markdown files")
def markdown() -> None:
    """Process markdown files from stdin."""
    files = [line.strip() for line in sys.stdin if line.strip()]
    errors: list[str] = []
    valid_files: list[Path] = []

    # Validate files
    for filepath_str in files:
        filepath = Path(filepath_str)
        if filepath.suffix != ".md":
            errors.append(f"Error: {filepath_str} is not a markdown file")
        elif not filepath.exists():
            errors.append(f"Error: {filepath_str} does not exist")
        else:
            valid_files.append(filepath)

    # Process valid files
    for filepath in valid_files:
        try:
            if process_file(filepath):
                print(str(filepath))
        except ClaudeUtilsError as e:
            errors.append(str(e))

    # Report errors
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)


main = cli  # Entry point alias
