"""Click group and subcommands for _recall artifact operations."""

import datetime
import os
import subprocess
from pathlib import Path

import click

from claudeutils.git import _fail
from claudeutils.when.resolver import ResolveError
from claudeutils.when.resolver import resolve as resolver_resolve

from .artifact import parse_entry_keys_section, parse_trigger


@click.group(name="_recall", hidden=True)
def recall_cmd() -> None:
    """Manage artifact operations (hidden)."""


@recall_cmd.command()
@click.argument("job")
def check(job: str) -> None:
    """Check if artifact has valid Entry Keys section.

    Exits 0 if artifact exists with >=1 entry, exits 1 otherwise.
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    artifact_path = project_root / "plans" / job / "recall-artifact.md"

    if not artifact_path.exists():
        _fail(f"recall-artifact.md missing for {job}", code=1)

    try:
        content = artifact_path.read_text()
    except (OSError, ValueError) as e:
        _fail(f"Failed to read artifact: {e}", code=1)

    entries = parse_entry_keys_section(content)

    if entries is None:
        _fail(f"recall-artifact.md has no Entry Keys section for {job}", code=1)

    if not entries:
        _fail(f"recall-artifact.md has no entries for {job}", code=1)

    # Valid artifact: exit 0


def _strip_operator(arg: str) -> str:
    """Strip optional operator prefix (when/how), return bare trigger."""
    parts = arg.split(" ", 1)
    if len(parts) >= 2 and parts[0].lower() in {"when", "how"}:
        return parts[1]
    return arg


def _load_triggers_from_artifact(artifact_path: str) -> list[str]:
    """Load triggers from artifact file."""
    try:
        content = Path(artifact_path).read_text()
    except (OSError, ValueError) as e:
        _fail(f"Failed to read artifact: {e}", code=1)

    entries = parse_entry_keys_section(content)
    if entries is None or not entries:
        _fail("Artifact has no Entry Keys entries", code=1)

    return [parse_trigger(entry) for entry in entries]


def _format_resolve_error(error: Exception, trigger: str) -> str:
    """Format resolution error message."""
    return f"Error resolving '{trigger}': {error}"


@recall_cmd.command()
@click.argument("args", nargs=-1, required=True)
def resolve(args: tuple[str, ...]) -> None:
    """Resolve artifact triggers to decision content.

    MODE DETECTION:
    - If first arg is a file path (artifact mode): read file, parse Entry Keys,
      resolve each trigger via when.resolver.resolve()
    - Otherwise (argument mode): resolve each arg as a trigger

    OUTPUT: Resolved content separated by ---, exit 0 on success.
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = str(project_root / "agents" / "memory-index.md")
    decisions_dir = str(project_root / "agents" / "decisions")

    is_artifact_mode = bool(args and Path(args[0]).is_file())
    triggers = (
        _load_triggers_from_artifact(args[0])
        if is_artifact_mode
        else [parse_trigger(arg) for arg in args]
    )

    results: list[str] = []
    seen: set[str] = set()
    errors: list[str] = []

    for trigger in triggers:
        query = _strip_operator(trigger)
        if not query.strip() or query == "null":
            continue

        try:
            result = resolver_resolve(query, index_path, decisions_dir)
            if result not in seen:
                seen.add(result)
                results.append(result)
        except (ResolveError, OSError, ValueError, RuntimeError) as e:
            errors.append(_format_resolve_error(e, trigger))

    output_parts = []
    if results:
        output_parts.append("\n---\n".join(results))
    if errors:
        output_parts.extend(errors)

    if output_parts:
        click.echo("\n".join(output_parts))

    if is_artifact_mode and errors:
        raise SystemExit(1)

    if not results:
        _fail("No entries resolved", code=1)


@recall_cmd.command()
@click.argument("job")
def diff(job: str) -> None:
    """List files changed in job directory since artifact mtime.

    Uses git log --since to find commits after artifact modification time.
    Excludes the artifact file itself from the output. Exits 0 on success
    (output may be empty), exits 1 only on precondition failures.
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    artifact_path = project_root / "plans" / job / "recall-artifact.md"

    if not artifact_path.exists():
        _fail(f"recall-artifact.md missing for {job}", code=1)

    # Check if inside a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=project_root,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        _fail("not inside a git repository", code=1)

    # Get artifact mtime, formatted for git log --since (ISO 8601)
    try:
        mtime_ts = artifact_path.stat().st_mtime
        mtime_dt = datetime.datetime.fromtimestamp(mtime_ts, tz=datetime.UTC)
        mtime_iso = mtime_dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (OSError, ValueError) as e:
        _fail(f"Failed to get artifact mtime: {e}", code=1)

    # Run git log to find changed files
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                f"--since={mtime_iso}",
                "--name-only",
                "--pretty=format:",
                "--",
                f"plans/{job}/",
            ],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError) as e:
        _fail(f"Failed to run git log: {e}", code=1)

    # Parse output: split by lines, filter blanks, exclude artifact, dedup, sort
    lines = [line for line in result.stdout.split("\n") if line.strip()]
    artifact_relative = f"plans/{job}/recall-artifact.md"
    changed_files = sorted({line for line in lines if line != artifact_relative})

    # Output sorted list
    for file_path in changed_files:
        click.echo(file_path)

    # Exit 0 always for this command (empty output is valid)
