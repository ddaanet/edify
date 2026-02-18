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
from claudeutils.worktree.display import format_rich_ls
from claudeutils.worktree.merge import merge as merge_impl
from claudeutils.worktree.session import focus_session as focus_session  # noqa: PLC0414
from claudeutils.worktree.session import (
    move_task_to_worktree,
    remove_worktree_task,
)
from claudeutils.worktree.utils import (
    _classify_branch,
    _get_worktree_path_for_branch,
    _git,
    _is_branch_merged,
    _is_merge_commit,
    _is_parent_dirty,
    _is_submodule_dirty,
    _parse_worktree_list,
    _probe_registrations,
    _remove_worktrees,
    wt_path,
)


def derive_slug(task_name: str) -> str:
    """Task name to slug."""
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)
    format_errors = validate_task_name_format(task_name)
    if format_errors:
        raise ValueError(format_errors[0])
    return re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")


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


def _initialize_environment(worktree_path: Path) -> None:
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


@worktree.command()
@click.option("--porcelain", is_flag=True, help="Machine-readable output")
def ls(*, porcelain: bool) -> None:
    """List worktrees and main tree."""
    main_path = _git("rev-parse", "--show-toplevel")
    porcelain_output = _git("worktree", "list", "--porcelain")

    if porcelain:
        for slug, branch, path in _parse_worktree_list(porcelain_output, main_path):
            click.echo(f"{slug}\t{branch}\t{path}")
    else:
        click.echo(format_rich_ls(main_path, porcelain_output))


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
    main_repo = _git("rev-parse", "--show-toplevel").strip()
    _create_submodule_worktree(main_repo, worktree_path, slug)
    add_sandbox_dir(str(worktree_path.parent), ".claude/settings.local.json")
    add_sandbox_dir(
        str(worktree_path.parent), f"{worktree_path}/.claude/settings.local.json"
    )
    add_sandbox_dir(main_repo, f"{worktree_path}/.claude/settings.local.json")
    _initialize_environment(worktree_path)
    click.echo(f"{slug}\t{worktree_path}" if task else str(worktree_path))


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Verify clean tree except session context."""
    parent = _git("status", "--porcelain")
    submodule = _git("-C", "agent-core", "status", "--porcelain", check=False)
    exempt = {"session.md", "learnings.md"}
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


@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Merge worktree branch back to main."""
    try:
        merge_impl(slug)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if isinstance(e.stderr, str) else ""
        click.echo(f"git error: {stderr or e}", err=True)
        raise SystemExit(1) from None


def _guard_branch_removal(slug: str) -> tuple[bool, str | None]:
    """Check if branch can be removed safely."""
    branch_check = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if branch_check.returncode != 0:
        return False, None

    if _is_branch_merged(slug):
        return True, "merged"

    count, is_focused = _classify_branch(slug)
    if count == 1 and is_focused:
        return True, "focused"

    msg = (
        f"Branch {slug} is orphaned (no common ancestor). Merge first."
        if count == 0
        else f"Branch {slug} has {count} unmerged commit(s). Merge first."
    )
    click.echo(msg, err=True)
    raise SystemExit(2)


def _delete_branch(slug: str, removal_type: str | None) -> None:
    flag = "-D" if removal_type == "focused" else "-d"
    r = subprocess.run(
        ["git", "branch", flag, slug], capture_output=True, text=True, check=False
    )
    if r.returncode != 0 and "not found" not in r.stderr.lower():
        click.echo(f"Branch {slug} deletion failed: {r.stderr.strip()}", err=True)
        raise SystemExit(1)


def _check_confirm(slug: str, confirm: bool) -> None:  # noqa: FBT001
    if not confirm:
        click.echo(
            f"Use the worktree skill (wt merge {slug}) to remove worktrees safely. "
            "Pass --confirm to invoke directly.",
            err=True,
        )
        raise SystemExit(2)


def _warn_if_dirty(worktree_path: Path) -> None:
    if worktree_path.exists():
        status = _git("-C", str(worktree_path), "status", "--porcelain", check=False)
        if status:
            n = len(status.strip().split("\n"))
            click.echo(f"Warning: worktree has {n} uncommitted files")


def _update_session_and_amend(slug: str) -> bool:
    session_md_path = Path("agents/session.md")
    if not session_md_path.exists():
        return False
    remove_worktree_task(session_md_path, slug, slug)
    if not _is_merge_commit():
        return False
    status_output = _git("status", "--porcelain", "agents/session.md", check=False)
    if not status_output.strip():
        return False
    _git("add", "agents/session.md")
    _git("commit", "--amend", "--no-edit")
    return True


@worktree.command()
@click.argument("slug")
@click.option(
    "--confirm",
    is_flag=True,
    default=False,
    help="Confirm direct invocation (bypass skill requirement)",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force removal bypassing all safety checks",
)
def rm(slug: str, confirm: bool, force: bool) -> None:  # noqa: FBT001
    """Remove worktree and its branch."""
    if not force:
        _check_confirm(slug, confirm)

    worktree_path = _get_worktree_path_for_branch(slug) or wt_path(slug)
    if not force:
        if _is_parent_dirty(exclude_path=str(worktree_path.parent)):
            click.echo(
                "Parent repo has uncommitted changes. "
                "Commit or stash before removing worktree.",
                err=True,
            )
            raise SystemExit(2)
        if _is_submodule_dirty():
            click.echo(
                "Submodule (agent-core) has uncommitted changes. "
                "Commit or stash before removing worktree.",
                err=True,
            )
            raise SystemExit(2)

        branch_exists, removal_type = _guard_branch_removal(slug)
    else:
        branch_exists = True
        removal_type = "focused"
    parent_reg, submodule_reg = _probe_registrations(worktree_path)

    _warn_if_dirty(worktree_path)
    amended = _update_session_and_amend(slug)

    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)

    if worktree_path.exists():
        shutil.rmtree(worktree_path)

    _git("worktree", "prune")

    container = worktree_path.parent
    if container.exists() and not list(container.iterdir()):
        container.rmdir()

    if branch_exists:
        _delete_branch(slug, removal_type)
    amend_note = " Merge commit amended." if amended else ""
    detail = " (focused session only)" if removal_type == "focused" else ""
    prefix = "Removed worktree" if removal_type is None else "Removed"
    click.echo(f"{prefix} {slug}{detail}{amend_note}")
