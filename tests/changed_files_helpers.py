"""Shared fixtures for ``plugin/skills/build/scripts/changed-files.sh`` tests.

D-88, D-89 and D-90 in ``docs/references/build-run-state.md``. Each test
builds a throwaway git repo under ``tmp_path`` and runs the script by
absolute path with CWD at the repo root, following the ``_init_repo`` pattern in
``tests/verify_step_helpers.py``.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugin" / "skills" / "build" / "scripts" / "changed-files.sh"


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


def _init_repo(tmp_path: Path) -> Path:
    """Init a repo under ``tmp_path``, seeded with ``README.md`` and ``b.txt``.

    ``b.txt`` is seeded here, before the run's first commit, so a later
    run commit can change (not add) it.
    """
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    (repo / "b.txt").write_text("base\n", encoding="utf-8")
    _run_git(repo, "add", "README.md", "b.txt")
    _run_git(repo, "commit", "-q", "-m", "seed")
    return repo


def _run_script(
    repo: Path,
    *args: str,
    script: Path = SCRIPT,
    path_prepend: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run ``script`` by absolute path with CWD at ``repo``.

    ``script`` defaults to the repo's ``changed-files.sh``; a test passes a
    copy to run it beside a doctored ``exempt-paths.sh``. ``path_prepend``
    puts a directory, such as one holding a ``git`` shim, ahead on ``PATH``.
    """
    env = dict(os.environ)
    if path_prepend is not None:
        env["PATH"] = f"{path_prepend}{os.pathsep}{env['PATH']}"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        [str(script), *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _commit(repo: Path, message: str, files: dict[str, str]) -> str:
    """Write and commit ``files``; return the new commit's sha.

    ``files`` maps a repo-relative path to its content.
    """
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _run_git(repo, "add", "--", *files)
    _run_git(repo, "commit", "-q", "-m", message)
    return _run_git(repo, "rev-parse", "HEAD").strip()
