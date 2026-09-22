"""Contract tests for ``edify-review-range.sh``'s ``RANGE:`` verdict.

One of five modules split from ``tests/test_review_range.py``, the name
KD-2 records, to keep each module under its line cap.

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


def test_first_pass_emits_range(tmp_path: Path) -> None:
    """Artifact with `Derived from: none` emits `RANGE: <base>..HEAD`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(artifact, "none", sha)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_base_with_trailing_rationale_emits_range(tmp_path: Path) -> None:
    """A `Base:` carrying a trailing rationale clause still emits `RANGE:`.

    The sibling of the `Derived from: none — <rationale>` case below: the script
    documents a trailing clause on *either* field, and the tree's real artifacts
    write one on `Base:`.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        "none",
        sha,
        base_rationale=" — copied verbatim from the superseded outline, "
        "**not** recomputed.",
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_second_pass_matching_base_emits_range(tmp_path: Path) -> None:
    """A prior artifact with the same `Base:` emits `RANGE: <base>..HEAD`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", sha)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/prior-job/outline.md"),
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_prior_base_uppercase_same_commit_emits_range(tmp_path: Path) -> None:
    """An uppercase-hex prior `Base:` on the same commit still emits `RANGE:`.

    `plugin/bin/edify-review-range.sh:151` compares `$resolved_base` (git-
    canonical lowercase) against `$prior_base`, the prior artifact's raw text —
    case-preserved and never canonicalised. Two artifacts naming the identical
    commit, one of them uppercase, must inherit cleanly: KD-2 reserves
    `CONFLICT:` for "one of two artifacts is wrong", and a case difference alone
    is neither artifact being wrong.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", sha.upper())
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/prior-job/outline.md"),
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_wrapped_derived_from_with_spaced_path(tmp_path: Path) -> None:
    """A wrapped `Derived from:` naming a spaced prior path resolves the range.

    The run helper already invokes from a CWD outside the repo with the
    artifact given as an absolute path (`_run_review_range`) — this test
    adds nothing new for that; it holds because the existing helper is
    reused unchanged.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    prior = repo / "plans" / "my job" / "outline.md"
    _write_artifact(prior, "none", sha)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/my job/outline.md"),
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_one_hop_only_ignores_grandprior_mismatch(tmp_path: Path) -> None:
    """A→B→C: C's range depends only on B's `Base:`, never on A's.

    KD-2's "one hop only" — each artifact in a chain was already compared
    against its own predecessor at its own review, so a later artifact compares
    only its immediate prior's `Base:`, never chases through to an earlier
    ancestor. Here B's `Base:` (the repo's second commit) differs from A's (the
    first) — a stale fact from B's own prior review, already settled there — and
    C's `Base:` matches B's. A two-hop implementation that chased through B to A
    would see C's base diverge from A's and report `CONFLICT:`; the one-hop
    contract must emit `RANGE:` instead, using only B's `Base:`.
    """
    repo = tmp_path / "repo"
    first = _init_repo(repo)
    second = _run_git(repo, "rev-parse", "HEAD").strip()
    a = repo / "plans" / "job-a" / "outline.md"
    _write_artifact(a, "none", first)
    b = repo / "plans" / "job-b" / "outline.md"
    _write_artifact(b, _second_pass_derived_from("plans/job-a/outline.md"), second)
    c = repo / "plans" / "job-c" / "outline.md"
    _write_artifact(c, _second_pass_derived_from("plans/job-b/outline.md"), second)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(c, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {second}..HEAD\n"


def test_first_pass_none_with_rationale_emits_range(tmp_path: Path) -> None:
    """`Derived from: none — <rationale>`, the tree's idiom, emits `RANGE:`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(artifact, "none — this job originates from the task frame", sha)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_backticked_none_emits_range(tmp_path: Path) -> None:
    """`` - **Derived from:** `none` `` resolves exactly like plain `none`.

    `plugin/bin/edify-review-range.sh:64` strips backticks from the `Base:`
    value only; the `derived_from` comparison against the literal `none`
    (`:119`) never sees backticks stripped, so the backticked form falls
    through to `NO-PROVENANCE:` — telling the operator the section is
    missing rather than that a value is over-quoted. The prescribed shape
    (`design-content-rules.md:139`) backticks every path, so backticking
    `none` for symmetry is a plausible slip.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(artifact, "`none`", sha)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"


def test_crlf_artifact_emits_range(tmp_path: Path) -> None:
    r"""An artifact written with CRLF line endings emits `RANGE:` unchanged.

    `plugin/bin/edify-review-range.sh:40` strips only `[ \\t]+$` from each raw
    line, so the `\\r` of every CRLF ending survives into the parsed values.
    The first casualty is `Base:`, which the script reports as
    `UNRESOLVED: <sha>\\r` — the operator is told the base cannot be resolved
    and shown a sha that resolves fine. `Derived from:` is the second: its
    value reads `none\\r`, which fails the `none` test at `:119` and would
    fall through to `NO-PROVENANCE:`. The whole artifact is written CRLF, not
    just the `Base:` line, so only a per-line fix at `:40` satisfies this —
    stripping `\\r` from the `Base:` value alone leaves the second casualty
    in place and merely swaps one wrong verdict for another.
    """
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(artifact, "none", sha)
    artifact.write_bytes(
        artifact.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8")
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
