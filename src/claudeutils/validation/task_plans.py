"""Validate that pending tasks reference plan-backed directories."""

import re
from pathlib import Path

from claudeutils.validation.task_parsing import parse_task_line

_RECOGNIZED_ARTIFACTS = {"requirements.md", "brief.md", "design.md"}
_PENDING_STATUSES = {" ", ">", "!"}
_PLAN_PATTERN = re.compile(r"plans/([^/\s`'\"]+)")
_SLUG_PATTERN = re.compile(r"/orchestrate\s+(\S+)")
# plans/reports/ is the shared reports container, not a plan directory
_CONTAINER_DIRS = {"reports"}


def validate(session_path: str, root: Path) -> list[str]:
    """Validate task plan references in session.md.

    Args:
        session_path: Relative path to session.md.
        root: Project root directory.

    Returns:
        List of error messages for tasks missing plan backing.
    """
    session_file = root / session_path
    if not session_file.exists():
        return []

    errors: list[str] = []
    content = session_file.read_text()

    for lineno, line in enumerate(content.splitlines(), start=1):
        parsed = parse_task_line(line, lineno)
        if not parsed:
            continue

        # Only validate pending tasks
        if parsed.checkbox not in _PENDING_STATUSES:
            continue

        # Extract plan slug from command or fall back to raw line scan
        search_text = parsed.command or parsed.full_line

        match = _PLAN_PATTERN.search(search_text)
        if not match:
            # Try slug-only pattern: /orchestrate my-plan
            slug_match = _SLUG_PATTERN.search(search_text)
            if not slug_match:
                errors.append(f"task '{parsed.name}': no plan reference in command")
                continue
            plan_slug = slug_match.group(1)
        else:
            plan_slug = match.group(1)

        # Skip container directories that are not plan directories
        if plan_slug in _CONTAINER_DIRS:
            continue
        plan_dir = root / "plans" / plan_slug

        # Check if plan directory exists and has a recognized artifact
        if not plan_dir.exists():
            errors.append(
                f"task '{parsed.name}': plan directory 'plans/{plan_slug}' not found"
            )
            continue

        # Check for recognized artifacts
        has_artifact = any(
            (plan_dir / artifact).exists() for artifact in _RECOGNIZED_ARTIFACTS
        )
        if not has_artifact:
            errors.append(
                f"task '{parsed.name}': plan 'plans/{plan_slug}' "
                "has no recognized artifacts"
            )

    return errors
