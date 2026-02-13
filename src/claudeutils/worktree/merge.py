"""Worktree merge operations."""

import subprocess
from pathlib import Path

import click


def _git(
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
) -> str:
    r = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
        env=env,
        input=input_data,
    )
    return r.stdout.strip()


def _check_clean_for_merge(
    path: Path | None = None,
    exempt_paths: set[str] | None = None,
    label: str = "main",
) -> None:
    """Verify clean tree for merge.

    Args:
        path: Directory to check (None = current directory)
        exempt_paths: Paths to exempt from dirty check (None = strict mode)
        label: Location label for error messages
    """
    parent_cmd = ["-C", str(path)] if path else []
    parent_cmd.extend(["status", "--porcelain", "--untracked-files=no"])
    parent = _git(*parent_cmd, check=False)

    if exempt_paths:
        dirty = [
            line
            for line in parent.split("\n")
            if line and not any(p in line for p in exempt_paths)
        ]
    else:
        dirty = [line for line in parent.split("\n") if line.strip()]

    if dirty:
        suffix = ": uncommitted changes would be lost" if not exempt_paths else ""
        click.echo(f"Clean tree required for merge ({label}{suffix})")
        raise SystemExit(1)

    submodule_path = (path / "agent-core") if path else Path("agent-core")
    if not (submodule_path.exists() and (submodule_path / ".git").exists()):
        return
    submodule = _git(
        "-C",
        str(submodule_path),
        "status",
        "--porcelain",
        "--untracked-files=no",
        check=False,
    )
    if submodule.strip():
        click.echo(f"Clean tree required for merge ({label} submodule)")
        raise SystemExit(1)


def wt_path(slug: str, create_container: bool = False) -> Path:  # noqa: FBT001,FBT002
    """Worktree path in sibling -wt container."""
    if not slug or not slug.strip():
        msg = "slug must not be empty or whitespace"
        raise ValueError(msg)
    current_path = Path.cwd()
    parent_name = current_path.parent.name
    container_path = (
        current_path.parent
        if parent_name.endswith("-wt")
        else current_path.parent / f"{current_path.name}-wt"
    )
    if create_container and not parent_name.endswith("-wt"):
        container_path.mkdir(parents=True, exist_ok=True)
    return container_path / slug


def merge(slug: str) -> None:
    """Prepare for merge: verify OURS and THEIRS clean tree."""
    _check_clean_for_merge(
        exempt_paths={
            "agents/session.md",
            "agents/jobs.md",
            "agents/learnings.md",
            "agent-core",
        }
    )
    _check_clean_for_merge(path=wt_path(slug), label="worktree")
