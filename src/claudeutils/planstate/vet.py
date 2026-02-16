"""Vet chain status inference for plan artifacts."""

from pathlib import Path

from .models import VetChain, VetStatus

SOURCE_TO_REPORT_MAP = {
    "outline.md": "reports/outline-review.md",
    "design.md": "reports/design-review.md",
    "runbook-outline.md": "reports/runbook-outline-review.md",
    "runbook-phase-1.md": "reports/phase-1-review.md",
    "runbook-phase-2.md": "reports/phase-2-review.md",
    "runbook-phase-3.md": "reports/phase-3-review.md",
    "runbook-phase-4.md": "reports/phase-4-review.md",
    "runbook-phase-5.md": "reports/phase-5-review.md",
    "runbook-phase-6.md": "reports/phase-6-review.md",
}


def get_vet_status(plan_dir: Path) -> VetStatus | None:
    """Scan plan_dir for recognized source artifacts and map to report paths.

    Returns VetStatus with chains for each source→report pair found. Returns
    None if no source artifacts are found.
    """
    chains = []

    for source_file, report_file in SOURCE_TO_REPORT_MAP.items():
        source_path = plan_dir / source_file
        report_path = plan_dir / report_file

        if source_path.exists():
            stale = False
            source_mtime = 0.0
            report_mtime = 0.0

            if report_path.exists():
                source_mtime = source_path.stat().st_mtime
                report_mtime = report_path.stat().st_mtime
                stale = source_mtime > report_mtime
            else:
                source_mtime = source_path.stat().st_mtime

            chain = VetChain(
                source=source_file,
                report=report_file,
                stale=stale,
                source_mtime=source_mtime,
                report_mtime=report_mtime,
            )
            chains.append(chain)

    if not chains:
        return None

    return VetStatus(chains=chains)
