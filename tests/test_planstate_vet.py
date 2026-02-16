"""Tests for planstate vet module."""

from pathlib import Path

import pytest

from claudeutils.planstate.vet import get_vet_status


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
