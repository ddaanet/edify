"""Shared fixtures for ``plugin/bin/triage-feedback.sh`` tests.

Each test builds a throwaway git repo under ``tmp_path`` and runs the script
by absolute path with CWD at the repo root, following the subprocess-run
pattern in ``tests/review_range_helpers.py``. The script takes the job name
only: its base is the parent of the commit that first added a
``plans/<job>/reports/item-*`` report (D-88), so every fixture commits one.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugin" / "bin" / "triage-feedback.sh"
JOB = "j"


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


def _init_repo(repo: Path) -> None:
    """Init a git repo at ``repo`` with a seed commit, outside the run."""
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-q", "-m", "seed")


def _commit(repo: Path, message: str, files: dict[str, str]) -> None:
    """Write and commit ``files``, a map of repo-relative path to content."""
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _run_git(repo, "add", "--", *files)
    _run_git(repo, "commit", "-q", "-m", message)


def _commit_item_report(repo: Path, files: dict[str, str] | None = None) -> None:
    """Commit the run's first item report together with ``files``.

    The commit's parent is the run base, so everything committed before this
    call is outside the run.
    """
    run_files = {f"plans/{JOB}/reports/item-1-1.md": "item report\n"}
    run_files.update(files or {})
    _commit(repo, "run: item 1.1", run_files)


def _run_triage(job: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run triage-feedback.sh by absolute path with CWD at the repo root."""
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        [str(SCRIPT), job],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _triage_lines(job: str, cwd: Path) -> list[str]:
    """Run triage-feedback.sh; return its stdout lines, asserting exit 0."""
    result = _run_triage(job, cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def _def_edits_pending(repo: Path) -> None:
    """Leave a ``def`` uncommitted in two tracked files.

    The run commit tracks ``module.py`` and ``other.py`` holding no
    definition. ``module.py`` then carries the ``def`` unstaged, ``other.py``
    staged.
    """
    _init_repo(repo)
    _commit_item_report(repo, {"module.py": "x = 1\n", "other.py": "y = 2\n"})
    (repo / "module.py").write_text("x = 1\ndef foo():\n    pass\n", encoding="utf-8")
    (repo / "other.py").write_text("y = 2\ndef bar():\n    pass\n", encoding="utf-8")
    _run_git(repo, "add", "other.py")
