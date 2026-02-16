"""Worktree CLI."""

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import click

from claudeutils.validation.tasks import validate_task_name_format
from claudeutils.worktree.merge import merge as merge_impl
from claudeutils.worktree.session import (
    extract_task_blocks,
    move_task_to_worktree,
    remove_worktree_task,
)
from claudeutils.worktree.utils import _git, _is_branch_merged, wt_path


def derive_slug(task_name: str) -> str:
    """Task name to slug."""
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)

    # Validate task name format
    format_errors = validate_task_name_format(task_name)
    if format_errors:
        msg = format_errors[0]
        raise ValueError(msg)

    return re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")


def _filter_section(
    content: str, section_name: str, task_name: str, plan_dir: str | None
) -> str:
    """Filter section entries by task_name or plan_dir match."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    if not (match := re.search(pattern, content, re.DOTALL)):
        return ""

    def is_relevant(entry: str) -> bool:
        lo = entry.lower()
        return task_name.lower() in lo or bool(plan_dir and plan_dir.lower() in lo)

    lines = []
    include = False
    for line in match.group(1).split("\n"):
        if line.startswith("- "):
            include = is_relevant(line[2:].strip())
            if include:
                lines.append(line)
        elif include and line.strip():
            lines.append(line)
    return f"## {section_name}\n\n" + "\n".join(lines) + "\n" if lines else ""


def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Filter session.md to task_name with relevant context sections."""
    content = Path(session_md_path).read_text()

    blocks = extract_task_blocks(content, section="Pending Tasks")
    task_block = next((b for b in blocks if b.name == task_name), None)
    if not task_block:
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)

    task_lines_str = "\n".join(task_block.lines)
    plan_dir = (
        m.group(1) if (m := re.search(r"[Pp]lan:\s*(\S+)", task_lines_str)) else None
    )
    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n{task_lines_str}\n"
    )
    for section in ["Blockers / Gotchas", "Reference Files"]:
        if filtered := _filter_section(content, section, task_name, plan_dir):
            result += f"\n{filtered}"
    return result


def add_sandbox_dir(container: str, settings_path: str | Path) -> None:
    """Add container to sandbox additionalDirectories."""
    path = Path(settings_path)
    if path.exists():
        settings = json.loads(path.read_text())
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        settings = {"permissions": {"additionalDirectories": []}}
    dirs = settings.setdefault("permissions", {}).setdefault(
        "additionalDirectories", []
    )
    if container not in dirs:
        dirs.append(container)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False))


