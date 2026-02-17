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


def _is_branch_merged(slug: str) -> bool:
    """Return True if slug is an ancestor of HEAD (merge-base --is-ancestor)."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", slug, "HEAD"],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def _classify_branch(slug: str) -> tuple[int, bool]:
    """Classify branch by commit count and focused session marker.

    Returns (commit_count, is_focused) where:
    - commit_count: number of commits between merge-base and branch tip
    - is_focused: True only if count==1 and message is "Focused session for {slug}"

    For orphan branches (no merge-base): returns (0, False)
    """
    try:
        merge_base = _git("merge-base", "HEAD", slug, check=True)
    except subprocess.CalledProcessError:
        return (0, False)

    count_str = _git("rev-list", "--count", f"{merge_base}..{slug}")
    count = int(count_str)

    is_focused = False
    if count == 1:
        msg = _git("log", "-1", "--format=%s", slug)
        is_focused = msg == f"Focused session for {slug}"

    return (count, is_focused)


def _is_parent_dirty(exclude_path: str | None = None) -> bool:
    """Return True if parent repo has staged/unstaged/untracked changes.

    exclude_path: if given, skip status lines whose path starts with
    Path(exclude_path).name + "/" (used to ignore the worktree container dir
    when it appears as an untracked entry inside the repo).
    """
    output = _git("status", "--porcelain", check=False)
    if not output:
        return False

    exclude_prefix = (Path(exclude_path).name + "/") if exclude_path else None
    for line in output.strip().split("\n"):
        if not line:
            continue
        path = line[3:]
        if exclude_prefix and path.startswith(exclude_prefix):
            continue
        return True
    return False


def _is_submodule_dirty() -> bool:
    """Return True if agent-core is dirty; False if absent or clean."""
    submodule_path = Path("agent-core")
    if not submodule_path.exists():
        return False

    result = subprocess.run(
        ["git", "-C", "agent-core", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def _parse_worktree_list(porcelain: str, main_path: str) -> list[tuple[str, str, str]]:
    """Parse git worktree list --porcelain, exclude main."""
    if not porcelain:
        return []
    lines, entries, i = porcelain.split("\n"), [], 0
    while i < len(lines):
        if not lines[i].startswith("worktree "):
            i += 1
            continue
        path, branch, i = lines[i].split(maxsplit=1)[1], "", i + 1
        while i < len(lines) and lines[i]:
            if lines[i].startswith("branch "):
                branch = lines[i].split(maxsplit=1)[1]
            i += 1
        i += 1
        if path != main_path:
            entries.append((Path(path).name, branch, path))
    return entries


def _get_worktree_path_for_branch(slug: str) -> Path | None:
    """Get the actual worktree path for a branch from git."""
    list_output = _git("worktree", "list", "--porcelain", check=False)
    for line in list_output.split("\n"):
        if line.startswith("worktree "):
            worktree_path = Path(line[len("worktree ") :])
        elif line.startswith("branch ") and worktree_path:
            if line[len("branch ") :] == f"refs/heads/{slug}":
                return worktree_path
            worktree_path = None
    return None


def _probe_registrations(worktree_path: Path) -> tuple[bool, bool]:
    """Check parent and submodule worktree registration."""
    parent_list = _git("worktree", "list", "--porcelain", check=False)
    submodule_list = _git(
        "-C", "agent-core", "worktree", "list", "--porcelain", check=False
    )
    parent_reg = str(worktree_path) in parent_list
    submodule_reg = str(worktree_path / "agent-core") in submodule_list
    return parent_reg, submodule_reg


def _remove_worktrees(
    worktree_path: Path,
    parent_registered: bool,  # noqa: FBT001
    submodule_registered: bool,  # noqa: FBT001
) -> None:
    """Remove worktrees (submodule first, force flag)."""
    if submodule_registered:
        _git(
            "-C",
            "agent-core",
            "worktree",
            "remove",
            "--force",
            str(worktree_path / "agent-core"),
        )
    if parent_registered:
        _git("worktree", "remove", "--force", str(worktree_path))


def _is_merge_commit() -> bool:
    """Return True if HEAD has 2+ parents."""
    parts = _git("rev-list", "--parents", "-n", "1", "HEAD").split()
    return len(parts) >= 3
