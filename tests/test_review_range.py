"""Contract tests for ``plugin/bin/edify-review-range.sh``.

KD-2 in ``plans/provenance-enforcement-and-routing/outline.md``. Each test
builds a throwaway git repo under ``tmp_path`` and runs the script as a
subprocess **by bare name** — ``plugin/bin`` on ``PATH``, CWD outside the
repo — the same way ``deliverable-review/SKILL.md`` Phase 1 step 2 will
invoke it.
"""

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = REPO_ROOT / "plugin" / "bin"


def _run_git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` insulated from user and system config; return stdout.

    Failures assert with stderr attached rather than raising a bare
    ``CalledProcessError`` (docs/design.md D-21).
    """
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"
    return result.stdout


def _init_repo(repo: Path) -> str:
    """Init a git repo at ``repo`` with two commits; return the *first* sha.

    Two commits, so that the first commit is not ``HEAD``: a script that
    emitted ``git rev-parse HEAD`` instead of reading ``Base:`` from the
    artifact would pass against a single-commit repo.
    """
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-q", "-m", "seed")
    first = _run_git(repo, "rev-parse", "HEAD").strip()
    (repo / "README.md").write_text("seed\nsecond\n", encoding="utf-8")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-q", "-m", "second")
    return first


def _write_artifact(
    path: Path,
    derived_from: str | None,
    base: str | None,
    base_rationale: str = "",
) -> None:
    """Write an artifact in the prescribed §Provenance shape.

    The shape is the one ``design-content-rules.md`` §Provenance Section
    prescribes for every ``/design`` artifact. ``derived_from`` may itself
    span lines with a leading-space continuation (the real second-pass
    shape below) — this writer interpolates it verbatim, then strips
    trailing whitespace line by line so a value that starts on a
    continuation line leaves no trailing blank on the bullet line, exactly
    as a real artifact is written.

    ``None`` for either field omits that bullet, leaving the ``## Provenance``
    heading in place — the "section present, field missing" shape. Any other
    value is written verbatim, unvalidated (a short sha, say), the same way a
    hand-edited artifact would carry it.

    ``base_rationale`` is appended after the `Base:` value's closing backtick —
    the trailing clause real artifacts write there
    (`plans/provenance-reach-and-sweep/outline.md` §Provenance).
    """
    bullets = ""
    if derived_from is not None:
        bullets += "\n".join(
            line.rstrip()
            for line in f"- **Derived from:** {derived_from}".splitlines()
        )
        bullets += "\n"
    if base is not None:
        bullets += f"- **Base:** `{base}`{base_rationale}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Outline\n\n## Provenance\n\n{bullets}\n## Requirements\n",
        encoding="utf-8",
    )


def _second_pass_derived_from(prior_path: str) -> str:
    """Build a `Derived from:` value in the real wrapped second-pass shape.

    Nothing after the label, the motivating report on the first indented
    continuation line, ``superseding `<prior_path>` `` on the second — the
    shape ``plans/provenance-enforcement-and-routing/outline.md``'s own
    ``## Provenance`` section uses, verbatim.
    """
    return (
        "\n  `plans/prior-job/reports/deliverable-review.md`,\n"
        f"  superseding `{prior_path}`"
    )


def _write_artifact_no_provenance_section(path: Path) -> None:
    """Write an artifact with no `## Provenance` heading at all."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Outline\n\n## Requirements\n", encoding="utf-8")


def _run_review_range(artifact: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Invoke edify-review-range.sh by bare name with plugin/bin on PATH."""
    env = dict(os.environ)
    env["PATH"] = f"{BIN_DIR}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        ["edify-review-range.sh", str(artifact)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
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
        result.stdout
        == f"CONFLICT: base {second} != {first} inherited from "
        "plans/prior-job/outline.md\n"
    )


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


def test_first_pass_none_with_rationale_emits_range(tmp_path: Path) -> None:
    """`Derived from: none — <rationale>`, the tree's idiom, emits `RANGE:`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact, "none — this job originates from the task frame", sha
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
