"""Shared worktree utilities."""

import subprocess
from pathlib import Path


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
