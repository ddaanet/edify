"""Validate plan archive coverage for deleted plans."""

import re
import subprocess
from pathlib import Path


def get_staged_plan_deletions(root: Path) -> list[str]:
    """Get plan directory names staged for deletion.

    Uses git diff --cached --name-status to find deleted files in plans/.
    Aggregates to directory level — a plan is "deleted" if ALL its tracked
    files are deleted.

    Args:
        root: Project root or repository root.

    Returns:
        List of deleted plan directory names (non-substantive plans excluded).
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return []

    deleted_files = set()

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        status, path = parts

        if status == "D" and path.startswith("plans/"):
            # Extract plan name from path like "plans/plan-name/file.md"
            path_parts = path.split("/")
            if len(path_parts) >= 2:
                plan_name = path_parts[1]
                deleted_files.add((plan_name, path))

    # Group files by plan and check if only .gitkeep remains
    plans_with_files: dict[str, list[str]] = {}
    for plan_name, filepath in deleted_files:
        if plan_name not in plans_with_files:
            plans_with_files[plan_name] = []
        plans_with_files[plan_name].append(filepath)

    # Only include plans that had substantive content (non-.gitkeep files)
    return sorted(
        [
            plan_name
            for plan_name, files in plans_with_files.items()
            if any(not f.endswith(".gitkeep") for f in files)
        ]
    )


def get_archive_headings(root: Path) -> set[str]:
    """Extract H2 headings from agents/plan-archive.md.

    Args:
        root: Project root directory.

    Returns:
        Set of heading names (case-insensitive comparison).
    """
    archive_path = root / "agents" / "plan-archive.md"
    if not archive_path.exists():
        return set()

    headings = set()
    with archive_path.open() as f:
        for line in f:
            # Match H2 headings: "## heading-name"
            match = re.match(r"^##\s+(.+)$", line.strip())
            if match:
                headings.add(match.group(1))

    return headings


def check_plan_archive_coverage(
    root: Path,
    deleted_plans: list[str] | None = None,
    archive_headings: set[str] | None = None,
) -> list[str]:
    """Validate deleted plans have archive entries.

    Args:
        root: Project root directory.
        deleted_plans: Optional pre-computed list of deleted plans (for testing).
                      If None, queries git staging area.
        archive_headings: Optional pre-computed archive headings (for testing).
                         If None, reads from agents/plan-archive.md.

    Returns:
        List of error strings. Empty if all deleted plans are archived.
    """
    if deleted_plans is None:
        deleted_plans = get_staged_plan_deletions(root)
    if archive_headings is None:
        archive_headings = get_archive_headings(root)

    # Normalize archive headings to lowercase for case-insensitive comparison
    archive_lower = {h.lower() for h in archive_headings}

    return [
        f"Deleted plan '{plan_name}' has no entry in agents/plan-archive.md"
        for plan_name in deleted_plans
        if plan_name.lower() not in archive_lower
    ]
