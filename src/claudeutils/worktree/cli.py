"""Worktree CLI."""

import json
import os
import re
import shutil
import subprocess
import tempfile
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
    """Filter section entries by task_name or plan_dir match."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    if not (match := re.search(pattern, content, re.DOTALL)):
        return ""

    def is_relevant(entry: str) -> bool:
        lo = entry.lower()
        return task_name.lower() in lo or bool(plan_dir and plan_dir.lower() in lo)

    lines = [
        line
        for line in match.group(1).split("\n")
        if (line.startswith("- ") and is_relevant(line[2:].strip()))
        or (not line.startswith("- ") and line.strip())
    ]
    return f"## {section_name}\n\n" + "\n".join(lines) + "\n" if lines else ""


def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Filter session.md to task_name with relevant context sections."""
    content = Path(session_md_path).read_text()
    pattern = rf"- \[ \] \*\*{re.escape(task_name)}\*\* (.+?)(?=\n-|\n## |\Z)"
    if not (match := re.search(pattern, content, re.DOTALL)):
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)

    metadata = match.group(1).rstrip()
    plan_match = re.search(r"plan:\s*(\S+)", metadata)
    plan_dir = plan_match.group(1) if plan_match else None

    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n- [ ] **{task_name}** {metadata}\n"
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

    perms = settings.setdefault("permissions", {})
    dirs = perms.setdefault("additionalDirectories", [])
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
        path, branch = lines[i].split(maxsplit=1)[1], ""
        i += 1
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
    content = Path(session).read_text()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": tmp.name}
    try:
        blob = _git("hash-object", "-w", "--stdin", input_data=content)
        _git("read-tree", _git("rev-parse", f"{base}^{{tree}}"), env=env)
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
    project_root = _git("rev-parse", "--show-toplevel")
    _create_submodule_worktree(project_root, worktree_path, slug)

    container = worktree_path.parent
    add_sandbox_dir(str(container), ".claude/settings.local.json")
    add_sandbox_dir(str(container), f"{worktree_path}/.claude/settings.local.json")

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
        msg = "slug and --task are mutually exclusive"
        raise click.UsageError(msg)
    if not task and not slug:
        msg = "either slug or --task is required"
        raise click.UsageError(msg)
    temp_session_file = None
    try:
        if task:
            slug = derive_slug(task)
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
                f.write(focus_session(task, session_md))
                temp_session_file = session = f.name
        assert slug is not None
        worktree_path = wt_path(slug, create_container=True)
        if worktree_path.exists():
            click.echo(f"Error: existing directory {worktree_path}", err=True)
            raise SystemExit(1)

        _setup_worktree(worktree_path, slug, base, session, task)
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


def _check_merge_clean(exempt_paths: set[str]) -> None:
    """Verify OURS clean tree for merge."""
    parent = _git("status", "--porcelain", "--untracked-files=no", check=False)
    dirty = [
        line
        for line in parent.split("\n")
        if line and not any(path in line for path in exempt_paths)
    ]
    if dirty:
        click.echo("Clean tree required for merge (main)")
        raise SystemExit(1)
    submodule = _git(
        "-C", "agent-core", "status", "--porcelain", "--untracked-files=no", check=False
    )
    if submodule.strip():
        click.echo("Clean tree required for merge (main submodule)")
        raise SystemExit(1)


def _check_worktree_clean(worktree_path: Path) -> None:
    """Verify THEIRS (worktree) clean tree for merge (strict, no exemptions)."""
    parent = _git(
        "-C",
        str(worktree_path),
        "status",
        "--porcelain",
        "--untracked-files=no",
        check=False,
    )
    if parent.strip():
        click.echo(
            "Clean tree required for merge"
            " (worktree: uncommitted changes would be lost)"
        )
        raise SystemExit(1)
    submodule_path = worktree_path / "agent-core"
    if submodule_path.exists() and (submodule_path / ".git").exists():
        submodule = _git(
            "-C",
            str(submodule_path),
            "status",
            "--porcelain",
            "--untracked-files=no",
            check=False,
        )
        if submodule.strip():
            click.echo("Clean tree required for merge (worktree submodule)")
            raise SystemExit(1)


@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Prepare for merge: verify OURS and THEIRS clean tree."""
    _check_merge_clean(
        {"agents/session.md", "agents/jobs.md", "agents/learnings.md", "agent-core"}
    )
    worktree_path = wt_path(slug)
    _check_worktree_clean(worktree_path)


@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove worktree and its branch."""
    worktree_path = wt_path(slug)
    parent_reg, submodule_reg = _probe_registrations(worktree_path)

    if worktree_path.exists():
        status = _git("-C", str(worktree_path), "status", "--porcelain", check=False)
        if status:
            count = len(status.strip().split("\n"))
            click.echo(f"Warning: worktree has {count} uncommitted files")

    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)
    else:
        _git("worktree", "prune")

    r = subprocess.run(
        ["git", "branch", "-d", slug], capture_output=True, text=True, check=False
    )
    if r.returncode != 0 and "not found" not in r.stderr.lower():
        click.echo(f"Branch {slug} has unmerged changes — use: git branch -D {slug}")

    if worktree_path.exists():
        shutil.rmtree(worktree_path)

    container_path = worktree_path.parent
    if container_path.exists() and not list(container_path.iterdir()):
        container_path.rmdir()

    click.echo(f"Removed worktree {slug}")
