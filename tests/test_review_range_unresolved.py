"""Contract tests for ``edify-review-range.sh``'s ``UNRESOLVED:`` verdict.

One of five modules split from ``tests/test_review_range.py``, the name
KD-2 records, to keep each module under its line cap.

See ``tests/review_range_helpers.py`` for the shared fixtures and the
subprocess-invocation contract these tests exercise against.
"""

from pathlib import Path

from .review_range_helpers import (
    _init_repo,
    _run_review_range,
    _second_pass_derived_from,
    _write_artifact,
)


def test_unresolvable_base_reported(tmp_path: Path) -> None:
    """A `Base:` of 40 hex chars naming no commit emits `UNRESOLVED: <base>`."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    fake = "0" * 39 + "1"
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(artifact, "none", fake)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout == f"UNRESOLVED: {fake}\n"


def test_unresolvable_prior_base_reported(tmp_path: Path) -> None:
    """A prior `Base:` of 40 hex chars naming no commit emits `UNRESOLVED:`.

    `plugin/bin/edify-review-range.sh:146` validates `$prior_base`
    syntactically (40 hex chars) and never against the repo, so a phantom sha
    reaches the compare at `:151` and, on mismatch, prints
    `CONFLICT: ... != <phantom> inherited from <path>` — presenting a
    nonexistent commit as an inherited base. KD-2 scopes `NO-PRIOR:` to a
    prior that is missing or "carries no full-sha `Base:`", which a phantom
    full sha is not, and scopes `CONFLICT:` to "one of two artifacts is
    wrong", adjudicated between two resolvable bases. What is left is the
    verdict the script already gives its *own* unresolvable `Base:` (`:107`,
    `:115`): `UNRESOLVED: <base>`, carrying the sha that failed to resolve.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    phantom = "f" * 40
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", phantom)
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
    assert result.stdout == f"UNRESOLVED: {phantom}\n"
