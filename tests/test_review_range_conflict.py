"""Contract tests for ``edify-review-range.sh``'s ``CONFLICT:`` verdict.

See ``tests/review_range_helpers.py`` for the shared fixtures and the
subprocess-invocation contract these tests exercise against.
"""

from pathlib import Path

from .review_range_helpers import (
    _init_repo,
    _run_git,
    _run_review_range,
    _second_pass_derived_from,
    _write_artifact,
)


def test_second_pass_recomputed_base_is_conflict(tmp_path: Path) -> None:
    """A `Base:` later than the prior's emits `CONFLICT:` naming both shas."""
    repo = tmp_path / "repo"
    first = _init_repo(repo)
    second = _run_git(repo, "rev-parse", "HEAD").strip()
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", first)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/prior-job/outline.md"),
        second,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert (
        result.stdout == f"CONFLICT: base {second} != {first} inherited from "
        "plans/prior-job/outline.md\n"
    )
