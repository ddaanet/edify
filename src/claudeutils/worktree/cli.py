"""Worktree CLI."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

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


def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Task name to slug."""
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)
    slug = re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")[:max_length]
    return slug.rstrip("-")


def _filter_section(
    content: str, section_name: str, task_name: str, plan_dir: str | None
) -> str:
    """Filter section to task-relevant entries."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return ""

    def is_relevant(entry: str) -> bool:
        lo = entry.lower()
        return task_name.lower() in lo or bool(plan_dir and plan_dir.lower() in lo)

    relevant_lines = [
        line
        for line in match.group(1).split("\n")
        if (line.startswith("- ") and is_relevant(line[2:].strip()))
        or (not line.startswith("- ") and line.strip())
    ]
    if not relevant_lines:
        return ""
    return f"## {section_name}\n\n" + "\n".join(relevant_lines) + "\n"


def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Focused session.md for task."""
    content = Path(session_md_path).read_text()
    pattern = rf"- \[ \] \*\*{re.escape(task_name)}\*\* (.+?)(?=\n-|\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)

    metadata = match.group(1).rstrip()
    plan_match = re.search(r"plan:\s*(\S+)", metadata) if "plan:" in metadata else None
    plan_dir = plan_match.group(1) if plan_match else None

    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n- [ ] **{task_name}** {metadata}\n"
    )

    for section in ["Blockers / Gotchas", "Reference Files"]:
        filtered = _filter_section(content, section, task_name, plan_dir)
        if filtered:
            result += f"\n{filtered}"

    return result


