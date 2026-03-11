"""CLI commands for validation."""

import sys
from pathlib import Path

import click

from claudeutils.validation.common import find_project_root
from claudeutils.validation.decision_files import validate as validate_decision_files
from claudeutils.validation.learnings import validate as validate_learnings
from claudeutils.validation.memory_index import validate as validate_memory_index
from claudeutils.validation.plan_archive import (
    check_plan_archive_coverage,
)
from claudeutils.validation.planstate import validate as validate_planstate
from claudeutils.validation.session_refs import validate as validate_session_refs
from claudeutils.validation.session_structure import (
    validate as validate_session_structure,
)
from claudeutils.validation.task_plans import validate as validate_task_plans
from claudeutils.validation.tasks import validate as validate_tasks


def _run_validator(
    name: str, validator_func: object, all_errors: dict[str, list[str]], *args: object
) -> None:
    """Run a single validator and collect errors.

    Args:
        name: Validator name for error reporting.
        validator_func: Validator function to call.
        all_errors: Dictionary to accumulate errors.
        *args: Arguments to pass to validator function.
    """
    try:
        # Type ignore needed because validator_func is callable but typed as object
        errors = validator_func(*args)  # type: ignore[operator]
        if errors:
            all_errors[name] = errors
    except (ValueError, FileNotFoundError, OSError) as e:
        all_errors[name] = [f"Error: {e}"]


def _run_all_validators(root: Path) -> dict[str, list[str]]:
    """Run all validators and collect errors.

    Args:
        root: Project root directory.

    Returns:
        Dictionary mapping validator names to error lists.
    """
    all_errors: dict[str, list[str]] = {}

    _run_validator(
        "learnings", validate_learnings, all_errors, Path("agents/learnings.md"), root
    )
    _run_validator(
        "memory-index",
        validate_memory_index,
        all_errors,
        Path("agents/memory-index.md"),
        root,
    )
    _run_validator(
        "tasks",
        validate_tasks,
        all_errors,
        "agents/session.md",
        "agents/learnings.md",
        root,
    )
    _run_validator("decisions", validate_decision_files, all_errors, root)
    _run_validator("planstate", validate_planstate, all_errors, root)
    _run_validator("session-refs", validate_session_refs, all_errors, root)
    # session-structure returns (errors, warnings) — handle separately
    try:
        struct_errors, struct_warnings = validate_session_structure(
            "agents/session.md", root
        )
        if struct_errors:
            all_errors["session-structure"] = struct_errors
        if struct_warnings:
            for warning in struct_warnings:
                click.echo(f"Warning (session-structure): {warning}", err=True)
    except (ValueError, FileNotFoundError, OSError) as e:
        all_errors["session-structure"] = [f"Error: {e}"]
    _run_validator("plan-archive", check_plan_archive_coverage, all_errors, root)
    _run_validator(
        "task-plans", validate_task_plans, all_errors, "agents/session.md", root
    )

    return all_errors


@click.group(invoke_without_command=True)
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate project structure and conventions.

    Run all validators by default, or specify individual validators.
    """
    if ctx.invoked_subcommand is None:
        # Run all validators
        root = find_project_root(Path.cwd())
        all_errors = _run_all_validators(root)

        # Print errors with headers
        if all_errors:
            for validator_name, errors in all_errors.items():
                click.echo(f"Error ({validator_name}):", err=True)
                for error in errors:
                    click.echo(f"  {error}", err=True)
            sys.exit(1)


@validate.command()
def learnings() -> None:
    """Validate learnings.md."""
    root = find_project_root(Path.cwd())
    errors = validate_learnings(Path("agents/learnings.md"), root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def memory_index() -> None:
    """Validate memory-index.md."""
    root = find_project_root(Path.cwd())
    errors = validate_memory_index(Path("agents/memory-index.md"), root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def tasks() -> None:
    """Validate task keys in session.md."""
    root = find_project_root(Path.cwd())
    errors = validate_tasks("agents/session.md", "agents/learnings.md", root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def decisions() -> None:
    """Validate decision files."""
    root = find_project_root(Path.cwd())
    errors = validate_decision_files(root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def planstate() -> None:
    """Validate plan state consistency."""
    root = find_project_root(Path.cwd())
    errors = validate_planstate(root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def session_refs() -> None:
    """Validate session files reject tmp/ references."""
    root = find_project_root(Path.cwd())
    errors = validate_session_refs(root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def session_structure() -> None:
    """Validate session.md structure."""
    root = find_project_root(Path.cwd())
    errors, warnings = validate_session_structure("agents/session.md", root)
    for warning in warnings:
        click.echo(f"Warning: {warning}", err=True)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def plan_archive() -> None:
    """Validate deleted plans have archive entries."""
    root = find_project_root(Path.cwd())
    errors = check_plan_archive_coverage(root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)


@validate.command()
def task_plans() -> None:
    """Validate task plan references."""
    root = find_project_root(Path.cwd())
    errors = validate_task_plans("agents/session.md", root)
    if errors:
        for error in errors:
            click.echo(error, err=True)
        sys.exit(1)
