"""Contract tests for ``plugin/bin/triage-feedback.sh``.

KD-3 in ``plans/build-defects/outline.md``: ``reports_count`` must exclude
review-gate and closing-review reports (``review.md``, ``review-*.md``,
``final-review.md``) since the script already reports review presence
separately, in ``review_artifact``.

Each test builds a throwaway git repo under ``tmp_path`` and runs the script
by absolute path with CWD at the repo root, following the subprocess-run
pattern in ``tests/review_range_helpers.py``.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugin" / "bin" / "triage-feedback.sh"


def _run_git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` insulated from user and system config; return stdout.

    Failures assert with stderr attached rather than raising a bare
    ``CalledProcessError`` (docs/references/testing.md D-21).
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
    """Init a git repo at ``repo`` with a baseline commit; return its sha."""
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-q", "-m", "seed")
    return _run_git(repo, "rev-parse", "HEAD").strip()


def _triage_lines(job_dir: str, baseline: str, cwd: Path) -> list[str]:
    """Run triage-feedback.sh by absolute path with CWD at the repo root.

    Return its stdout lines, asserting exit 0 with the output attached.
    """
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    result = subprocess.run(
        [str(SCRIPT), job_dir, baseline],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def test_simple_with_review_reports_matches(tmp_path: Path) -> None:
    """A Simple job whose only reports are review-gate ones matches.

    ``reports/`` holds what a reviewed Simple run leaves — ``review.md``,
    ``review-skill.md``, ``review-skip.md`` and the closing review's
    ``final-review.md`` together, so every KD-3 exclusion pattern has a file:
    a fix excluding only some of ``review.md``, ``review-*.md`` and
    ``final-review.md`` leaves the count above zero and the verdict at
    ``underclassified``.

    Adding one slice code-review report then must count as 1: a fix that stops
    counting reports altogether, or excludes every name containing
    ``review``, reads 0 there.
    """
    repo = tmp_path / "repo"
    baseline = _init_repo(repo)

    # A plain text file with no definitions: `Behavioral code: no` holds, so
    # the verdict turns only on the report count.
    (repo / "notes.txt").write_text("just plain text, no code here\n", encoding="utf-8")
    _run_git(repo, "add", "notes.txt")
    _run_git(repo, "commit", "-q", "-m", "add notes")

    job_dir = "job"
    plan_dir = repo / "plans" / job_dir
    plan_dir.mkdir(parents=True)
    (plan_dir / "classification.md").write_text(
        "# Classification — job\n\n- **Classification:** Simple\n",
        encoding="utf-8",
    )

    reports_dir = plan_dir / "reports"
    reports_dir.mkdir()
    (reports_dir / "review.md").write_text("reviewed\n", encoding="utf-8")
    (reports_dir / "review-skill.md").write_text("reviewed\n", encoding="utf-8")
    (reports_dir / "review-skip.md").write_text("skipped\n", encoding="utf-8")
    (reports_dir / "final-review.md").write_text("closing review\n", encoding="utf-8")

    lines = _triage_lines(job_dir, baseline, repo)
    assert "- Behavioral code: no" in lines, "\n".join(lines)
    assert "- Reports: 0" in lines, "\n".join(lines)
    assert lines[lines.index("## Verdict") + 1] == "match", "\n".join(lines)

    (reports_dir / "item-1-1-s1-code-review.md").write_text(
        "slice code review\n", encoding="utf-8"
    )

    lines = _triage_lines(job_dir, baseline, repo)
    assert "- Behavioral code: no" in lines, "\n".join(lines)
    assert "- Reports: 1" in lines, "\n".join(lines)
    assert lines[lines.index("## Verdict") + 1] == "underclassified", "\n".join(lines)