def add_sandbox_dir(container: str, settings_path: str | Path) -> None:
    """Register container in settings for sandbox."""
    settings_path = Path(settings_path)
    if settings_path.exists():
        with settings_path.open() as f:
            settings: dict[str, Any] = json.load(f)
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings = {"permissions": {"additionalDirectories": []}}

    dirs = settings.setdefault("permissions", {}).setdefault(
        "additionalDirectories", []
    )
    if container not in dirs:
        dirs.append(container)
    with settings_path.open("w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def initialize_environment(worktree_path: Path) -> None:
    """Run just setup in worktree."""
    try:
        r = subprocess.run(["just", "--version"], capture_output=True, check=False)
        just_available = r.returncode == 0
    except FileNotFoundError:
        just_available = False

    if not just_available:
        click.echo("Warning: just command not found, skipping setup step", err=True)
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
    """Manage git worktrees."""


@worktree.command()
def ls() -> None:
    """List worktrees excluding main."""
    main_path = _git("rev-parse", "--show-toplevel")
    porcelain_output = _git("worktree", "list", "--porcelain")

    lines = porcelain_output.split("\n") if porcelain_output else []
    entries = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("worktree "):
            path = lines[i].split(maxsplit=1)[1]
            i += 1
            branch = ""
            while i < len(lines) and lines[i]:
                if lines[i].startswith("branch "):
                    branch = lines[i].split(maxsplit=1)[1]
                i += 1
            i += 1
            if path != main_path:
                entries.append((Path(path).name, branch, path))
        else:
            i += 1

    for slug, branch, path in entries:
        click.echo(f"{slug}\t{branch}\t{path}")


def _build_tree_with_session(content: str, base_tree: str, env: dict[str, str]) -> str:
    """Git tree with session.md added."""
    blob = _git("hash-object", "-w", "--stdin", input_data=content)
    _git("read-tree", base_tree, env=env)
    _git(
        "update-index",
        "--add",
        "--cacheinfo",
        f"100644,{blob},agents/session.md",
        env=env,
    )
    return _git("write-tree", env=env)


def _create_session_commit(slug: str, base: str, session: str) -> str:
    """Commit session.md, return hash."""
    try:
        content = Path(session).read_text()
    except (FileNotFoundError, PermissionError) as e:
        click.echo(f"Error reading session file {session}: {e}", err=True)
        raise SystemExit(1) from e

    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp_index:
        tmp_index_path = tmp_index.name

    try:
        env = {**os.environ, "GIT_INDEX_FILE": tmp_index_path}
        base_tree = _git("rev-parse", f"{base}^{{tree}}")
        tree = _build_tree_with_session(content, base_tree, env)
        return _git(
            "commit-tree", tree, "-p", base, "-m", f"Focused session for {slug}"
        )
    finally:
        Path(tmp_index_path).unlink(missing_ok=True)


def _create_parent_worktree(
    worktree_path: Path, slug: str, base: str, session: str
) -> None:
    """Create parent worktree."""
    try:
        _git("rev-parse", "--verify", slug)
        branch_exists = True
    except subprocess.CalledProcessError:
        branch_exists = False

    if branch_exists and session:
        msg = f"Warning: branch {slug} exists, ignoring --session"
        click.echo(msg, err=True)
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
    """Create submodule worktree for agent-core."""
    agent_core_local = Path(project_root) / "agent-core"
    if not agent_core_local.exists() or not (agent_core_local / ".git").exists():
        return

    try:
        _git("-C", str(agent_core_local), "rev-parse", "--verify", slug)
        flag = []
    except subprocess.CalledProcessError:
        flag = ["-b"]
    _git(
        "-C",
        str(agent_core_local),
        "worktree",
        "add",
        str(worktree_path / "agent-core"),
        *flag,
        slug,
    )


def _setup_worktree(
    worktree_path: Path, slug: str, base: str, session: str, task: str
) -> None:
    """Create parent and submodule worktrees, configure sandbox."""
    try:
        _create_parent_worktree(worktree_path, slug, base, session)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating parent worktree: {e.stderr}", err=True)
        raise SystemExit(1) from e

    project_root = _git("rev-parse", "--show-toplevel")

    try:
        _create_submodule_worktree(project_root, worktree_path, slug)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating submodule worktree: {e.stderr}", err=True)
        raise SystemExit(1) from e

    container_path = worktree_path.parent
    add_sandbox_dir(str(container_path), ".claude/settings.local.json")
    add_sandbox_dir(str(container_path), f"{worktree_path}/.claude/settings.local.json")

    initialize_environment(worktree_path)

    if task:
        click.echo(f"{slug}\t{worktree_path}")
    else:
        click.echo(str(worktree_path))


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Clean tree except session context."""
    parent_status = _git("status", "--porcelain")
    submodule_status = _git("-C", "agent-core", "status", "--porcelain", check=False)

    exempt_files = {"session.md", "jobs.md", "learnings.md"}
    filtered_lines = [
        line
        for line in (parent_status + submodule_status).rstrip().split("\n")
        if line
        and not (
            len(tokens := line.split()) >= 2
            and tokens[-1].startswith("agents/")
            and Path(tokens[-1]).name in exempt_files
        )
    ]
    if filtered_lines:
        click.echo("\n".join(filtered_lines))
        raise SystemExit(1)


@worktree.command()
@click.argument("slug", required=False)
@click.option("--base", default="HEAD")
@click.option("--session", default="")
@click.option("--task", default="")
@click.option("--session-md", default="agents/session.md")
def new(slug: str | None, base: str, session: str, task: str, session_md: str) -> None:
    """Create worktree at sibling -wt container with branch {slug}."""
    if task and slug:
        msg = "slug and --task are mutually exclusive"
        raise click.UsageError(msg)
    if not task and not slug:
        msg = "either slug or --task is required"
        raise click.UsageError(msg)
    if task and session:
        click.echo("Warning: --session option ignored when --task provided", err=True)
        session = ""

    temp_session_file = None
    try:
        if task:
            slug = derive_slug(task)
            session_content = focus_session(task, session_md)
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
                f.write(session_content)
                session = f.name
                temp_session_file = session

        if slug is None:
            msg = "either slug or --task is required"
            raise click.UsageError(msg)

        worktree_path = wt_path(slug, create_container=True)

        if worktree_path.exists():
            click.echo(f"Error: existing directory {worktree_path}", err=True)
            raise SystemExit(1)

        _setup_worktree(worktree_path, slug, base, session, task)
    finally:
        if temp_session_file is not None:
            Path(temp_session_file).unlink(missing_ok=True)


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage and commit with stdin message."""
    _git("add", *list(files))
    try:
        _git("diff", "--quiet", "--cached")
    except subprocess.CalledProcessError:
        click.echo(_git("commit", "-m", click.get_text_stream("stdin").read()))


@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove worktree and branch."""
    worktree_path = wt_path(slug)
    if worktree_path.exists():
        status_output = _git(
            "-C", str(worktree_path), "status", "--porcelain", check=False
        )
        if status_output:
            uncommitted_count = len(status_output.strip().split("\n"))
            click.echo(f"Warning: worktree has {uncommitted_count} uncommitted files")
        _git("worktree", "remove", "--force", str(worktree_path))
    else:
        _git("worktree", "prune")

    try:
        _git("branch", "-D", slug)
    except subprocess.CalledProcessError as e:
        if "not found" not in e.stderr.lower():
            click.echo(e.stderr)
    click.echo(f"Removed worktree {slug}")
