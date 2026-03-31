"""Shared git helpers for edify subcommands."""

import subprocess
from pathlib import Path
from typing import Never

import click


def _git(
    *args: str,
    check: bool = True,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
) -> str:
    """Run git command and return stripped stdout.

    Warning: strips leading whitespace, destroying porcelain XY format.
    Do not use for ``git status --porcelain`` — use raw subprocess instead.
    """
    r = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
        env=env,
        input=input_data,
    )
    return r.stdout.strip()


def _git_ok(*args: str) -> bool:
    """Return True if the git command exits with code 0."""
    result = subprocess.run(["git", *args], check=False, capture_output=True)
    return result.returncode == 0


def _fail(msg: str, code: int = 1) -> Never:
    """Print msg to stdout and exit with code.

    Return type Never for type checkers.
    """
    click.echo(msg)
    raise SystemExit(code)


def discover_submodules(cwd: Path | None = None) -> list[str]:
    """Return list of submodule paths from `git submodule status`.

    Each output line: [space/+/-] <hash> <path> [(<describe>)]
    Returns empty list if no submodules or git command fails.
    """
    result = subprocess.run(
        ["git", "submodule", "status"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    paths = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        # Format: [+-U ] <hash> <path> [(<describe>)]
        # Strip the leading status character and hash to get path
        parts = line.strip().split()
        if len(parts) >= 2:
            paths.append(parts[1])
    return paths


def _is_submodule_dirty(path: str) -> bool:
    """Return True if submodule at path is dirty; False if absent or clean."""
    submodule_path = Path(path)
    if not submodule_path.exists():
        return False

    result = subprocess.run(
        ["git", "-C", str(submodule_path), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def git_status(repo_dir: str | None = None) -> str:
    """Return raw `git status --porcelain` output (empty string if clean).

    repo_dir: if given, run git in that directory via -C flag.
    """
    args = ["status", "--porcelain"]
    if repo_dir:
        args = ["-C", repo_dir, *args]
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.rstrip("\n")


def git_diff(repo_dir: str | None = None) -> str:
    """Return combined staged + unstaged diff output (empty string if none).

    Runs `git diff HEAD` to capture all changes relative to HEAD,
    which covers both staged and unstaged modifications.

    repo_dir: if given, run git in that directory via -C flag.
    """
    args = ["diff", "HEAD"]
    if repo_dir:
        args = ["-C", repo_dir, *args]
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _is_dirty(exclude_path: str | None = None) -> bool:
    """Return True if repo has staged/unstaged/untracked changes.

    exclude_path: if given, skip status lines whose path starts with
    Path(exclude_path).name + "/" (used to ignore the worktree container dir
    when it appears as an untracked entry inside the repo).
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.rstrip("\n")
    if not output:
        return False

    exclude_prefix = (Path(exclude_path).name + "/") if exclude_path else None
    for line in output.split("\n"):
        if not line:
            continue
        path = line[3:]
        if exclude_prefix and path.startswith(exclude_prefix):
            continue
        return True
    return False