def initialize_environment(worktree_path: Path) -> None:
    """Run just setup if just is available."""
    try:
        subprocess.run(["just", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return
    r = subprocess.run(
        ["just", "setup"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        click.echo(f"Warning: just setup failed: {r.stderr}", err=True)


@click.group(name="_worktree")
def worktree() -> None:
    """Worktree commands."""


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


@worktree.command()
def ls() -> None:
    """List worktrees excluding main."""
    main_path = _git("rev-parse", "--show-toplevel")
    porcelain = _git("worktree", "list", "--porcelain")
    for slug, branch, path in _parse_worktree_list(porcelain, main_path):
        click.echo(f"{slug}\t{branch}\t{path}")


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


def _create_parent_worktree(
    worktree_path: Path, slug: str, base: str, session: str
) -> None:
    """Create parent worktree, optionally with session commit."""
    branch_exists = (
        subprocess.run(
            ["git", "rev-parse", "--verify", slug], capture_output=True, check=False
        ).returncode
        == 0
    )
    if branch_exists and session:
        click.echo(f"Warning: branch {slug} exists, ignoring --session", err=True)
        session = ""
    if session:
        _git("branch", slug, _create_session_commit(slug, base, session))
        _git("worktree", "add", str(worktree_path), slug)
    elif branch_exists:
        _git("worktree", "add", str(worktree_path), slug)
    else:
        _git("worktree", "add", str(worktree_path), "-b", slug, base)


def _create_submodule_worktree(
    project_root: str, worktree_path: Path, slug: str
) -> None:
    """Create agent-core submodule worktree if exists."""
    agent_core = Path(project_root) / "agent-core"
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
        str(worktree_path / "agent-core"),
        *flag,
        slug,
    )


def _setup_worktree(
    worktree_path: Path, slug: str, base: str, session: str, task: str
) -> None:
    """Create worktrees, register sandbox, init environment."""
    _create_parent_worktree(worktree_path, slug, base, session)
    _create_submodule_worktree(
        _git("rev-parse", "--show-toplevel"), worktree_path, slug
    )
    add_sandbox_dir(str(worktree_path.parent), ".claude/settings.local.json")
    add_sandbox_dir(
        str(worktree_path.parent), f"{worktree_path}/.claude/settings.local.json"
    )
    initialize_environment(worktree_path)
    click.echo(f"{slug}\t{worktree_path}" if task else str(worktree_path))


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Verify clean tree except session context."""
    parent = _git("status", "--porcelain")
    submodule = _git("-C", "agent-core", "status", "--porcelain", check=False)
    exempt = {"session.md", "jobs.md", "learnings.md"}
    dirty = [
        line
        for line in (parent + submodule).rstrip().split("\n")
        if line
        and not (
            len(tokens := line.split()) >= 2
            and tokens[-1].startswith("agents/")
            and Path(tokens[-1]).name in exempt
        )
    ]
    if dirty:
        click.echo("\n".join(dirty))
        raise SystemExit(1)


@worktree.command()
@click.argument("slug", required=False)
@click.option("--base", default="HEAD")
@click.option("--session", default="")
@click.option("--task", default="")
@click.option("--session-md", default="agents/session.md")
def new(slug: str | None, base: str, session: str, task: str, session_md: str) -> None:
    """Create worktree in sibling container."""
    if task and slug:
        raise click.UsageError("slug and --task are mutually exclusive")  # noqa: TRY003
    if not task and not slug:
        raise click.UsageError("either slug or --task is required")  # noqa: TRY003
    temp_session_file = None
    try:
        if task:
            slug = derive_slug(task)
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
                f.write(focus_session(task, session_md))
                temp_session_file = session = f.name
        assert slug is not None
        if (path := wt_path(slug, create_container=True)).exists():
            click.echo(f"Error: existing directory {path}", err=True)
            raise SystemExit(1)
        _setup_worktree(path, slug, base, session, task)
        if task:
            session_md_path = Path(session_md)
            if not session_md_path.exists():
                click.echo(f"Error: session.md not found at {session_md}", err=True)
                raise SystemExit(1)
            move_task_to_worktree(session_md_path, task, slug)
    finally:
        if temp_session_file:
            Path(temp_session_file).unlink(missing_ok=True)


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files, commit with stdin message."""
    _git("add", *list(files))
    try:
        _git("diff", "--quiet", "--cached")
    except subprocess.CalledProcessError:
        click.echo(_git("commit", "-m", click.get_text_stream("stdin").read()))


def _get_worktree_path_for_branch(slug: str) -> Path | None:
    """Get the actual worktree path for a branch from git."""
    list_output = _git("worktree", "list", "--porcelain", check=False)
    lines = list_output.split("\n")

    worktree_path = None
    for i, line in enumerate(lines):
        if line.startswith("worktree "):
            worktree_path = Path(line[len("worktree ") :])
        elif line.startswith("branch ") and worktree_path:
            branch_ref = line[len("branch ") :]
            if branch_ref == f"refs/heads/{slug}":
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


@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Merge worktree branch: validate, resolve submodule, merge parent."""
    merge_impl(slug)


@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove worktree and its branch."""
    # Guard: refuse removal of unmerged real history
    branch_exists = False
    removal_type = None  # "merged" or "focused"
    branch_check = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if branch_check.returncode == 0:
        branch_exists = True
        # Branch exists - check if merged
        is_merged = _is_branch_merged(slug)
        if is_merged:
            removal_type = "merged"
        else:
            # Not merged - check if it's just the focused-session marker
            count, is_focused = _classify_branch(slug)
            if count == 1 and is_focused:
                # Focused-session-only - allow removal with force
                removal_type = "focused"
            else:
                # Real history or orphan - refuse removal
                if count == 0:
                    click.echo(
                        f"Branch {slug} is orphaned (no common ancestor). Merge first.",
                        err=True,
                    )
                else:
                    click.echo(
                        f"Branch {slug} has {count} unmerged commit(s). Merge first.",
                        err=True,
                    )
                raise click.Abort()

    # Get actual worktree path from git, fall back to wt_path() if not found
    worktree_path = _get_worktree_path_for_branch(slug)
    if worktree_path is None:
        worktree_path = wt_path(slug)

    parent_reg, submodule_reg = _probe_registrations(worktree_path)

    if worktree_path.exists():
        status = _git("-C", str(worktree_path), "status", "--porcelain", check=False)
        if status:
            count = len(status.strip().split("\n"))
            click.echo(f"Warning: worktree has {count} uncommitted files")

    session_md_path = Path("agents/session.md")
    if session_md_path.exists():
        remove_worktree_task(session_md_path, slug, slug)

    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)

    if worktree_path.exists():
        shutil.rmtree(worktree_path)

    _git("worktree", "prune")

    container = worktree_path.parent
    if container.exists() and not list(container.iterdir()):
        container.rmdir()

    if branch_exists:
        # Choose deletion flag based on removal type
        if removal_type == "focused":
            # Force delete for focused-session-only branches
            delete_flag = "-D"
        else:
            # Safe delete for merged branches
            delete_flag = "-d"

        r = subprocess.run(
            ["git", "branch", delete_flag, slug],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode != 0 and "not found" not in r.stderr.lower():
            click.echo(f"Branch {slug} deletion failed: {r.stderr.strip()}", err=True)

    # Output appropriate success message
    if removal_type == "merged":
        click.echo(f"Removed {slug}")
    elif removal_type == "focused":
        click.echo(f"Removed {slug} (focused session only)")
    else:
        click.echo(f"Removed worktree {slug}")
