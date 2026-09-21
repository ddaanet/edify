"""Contract tests for ``edify-review-range.sh``'s ``NO-PROVENANCE:`` verdict.

See ``tests/review_range_helpers.py`` for the shared fixtures and the
subprocess-invocation contract these tests exercise against.
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from .review_range_helpers import (
    _init_repo,
    _run_review_range,
    _write_artifact,
    _write_artifact_no_provenance_section,
)


def test_derived_from_naming_only_a_report_reported(tmp_path: Path) -> None:
    """A `Derived from:` naming no prior artifact emits `NO-PROVENANCE:`.

    Neither `none` nor a `superseding <path>` clause — the "names only the
    motivating report" shape. The script has no prior to compare against and
    no licence to recompute, so it falls through to `NO-PROVENANCE:`.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        "`plans/prior-job/reports/deliverable-review.md`",
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout == "NO-PROVENANCE:\n"


@pytest.mark.parametrize(
    "write_artifact",
    [
        pytest.param(_write_artifact_no_provenance_section, id="no-section"),
        pytest.param(
            lambda path: _write_artifact(path, "none", None),
            id="only-derived-from",
        ),
        pytest.param(
            lambda path: _write_artifact(path, None, "0" * 40),
            id="only-base",
        ),
    ],
)
def test_missing_provenance_reported(
    tmp_path: Path, write_artifact: Callable[[Path], None]
) -> None:
    """No section, or one missing either field, emits `NO-PROVENANCE:`."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    write_artifact(artifact)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout == "NO-PROVENANCE:\n"
