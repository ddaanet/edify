"""Contract tests for ``edify-review-range.sh``'s ``NO-PRIOR:`` verdict.

See ``tests/review_range_helpers.py`` for the shared fixtures and the
subprocess-invocation contract these tests exercise against.
"""

from pathlib import Path

import pytest

from .review_range_helpers import (
    _init_repo,
    _run_review_range,
    _second_pass_derived_from,
    _write_artifact,
)


def test_missing_prior_artifact_reported(tmp_path: Path) -> None:
    """A `Derived from:` naming a missing path emits `NO-PRIOR: <path>`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/missing-job/outline.md"),
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout == "NO-PRIOR: plans/missing-job/outline.md\n"


@pytest.mark.parametrize(
    "prior_base",
    [
        pytest.param(None, id="base-absent"),
        pytest.param("abc123", id="base-short"),
    ],
)
def test_prior_without_base_reported(tmp_path: Path, prior_base: str | None) -> None:
    """A prior artifact with no full-sha `Base:` emits `NO-PRIOR: <path>`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", prior_base)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/prior-job/outline.md"),
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout == "NO-PRIOR: plans/prior-job/outline.md\n"
