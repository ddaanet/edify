"""Shared fixtures for ``plugin/skills/build/scripts/verify-step.sh`` tests.

Each test builds a throwaway git repo under ``tmp_path`` and runs the script
by absolute path with CWD at the repo root, following the subprocess-run
pattern in ``tests/triage_feedback_helpers.py``.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugin" / "skills" / "build" / "scripts" / "verify-step.sh"


def _run_git(repo: Path, *args: str, returncode: int = 0) -> str:
    """Run git in ``repo`` insulated from user and system config; return stdout.

    Failures assert with stderr attached rather than raising a bare
    ``CalledProcessError`` (docs/references/testing.md D-21). ``returncode``
    is the exit expected, for a call that fails on purpose.
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
    assert result.returncode == returncode, (
        f"git {args}: {result.stdout}{result.stderr}"
    )
    return result.stdout


def _status(repo: Path) -> str:
    """Return the repo's porcelain status, exploding untracked directories."""
    return _run_git(repo, "status", "--porcelain", "--untracked-files=all")


def _init_repo(tmp_path: Path) -> Path:
    """Init a repo under ``tmp_path``, seeded with a handoff file; return it."""
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    claude_dir = repo / ".claude"
    claude_dir.mkdir()
    (claude_dir / "handoff-task.md").write_text("original\n", encoding="utf-8")
    _run_git(repo, "add", "README.md", ".claude/handoff-task.md")
    _run_git(repo, "commit", "-q", "-m", "seed")
    return repo


def _stub_just(tmp_path: Path) -> tuple[Path, Path]:
    """Write a ``just`` stub under ``tmp_path``; return ``(bin_dir, marker)``.

    The stub appends its args to ``marker``, which exists only once ``just``
    has been invoked.
    """
    bin_dir = tmp_path / "bin"
    marker = tmp_path / "just-invocations"
    bin_dir.mkdir(parents=True, exist_ok=True)
    stub = bin_dir / "just"
    stub.write_text(f'#!/bin/sh\necho "$*" >> "{marker}"\nexit 0\n', encoding="utf-8")
    stub.chmod(0o755)
    return bin_dir, marker


def _run_script(
    repo: Path,
    bin_dir: Path,
    *,
    extra_env: dict[str, str] | None = None,
    script: Path = SCRIPT,
) -> subprocess.CompletedProcess[str]:
    """Run ``script`` by absolute path with CWD at ``repo``.

    ``script`` defaults to the repo's ``verify-step.sh``; a test passes a copy
    to run it beside a doctored ``exempt-paths.sh``.

    ``bin_dir`` is prepended to ``PATH`` so the stub ``just`` is found first;
    git config is insulated the same way as ``_run_git``. ``extra_env`` is
    applied last, so a ``PATH`` entry there replaces the prepended one
    outright instead of merely prefixing it.
    """
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(script)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _assert_dirty(result: subprocess.CompletedProcess[str], *lines: str) -> None:
    """Assert exit 1 and a DIRTY verdict listing exactly ``lines``, in order."""
    assert result.returncode == 1, result.stdout + result.stderr
    expected = ["DIRTY: uncommitted changes", *lines]
    assert result.stdout.splitlines() == expected, result.stdout
