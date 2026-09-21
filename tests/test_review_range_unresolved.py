"""Contract tests for ``edify-review-range.sh``'s ``UNRESOLVED:`` verdict.

See ``tests/review_range_helpers.py`` for the shared fixtures and the
subprocess-invocation contract these tests exercise against.
"""

from pathlib import Path

from .review_range_helpers import _init_repo, _run_review_range, _write_artifact


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
