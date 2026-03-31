"""Vet chain status inference for plan artifacts."""

import re
from pathlib import Path

from .models import VetChain, VetStatus

_STATIC_SOURCE_TO_REPORT: dict[str, str] = {
    "outline.md": "reports/outline-review.md",
    "design.md": "reports/design-review.md",
    "runbook-outline.md": "reports/runbook-outline-review.md",
}


def _build_source_report_map(plan_dir: Path) -> dict[str, str]:
    """Build source→report map with dynamic phase discovery."""
    mapping = dict(_STATIC_SOURCE_TO_REPORT)
    for phase_file in sorted(plan_dir.glob("runbook-phase-*.md")):
        match = re.search(r"runbook-phase-(\d+)", phase_file.name)
        if match:
            n = match.group(1)
            mapping[phase_file.name] = f"reports/phase-{n}-review.md"
    return mapping


def _extract_iteration_number(filename: str) -> int | None:
    """Extract iteration number from report filename.

    Returns the numeric suffix (e.g., outline-review-3.md → 3). Returns None if
    no number found.
    """
    # Match patterns like -2, -3 at the end before extension
    # But exclude variant suffixes like -opus
    match = re.search(r"-(\d+)(?:\.[^.]*)?$", filename)
    if match:
        return int(match.group(1))
    return None


def _find_best_report(candidates: list[Path]) -> Path | None:
    """Select best report from candidates: highest iteration number or highest mtime.

    Candidates can include both numbered iterations (e.g., outline-review-3.md)
    and variants (e.g., outline-review-opus.md).
    """
    if not candidates:
        return None

    # Separate candidates with iteration numbers from variants
    numbered = []
    unnumbered = []

    for candidate in candidates:
        iteration = _extract_iteration_number(candidate.name)
        if iteration is not None:
            numbered.append((iteration, candidate))
        else:
            unnumbered.append(candidate)

    # If we have numbered reports, return the one with highest iteration number
    if numbered:
        highest = max(numbered, key=lambda x: x[0])
        return highest[1]

    # No numbered reports; use highest mtime among all candidates
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _find_iterative_report_for_source(
    reports_dir: Path, source_file: str, report_file: str
) -> str | None:
    """Find best iterative review for a source artifact.

    Returns report path (relative to plan_dir) with highest iteration number, or
    highest mtime if no iterations found. Returns None if no matches.
    """
    if not reports_dir.exists():
        return None

    if source_file.startswith("runbook-phase-"):
        # For phase sources, glob using phase number
        match = re.search(r"runbook-phase-(\d+)", source_file)
        if match:
            phase_num = int(match.group(1))
            pattern = f"*-{phase_num}-*"
            candidates = [
                f
                for f in reports_dir.glob(pattern)
                if "review" in f.name or "vet" in f.name
            ]
            if not candidates:
                # Fallback: phase number at end before extension (e.g., phase-1.md)
                candidates = [
                    f
                    for f in reports_dir.glob(f"*-{phase_num}.*")
                    if "review" in f.name or "vet" in f.name
                ]
            if candidates:
                best = _find_best_report(candidates)
                if best:
                    return f"reports/{best.name}"
    else:
        # For non-phase sources, glob by report base name
        report_base = report_file.replace(".md", "").replace("reports/", "")
        pattern = f"{report_base}*.md"
        candidates = list(reports_dir.glob(pattern))
        if candidates:
            best = _find_best_report(candidates)
            if best:
                return f"reports/{best.name}"

    return None


def get_vet_status(plan_dir: Path) -> VetStatus | None:
    """Scan plan_dir for recognized source artifacts and map to report paths.

    Returns VetStatus with chains for each source→report pair found. Returns
    None if no source artifacts are found.
    """
    chains = []
    reports_dir = plan_dir / "reports"

    source_report_map = _build_source_report_map(plan_dir)
    for source_file, report_file in source_report_map.items():
        source_path = plan_dir / source_file

        if not source_path.exists():
            continue

        # Check for iterative reviews first, then fall back to primary
        actual_report = _find_iterative_report_for_source(
            reports_dir, source_file, report_file
        )
        if not actual_report:
            actual_report = report_file

        report_path = plan_dir / actual_report

        # Determine staleness
        source_mtime = source_path.stat().st_mtime
        report_mtime = None
        stale = True

        if report_path.exists():
            report_mtime = report_path.stat().st_mtime
            stale = source_mtime > report_mtime
        else:
            actual_report = None

        chain = VetChain(
            source=source_file,
            report=actual_report,
            stale=stale,
            source_mtime=source_mtime,
            report_mtime=report_mtime,
        )
        chains.append(chain)

    if not chains:
        return None

    return VetStatus(chains=chains)
