"""Contract tests for ``plugin/bin/edify-review-range.sh``.

KD-2 in ``plans/provenance-enforcement-and-routing/outline.md``. Each test
builds a throwaway git repo under ``tmp_path`` and runs the script as a
subprocess **by bare name** — ``plugin/bin`` on ``PATH``, CWD outside the
repo — the same way ``deliverable-review/SKILL.md`` Phase 1 step 2 will
invoke it.
"""

import os
import subprocess
from pathlib import Path

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


def _write_artifact(path: Path, derived_from: str, base: str) -> None:
    """Write an artifact in the prescribed §Provenance shape.

    The shape is the one ``design-content-rules.md`` §Provenance Section
    prescribes for every ``/design`` artifact. ``derived_from`` may itself
    span lines with a leading-space continuation (the real second-pass
    shape below) — this writer interpolates it verbatim, then strips
    trailing whitespace line by line so a value that starts on a
    continuation line leaves no trailing blank on the bullet line, exactly
    as a real artifact is written.
    """
    derived_bullet = "\n".join(
        line.rstrip() for line in f"- **Derived from:** {derived_from}".splitlines()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Outline\n\n"
        "## Provenance\n\n"
        f"{derived_bullet}\n"
        f"- **Base:** `{base}`\n\n"
        "## Requirements\n",
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
