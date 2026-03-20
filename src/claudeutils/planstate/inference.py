"""Plan state inference from directory artifacts."""

import re
from collections.abc import Callable
from pathlib import Path

from .models import PlanState, VetChain


def _collect_artifacts(plan_dir: Path) -> set[str]:
    artifacts = set()

    # Baseline artifacts
    for filename in [
        "brief.md",
        "classification.md",
        "requirements.md",
        "inline-plan.md",
        "design.md",
        "outline.md",
        "lifecycle.md",
    ]:
        if (plan_dir / filename).exists():
            artifacts.add(filename)

    # Runbook phase files
    for phase_file in sorted(plan_dir.glob("runbook-phase-*.md")):
        artifacts.add(phase_file.name)

    # Ready-state artifacts
    if (plan_dir / "steps").is_dir():
        artifacts.add("steps")
    if (plan_dir / "orchestrator-plan.md").exists():
        artifacts.add("orchestrator-plan.md")

    return artifacts


def _parse_lifecycle_status(plan_dir: Path) -> str | None:
    """Parse lifecycle.md to extract current status.

    Returns the status from the last non-empty line if valid, None otherwise.
    Valid states: review-pending, rework, reviewed, delivered
    """
    lifecycle_file = plan_dir / "lifecycle.md"
    if not lifecycle_file.exists():
        return None

    content = lifecycle_file.read_text()
    lines = [line.strip() for line in content.split("\n") if line.strip()]

    if not lines:
        return None

    # Parse last non-empty line: split on spaces, extract second token
    last_line = lines[-1]
    parts = last_line.split()
    if len(parts) < 2:
        return None

    state = parts[1]
    valid_states = {"review-pending", "rework", "reviewed", "delivered"}
    return state if state in valid_states else None


def _determine_pre_ready_status(plan_dir: Path) -> str:
    """Determine pre-ready status from artifacts.

    Priority: ready > planned > inline-planned > designed > outlined > requirements.
    (briefed is a sub-case of requirements: brief.md present, no requirements.md)
    """
    if (plan_dir / "steps").is_dir() and (plan_dir / "orchestrator-plan.md").exists():
        return "ready"
    if list(plan_dir.glob("runbook-phase-*.md")):
        return "planned"
    if (plan_dir / "inline-plan.md").exists():
        return "inline-planned"
    if (plan_dir / "design.md").exists():
        return "designed"
    if (plan_dir / "outline.md").exists():
        return "outlined"
    has_brief_only = (plan_dir / "brief.md").exists() and not (
        (plan_dir / "requirements.md").exists()
    )
    return "briefed" if has_brief_only else "requirements"


def _determine_status(plan_dir: Path) -> str:
    """Determine status from artifacts.

    Checks lifecycle.md first; delegates to _determine_pre_ready_status
    otherwise.
    """
    lifecycle_status = _parse_lifecycle_status(plan_dir)
    if lifecycle_status is not None:
        return lifecycle_status
    return _determine_pre_ready_status(plan_dir)


_NEXT_ACTION_TEMPLATES: dict[str, str | None] = {
    "briefed": "/design plans/{plan_name}/brief.md",
    "requirements": "/design plans/{plan_name}/requirements.md",
    "outlined": "/design plans/{plan_name}/outline.md",
    "inline-planned": "/inline plans/{plan_name}",
    "designed": "/runbook plans/{plan_name}/design.md",
    "planned": "agent-core/bin/prepare-runbook.py plans/{plan_name}",
    "ready": "/orchestrate {plan_name}",
    "review-pending": "/deliverable-review plans/{plan_name}",
}


def _derive_next_action(status: str, plan_name: str) -> str:
    """Derive next action from plan status.

    Pre-ready states have defined actions. Post-ready states (rework, reviewed,
    delivered) are terminal or require manual intervention.
    """
    template = _NEXT_ACTION_TEMPLATES.get(status)
    if template is None:
        return ""
    return template.format(plan_name=plan_name)


_GATE_PRIORITY: list[tuple[str, str]] = [
    ("design.md", "design vet stale — re-vet before planning"),
    ("runbook-outline.md", "runbook outline vet stale — re-review before expansion"),
]


def _first_stale_gate(chains: list[VetChain]) -> str | None:
    """Return highest-priority gate message for stale chains.

    Priority: design > runbook outline > phase-level > outline.
    """
    stale_sources = {c.source for c in chains if c.stale}
    if not stale_sources:
        return None

    # Check design and runbook-outline (highest priority)
    for source, message in _GATE_PRIORITY:
        if source in stale_sources:
            return message

    # Check phase-level (any runbook-phase-N.md)
    phase_sources = sorted(s for s in stale_sources if s.startswith("runbook-phase-"))
    if phase_sources:
        # Report first stale phase
        match = re.search(r"runbook-phase-(\d+)", phase_sources[0])
        phase_num = match.group(1) if match else "?"
        return f"phase {phase_num} vet stale — re-review"

    # Check outline (lowest priority)
    if "outline.md" in stale_sources:
        return "outline vet stale — re-review before design"

    return None


def infer_state(
    plan_dir: Path, vet_status_func: Callable[[Path], object] | None = None
) -> PlanState | None:
    """Infer plan state from directory artifacts.

    Scans for recognized artifacts and returns PlanState or None if no artifacts
    found. Priority: lifecycle > ready > planned > designed > outlined > requirements

    Args:
        plan_dir: Path to the plan directory
        vet_status_func: Optional callable that returns VetStatus for testing

    Returns:
        PlanState with inferred status and metadata, or None if no artifacts found
    """
    if not plan_dir.exists():
        return None

    artifacts = _collect_artifacts(plan_dir)
    if not artifacts:
        return None

    name = plan_dir.name
    status = _determine_status(plan_dir)
    next_action = _derive_next_action(status, name)

    gate = None
    if vet_status_func is not None:
        vet_status = vet_status_func(plan_dir)
        if vet_status is not None and hasattr(vet_status, "chains"):
            gate = _first_stale_gate(vet_status.chains)

    return PlanState(
        name=name,
        status=status,
        next_action=next_action,
        gate=gate,
        artifacts=artifacts,
    )


def list_plans(plans_dir: Path) -> list[PlanState]:
    """List all plans in a plans directory, filtering out empty directories.

    Returns:
        List of PlanState objects for all valid plans, sorted by directory name
    """
    if not plans_dir.exists():
        return []

    plans = []
    for plan_dir in sorted(plans_dir.iterdir()):
        if plan_dir.is_dir():
            state = infer_state(plan_dir)
            if state is not None:
                plans.append(state)

    return plans
