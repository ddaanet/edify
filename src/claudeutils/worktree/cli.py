"""Worktree CLI."""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import click

from claudeutils.git import _fail, _git, _is_submodule_dirty
from claudeutils.validation.session_commands import (
    _COMMAND_REQUIRED_CHECKBOXES,
    _SKILL_NAME_PATTERN,
    WORKFLOW_SKILLS,
)
from claudeutils.validation.task_parsing import parse_task_line
from claudeutils.validation.tasks import validate_task_name_format
from claudeutils.worktree.display import format_rich_ls
from claudeutils.worktree.git_ops import (
    _classify_branch,
    _create_session_commit,
    _create_submodule_worktree,
    _delete_submodule_branch,
    _get_worktree_path_for_branch,
    _is_branch_merged,
    _is_merge_of,
    _parse_worktree_list,
    _probe_registrations,
    _remove_worktrees,
    wt_path,
)
from claudeutils.worktree.merge import merge as merge_impl
from claudeutils.worktree.session import (
    add_slug_marker,
    remove_slug_marker,
)
from claudeutils.worktree.session import focus_session as focus_session  # noqa: PLC0414


def _validate_task_command(session_md_path: Path, task_name: str) -> None:
    """Validate task has a valid command before worktree creation.

    Checks command presence and skill allowlist (FR-1, FR-2, FR-4).
    """
    lines = session_md_path.read_text().splitlines()
    for i, line in enumerate(lines, 1):
        parsed = parse_task_line(line, lineno=i)
        if not parsed or parsed.name != task_name:
            continue
        if parsed.checkbox not in _COMMAND_REQUIRED_CHECKBOXES:
            return  # exempt checkbox
        if not parsed.command:
            _fail(f"Missing command in **{task_name}** — cannot create worktree")
        m = _SKILL_NAME_PATTERN.match(parsed.command)
        if m and m.group(1) not in WORKFLOW_SKILLS:
            _fail(
                f"Unknown skill /{m.group(1)} in **{task_name}** — "
                "cannot create worktree"
            )
        return  # found and valid


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


def _copy_test_sentinel(worktree_path: Path) -> None:
    """Copy test sentinel to new worktree so cached test state carries over."""
    sentinel = Path("tmp/.test-sentinel")
    if sentinel.exists():
        dest = worktree_path / "tmp"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sentinel, dest / ".test-sentinel")


