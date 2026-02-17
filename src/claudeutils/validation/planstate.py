"""Validate plan state consistency.

Checks:
- All plan directories have recognized artifacts
- Steps/ and runbook-phase-*.md files are consistent
- Orchestrator-plan.md has corresponding steps/
- Archived plans don't still have directories
"""

import re
from pathlib import Path

from claudeutils.planstate.inference import infer_state

_SKIP_DIRS = {"reports", "claude"}


def _check_plan_consistency(plan_dir: Path) -> list[str]:
    """Check artifact consistency within a single plan directory."""
    state = infer_state(plan_dir)
    if state is None:
        return [f"Plan '{plan_dir.name}' has no recognized artifacts"]

    errors: list[str] = []

    if (plan_dir / "steps").is_dir() and not list(plan_dir.glob("runbook-phase-*.md")):
        errors.append(
            f"Plan '{plan_dir.name}' has steps/ without runbook-phase-*.md files"
        )

    if (plan_dir / "orchestrator-plan.md").exists() and not (
        plan_dir / "steps"
    ).is_dir():
        errors.append(
            f"Plan '{plan_dir.name}' has orchestrator-plan.md without steps/ directory"
        )

    return errors


def _check_archive_orphans(root: Path, plans_dir: Path) -> list[str]:
    """Check for archived plans that still have directories."""
    archive_path = root / "agents" / "plan-archive.md"
    if not archive_path.exists():
        return []

    content = archive_path.read_text()
    archived_names = re.findall(r"^## (.+)$", content, re.MULTILINE)
    return [
        f"Plan '{name}' archived but directory still exists"
        for name in archived_names
        if (plans_dir / name).is_dir()
    ]


def validate(root: Path) -> list[str]:
    """Validate plan state across plans/ directory.

    Returns list of error/warning messages. Empty list if no issues.
    """
    plans_dir = root / "plans"
    if not plans_dir.exists():
        return []

    errors: list[str] = []
    for plan_dir in sorted(plans_dir.iterdir()):
        if not plan_dir.is_dir() or plan_dir.name in _SKIP_DIRS:
            continue
        errors.extend(_check_plan_consistency(plan_dir))

    errors.extend(_check_archive_orphans(root, plans_dir))
    return errors
