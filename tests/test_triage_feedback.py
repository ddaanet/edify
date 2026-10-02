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


def test_files_changed_counts_committed_changes_only(tmp_path: Path) -> None:
    """Files changed counts the committed diff from the baseline to HEAD only.

    Every file is tracked at the baseline, so each later edit is a diff:
    ``git diff`` never lists an untracked path, which would drop the
    uncommitted files for the wrong reason. Two commits follow the baseline --
    ``a.txt``, then ``d.txt`` and ``e.txt`` -- and ``b.txt`` is left modified
    unstaged and ``c.txt`` modified and staged (KD-6). The answer, 3, differs
    from every neighbouring range: the last commit alone reads 2, the index
    against HEAD 1, the working tree against HEAD 2, the baseline against the
    index 4 and against the working tree 5.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)

    names = ("a.txt", "b.txt", "c.txt", "d.txt", "e.txt")
    for name in names:
        (repo / name).write_text("original\n", encoding="utf-8")
    _run_git(repo, "add", *names)
    _run_git(repo, "commit", "-q", "-m", "track files")
    baseline = _run_git(repo, "rev-parse", "HEAD").strip()

    (repo / "a.txt").write_text("changed\n", encoding="utf-8")
    _run_git(repo, "add", "a.txt")
    _run_git(repo, "commit", "-q", "-m", "change a")

    (repo / "d.txt").write_text("changed\n", encoding="utf-8")
    (repo / "e.txt").write_text("changed\n", encoding="utf-8")
    _run_git(repo, "add", "d.txt", "e.txt")
    _run_git(repo, "commit", "-q", "-m", "change d and e")

    (repo / "b.txt").write_text("modified, uncommitted\n", encoding="utf-8")

    (repo / "c.txt").write_text("staged, uncommitted\n", encoding="utf-8")
    _run_git(repo, "add", "c.txt")

    lines = _triage_lines("job", baseline, repo)
    assert "- Files changed: 3" in lines, "\n".join(lines)


def test_uncommitted_definition_is_not_behavioral(tmp_path: Path) -> None:
    """Behavioral code reads the committed diff from the baseline to HEAD only.

    Both repos come from ``_def_edits_pending``: after the baseline a commit
    tracks ``module.py`` and ``other.py`` holding no definition, then each
    file picks up a ``def`` line, ``module.py`` unstaged and ``other.py``
    staged (KD-6). The negative leaves both edits uncommitted, so it reads
    ``no`` only once neither the working tree nor the index reaches the diff.

    The positive differs only in committing those same edits, then a
    plain-text commit on top, and must read ``yes``: an implementation whose
    regex misses the ``def`` lines, that diffs only the uncommitted state, or
    that diffs only the last commit reads ``no`` there. It runs second so the
    negative's result stays its own.
    """
    repo = tmp_path / "repo"
    baseline = _def_edits_pending(repo)

    lines = _triage_lines("job", baseline, repo)
    assert "- Behavioral code: no" in lines, "\n".join(lines)

    positive_repo = tmp_path / "positive"
    positive_baseline = _def_edits_pending(positive_repo)
    _run_git(positive_repo, "commit", "-q", "-a", "-m", "commit defs")
    (positive_repo / "notes.txt").write_text("plain text\n", encoding="utf-8")
    _run_git(positive_repo, "add", "notes.txt")
    _run_git(positive_repo, "commit", "-q", "-m", "add notes")

    lines = _triage_lines("job", positive_baseline, positive_repo)
    assert "- Behavioral code: yes" in lines, "\n".join(lines)


def _def_edits_pending(repo: Path) -> str:
    """Leave a ``def`` uncommitted in two tracked files; return the baseline.

    ``module.py`` carries it unstaged, ``other.py`` staged.
    """
    baseline = _init_repo(repo)
    (repo / "module.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "other.py").write_text("y = 2\n", encoding="utf-8")
    _run_git(repo, "add", "module.py", "other.py")
    _run_git(repo, "commit", "-q", "-m", "add plain text")
    (repo / "module.py").write_text("x = 1\ndef foo():\n    pass\n", encoding="utf-8")
    (repo / "other.py").write_text("y = 2\ndef bar():\n    pass\n", encoding="utf-8")
    _run_git(repo, "add", "other.py")
    return baseline