def _initialize_environment(worktree_path: Path) -> None:
    try:
        subprocess.run(["just", "--version"], capture_output=True, check=True)
    except FileNotFoundError, subprocess.CalledProcessError:
        return
    r = subprocess.run(
        ["just", "setup"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        click.echo(f"Warning: just setup failed: {r.stderr}")


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
        click.echo(f"Warning: branch {slug} exists, ignoring --session")
        session = ""
    if session:
        _git("branch", slug, _create_session_commit(slug, base, session))
        _git("worktree", "add", str(worktree_path), slug)
    elif branch_exists:
        _git("worktree", "add", str(worktree_path), slug)
    else:
        _git("worktree", "add", str(worktree_path), "-b", slug, base)


def _setup_worktree(
    worktree_path: Path, slug: str, base: str, session: str, task: str
) -> None:
    """Create worktrees and init environment."""
    _create_parent_worktree(worktree_path, slug, base, session)
    main_repo = _git("rev-parse", "--show-toplevel").strip()
    _create_submodule_worktree(main_repo, worktree_path, slug)
    _initialize_environment(worktree_path)
    _copy_test_sentinel(worktree_path)
    click.echo(f"{slug}\t{worktree_path}" if task else str(worktree_path))


def _setup_worktree_safe(
    path: Path, slug: str, base: str, session: str, task: str
) -> None:
    """Run _setup_worktree, cleaning up the directory on failure."""
    try:
        _setup_worktree(path, slug, base, session, task)
    except subprocess.CalledProcessError, OSError:
        if path.exists():
            shutil.rmtree(path)
        container = path.parent
        if container.exists() and not list(container.iterdir()):
            container.rmdir()
        raise


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Verify clean tree except session context."""
    parent = _git("status", "--porcelain")
    submodule = _git("-C", "plugin", "status", "--porcelain", check=False)
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
        _fail("\n".join(dirty))


@worktree.command()
@click.argument("task_name", required=False)
@click.option("--branch", default="")
@click.option("--base", default="HEAD")
@click.option("--session", default="")
@click.option("--session-md", default="agents/session.md")
def new(
    task_name: str | None, branch: str, base: str, session: str, session_md: str
) -> None:
    """Create worktree in sibling container."""
    if not task_name and not branch:
        raise click.UsageError("provide a task name or --branch <slug>")  # noqa: TRY003
    temp_session_file = None
    try:
        if task_name:
            try:
                slug = branch or derive_slug(task_name)
            except ValueError as e:
                _fail(str(e), 2)
            session_md_path = Path(session_md)
            if not session_md_path.exists():
                _fail(f"Error: session.md not found at {session_md}")
            _validate_task_command(session_md_path, task_name)
            add_slug_marker(session_md_path, task_name, slug)
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
                f.write(focus_session(task_name, session_md))
                temp_session_file = session = f.name
        else:
            slug = branch
        if (path := wt_path(slug, create_container=True)).exists():
            _fail(f"Error: existing directory {path}")
        _setup_worktree_safe(path, slug, base, session, task_name or "")
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
        _fail(f"git error: {stderr or e}")


def _guard_branch_removal(slug: str) -> tuple[bool, str | None]:  # noqa: RET503
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
    _fail(msg, 2)


def _delete_branch(slug: str, removal_type: str | None) -> None:
    flag = "-D" if removal_type == "focused" else "-d"
    r = subprocess.run(
        ["git", "branch", flag, slug], capture_output=True, text=True, check=False
    )
    if r.returncode != 0 and "not found" not in r.stderr.lower():
        _fail(f"Branch {slug} deletion failed: {r.stderr.strip()}")


def _check_not_dirty(slug: str, worktree_path: Path) -> None:  # noqa: ARG001
    """Block removal if worktree or submodule has uncommitted changes."""
    if worktree_path.exists():
        status = _git("-C", str(worktree_path), "status", "--porcelain", check=False)
        if status.strip():
            n = len(status.strip().split("\n"))
            msg = (
                f"Worktree has {n} uncommitted file(s). "
                "Commit or stash before removing worktree."
            )
            _fail(msg, 2)
    if _is_submodule_dirty("plugin"):
        msg = (
            "Submodule (plugin) has uncommitted changes. "
            "Commit or stash before removing worktree."
        )
        _fail(msg, 2)


def _update_session_and_amend(slug: str) -> bool:
    session_md_path = Path("agents/session.md")
    if not session_md_path.exists():
        return False
    remove_slug_marker(session_md_path, slug)
    if not _is_merge_of(slug):
        return False
    parent_status = _git("status", "--porcelain", check=False)
    other_dirty = [
        line
        for line in parent_status.strip().split("\n")
        if line and not line.endswith("agents/session.md")
    ]
    if other_dirty:
        click.echo("Warning: skipping session amend (parent repo dirty)")
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
    "--force",
    is_flag=True,
    default=False,
    help="Force removal bypassing all safety checks",
)
def rm(slug: str, force: bool) -> None:  # noqa: FBT001
    """Remove worktree and its branch."""
    try:
        worktree_path = _get_worktree_path_for_branch(slug) or wt_path(slug)
        if not force:
            _check_not_dirty(slug, worktree_path)
            branch_exists, removal_type = _guard_branch_removal(slug)
        else:
            branch_exists = True
            removal_type = "focused"
        parent_reg, submodule_reg = _probe_registrations(worktree_path)
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
            if warning := _delete_submodule_branch(slug):
                click.echo(warning)
        amend_note = " Merge commit amended." if amended else ""
        detail = " (focused session only)" if removal_type == "focused" else ""
        prefix = "Removed worktree" if removal_type is None else "Removed"
        click.echo(f"{prefix} {slug}{detail}{amend_note}")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if isinstance(e.stderr, str) else ""
        _fail(f"git error: {stderr or e}")
