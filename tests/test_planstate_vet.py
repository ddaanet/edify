"""Tests for planstate vet module."""

import os
from pathlib import Path

import pytest

from edify.planstate.models import VetChain, VetStatus
from edify.planstate.vet import get_vet_status


@pytest.mark.parametrize(
    ("source_file", "expected_report"),
    [
        ("outline.md", "reports/outline-review.md"),
        ("design.md", "reports/design-review.md"),
        ("runbook-outline.md", "reports/runbook-outline-review.md"),
        ("runbook-phase-1.md", "reports/phase-1-review.md"),
    ],
)
def test_source_report_mapping_conventions(
    tmp_path: Path,
    source_file: str,
    expected_report: str,
) -> None:
    """Test source→report mapping for all convention types."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()

    # Create source artifact
    (plan_dir / source_file).write_text("")

    # Create report directory and report file
    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()
    (plan_dir / expected_report).write_text("")

    vet_status = get_vet_status(plan_dir)

    assert vet_status is not None
    assert len(vet_status.chains) == 1

    chain = vet_status.chains[0]
    assert chain.source == source_file
    assert chain.report == expected_report


def test_phase_level_fallback_glob(tmp_path: Path) -> None:
    """Test fallback glob when phase-level report naming varies."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()

    # Create source artifact
    (plan_dir / "runbook-phase-3.md").write_text("")

    # Create multiple report naming variants with different mtimes
    # but NOT the primary pattern (phase-3-review.md)
    checkpoint_3_vet = reports_dir / "checkpoint-3-vet.md"
    phase_3_review_opus = reports_dir / "phase-3-review-opus.md"

    # Write files and set mtimes to establish precedence
    checkpoint_3_vet.write_text("")
    os.utime(checkpoint_3_vet, (2000, 2000))

    phase_3_review_opus.write_text("")
    os.utime(phase_3_review_opus, (1500, 1500))

    # Without fallback glob, no report would be found (primary pattern doesn't exist).
    # With fallback, we should find one of the variants.
    # Most recent (highest mtime) should win: checkpoint-3-vet.md
    vet_status = get_vet_status(plan_dir)

    assert vet_status is not None
    assert len(vet_status.chains) == 1

    chain = vet_status.chains[0]
    assert chain.source == "runbook-phase-3.md"
    assert chain.report == "reports/checkpoint-3-vet.md"


def test_mtime_comparison_staleness(tmp_path: Path) -> None:
    """Test mtime comparison determines staleness correctly."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()

    # Case 1: Fresh report (report_mtime > source_mtime, so stale = False)
    source_fresh = plan_dir / "design.md"
    report_fresh = reports_dir / "design-review.md"
    source_fresh.write_text("")
    report_fresh.write_text("")
    os.utime(source_fresh, (1000, 1000))  # older
    os.utime(report_fresh, (2000, 2000))  # newer

    vet_status = get_vet_status(plan_dir)
    assert vet_status is not None
    assert len(vet_status.chains) == 1
    chain = vet_status.chains[0]
    assert chain.source == "design.md"
    assert chain.report == "reports/design-review.md"
    assert chain.stale is False
    assert chain.source_mtime == 1000.0
    assert chain.report_mtime == 2000.0

    # Case 2: Stale report (source_mtime > report_mtime, so stale = True)
    source_stale = plan_dir / "outline.md"
    report_stale = reports_dir / "outline-review.md"
    source_stale.write_text("")
    report_stale.write_text("")
    os.utime(source_stale, (5000, 5000))  # newer
    os.utime(report_stale, (3000, 3000))  # older

    vet_status = get_vet_status(plan_dir)
    assert vet_status is not None
    assert len(vet_status.chains) == 2

    stale_chain = next((c for c in vet_status.chains if c.source == "outline.md"), None)
    assert stale_chain is not None
    assert stale_chain.report == "reports/outline-review.md"
    assert stale_chain.stale is True
    assert stale_chain.source_mtime == 5000.0
    assert stale_chain.report_mtime == 3000.0


def test_missing_report_treated_as_stale(tmp_path: Path) -> None:
    """Test missing report file is treated as stale."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()

    # Create source artifact without report file
    (plan_dir / "design.md").write_text("")

    vet_status = get_vet_status(plan_dir)

    assert vet_status is not None
    assert len(vet_status.chains) == 1

    chain = vet_status.chains[0]
    assert chain.stale is True
    assert chain.report is None
    assert chain.report_mtime is None


def test_iterative_review_highest_wins(tmp_path: Path) -> None:
    """Test highest-numbered or highest-mtime review report wins."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()

    # Create source artifact
    (plan_dir / "outline.md").write_text("")

    # Create multiple review reports with iteration numbers
    outline_review = reports_dir / "outline-review.md"
    outline_review_2 = reports_dir / "outline-review-2.md"
    outline_review_3 = reports_dir / "outline-review-3.md"
    outline_review_opus = reports_dir / "outline-review-opus.md"

    # Write files with different mtimes
    outline_review.write_text("")
    os.utime(outline_review, (1000, 1000))

    outline_review_2.write_text("")
    os.utime(outline_review_2, (1500, 1500))

    outline_review_3.write_text("")
    os.utime(outline_review_3, (2000, 2000))  # highest number, should win

    outline_review_opus.write_text("")
    os.utime(outline_review_opus, (1800, 1800))  # variant, but lower mtime than 3

    vet_status = get_vet_status(plan_dir)

    assert vet_status is not None
    assert len(vet_status.chains) == 1

    chain = vet_status.chains[0]
    assert chain.source == "outline.md"
    assert chain.report == "reports/outline-review-3.md"


def test_any_stale_property() -> None:
    """Test VetStatus.any_stale computed property."""
    # All fresh → not stale
    fresh_status = VetStatus(
        chains=[
            VetChain(
                source="design.md", report="reports/design-review.md", stale=False
            ),
            VetChain(
                source="outline.md", report="reports/outline-review.md", stale=False
            ),
        ]
    )
    assert fresh_status.any_stale is False

    # One stale → stale
    mixed_status = VetStatus(
        chains=[
            VetChain(
                source="design.md", report="reports/design-review.md", stale=False
            ),
            VetChain(source="outline.md", report=None, stale=True),
        ]
    )
    assert mixed_status.any_stale is True

    # All stale → stale
    all_stale = VetStatus(
        chains=[
            VetChain(source="design.md", report=None, stale=True),
        ]
    )
    assert all_stale.any_stale is True

    # Empty chains → not stale
    empty_status = VetStatus(chains=[])
    assert empty_status.any_stale is False


def test_dynamic_phase_discovery(tmp_path: Path) -> None:
    """Test vet discovers phases beyond 6 dynamically."""
    plan_dir = tmp_path / "test-plan"
    plan_dir.mkdir()
    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()

    # Create phases 1, 7, 12
    for n in [1, 7, 12]:
        (plan_dir / f"runbook-phase-{n}.md").write_text("")
        report = reports_dir / f"phase-{n}-review.md"
        report.write_text("")
        os.utime(report, (2000, 2000))
        os.utime(plan_dir / f"runbook-phase-{n}.md", (1000, 1000))

    vet_status = get_vet_status(plan_dir)
    assert vet_status is not None
    assert len(vet_status.chains) == 3

    sources = {c.source for c in vet_status.chains}
    expected = {
        "runbook-phase-1.md",
        "runbook-phase-7.md",
        "runbook-phase-12.md",
    }
    assert sources == expected
    assert all(not c.stale for c in vet_status.chains)
