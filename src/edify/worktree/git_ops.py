"""Git and worktree operations."""

import os
import subprocess
import tempfile
from pathlib import Path

from edify.git import _git, _is_dirty, _is_submodule_dirty  # noqa: F401


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
        ["git", "merge-base", "--is-ancestor", slug, "HEAD", "--"],
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
        merge_base = _git("merge-base", "HEAD", slug, "--", check=True)
    except subprocess.CalledProcessError:
        return (0, False)

    count_str = _git("rev-list", "--count", f"{merge_base}..{slug}")
    count = int(count_str)

    is_focused = False
    if count == 1:
        msg = _git("log", "-1", "--format=%s", slug)
        is_focused = msg == f"Focused session for {slug}"

    return (count, is_focused)


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
        "-C", "plugin", "worktree", "list", "--porcelain", check=False
    )
    parent_reg = str(worktree_path) in parent_list
    submodule_reg = str(worktree_path / "plugin") in submodule_list
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
            "plugin",
            "worktree",
            "remove",
            "--force",
            str(worktree_path / "plugin"),
        )
    if parent_registered:
        _git("worktree", "remove", "--force", str(worktree_path))


def _is_merge_commit() -> bool:
    """Return True if HEAD has 2+ parents."""
    parts = _git("rev-list", "--parents", "-n", "1", "HEAD", "--").split()
    return len(parts) >= 3


def _is_merge_of(slug: str) -> bool:
    """Return True if HEAD is a merge commit with slug's branch as a parent."""
    parts = _git("rev-list", "--parents", "-n", "1", "HEAD", "--").split()
    if len(parts) < 3:
        return False
    branch_sha = _git(
        "rev-parse", "--verify", f"refs/heads/{slug}", check=False
    ).strip()
    if not branch_sha:
        return False
    return branch_sha in parts[1:]


def _create_session_commit(slug: str, base: str, session: str) -> str:
    """Create commit with session.md from file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": tmp.name}
    try:
        _git("read-tree", _git("rev-parse", f"{base}^{{tree}}"), env=env)
        content = Path(session).read_text()
        blob = _git("hash-object", "-w", "--stdin", input_data=content)
        _git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{blob},agents/session.md",
            env=env,
        )
        return _git(
            "commit-tree",
            _git("write-tree", env=env),
            "-p",
            base,
            "-m",
            f"Focused session for {slug}",
        )
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def _create_submodule_worktree(
    project_root: str, worktree_path: Path, slug: str
) -> None:
    """Create plugin submodule worktree if exists."""
    agent_core = Path(project_root) / "plugin"
    if not agent_core.exists() or not (agent_core / ".git").exists():
        return

    try:
        _git("-C", str(agent_core), "rev-parse", "--verify", slug)
        flag = []
    except subprocess.CalledProcessError:
        flag = ["-b"]
    _git(
        "-C",
        str(agent_core),
        "worktree",
        "add",
        str(worktree_path / "plugin"),
        *flag,
        slug,
    )


def _delete_submodule_branch(slug: str) -> str | None:
    """Delete branch in plugin submodule if it exists.

    Returns a warning message string if deletion failed unexpectedly, None
    otherwise.
    """
    agent_core = Path("plugin")
    if not agent_core.exists() or not (agent_core / ".git").exists():
        return None
    r = subprocess.run(
        ["git", "-C", "plugin", "branch", "-D", slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0 and "not found" not in r.stderr.lower():
        return f"Submodule branch {slug} deletion failed: {r.stderr.strip()}"
    return None
