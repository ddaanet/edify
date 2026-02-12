"""Worktree CLI module."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import click


def wt_path(slug: str, create_container: bool = False) -> Path:  # noqa: FBT001,FBT002
    """Return absolute worktree path, optionally creating -wt container."""
    if not slug or not slug.strip():
        msg = "slug must not be empty or whitespace"
        raise ValueError(msg)

    current_path = Path.cwd()
    parent_name = current_path.parent.name

    if parent_name.endswith("-wt"):
        container_path = current_path.parent
    else:
        repo_name = current_path.name
        container_name = f"{repo_name}-wt"
        container_path = current_path.parent / container_name

    if create_container and not parent_name.endswith("-wt"):
        container_path.mkdir(parents=True, exist_ok=True)

    return container_path / slug


def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Transform task name to slug: lowercase, hyphens, truncated to max_length.

    Raises ValueError if task_name is empty or whitespace-only.
    """
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)

    slug = task_name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    slug = slug[:max_length]
    return slug.rstrip("-")


def _is_relevant_entry(entry: str, task_name: str, plan_dir: str | None) -> bool:
    """Check if entry mentions task name or plan directory."""
    entry_lower = entry.lower()
    task_lower = task_name.lower()

    if task_lower in entry_lower:
        return True
    return bool(plan_dir and plan_dir.lower() in entry_lower)


def _filter_section(
    content: str, section_name: str, task_name: str, plan_dir: str | None
) -> str:
    """Extract and filter a section, returning section text or empty string."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return ""

    section_content = match.group(1)
    lines = section_content.split("\n")

    relevant_lines = []
    for line in lines:
        if line.startswith("- "):
            entry = line[2:].strip()
            if _is_relevant_entry(entry, task_name, plan_dir):
                relevant_lines.append(line)
        elif not line.strip():
            continue
        else:
            relevant_lines.append(line)

    if not relevant_lines:
        return ""

    return f"## {section_name}\n\n" + "\n".join(relevant_lines) + "\n"


def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Extract task from session.md and generate focused session.

    Returns formatted string with H1 header, status, extracted task, and
    filtered sections.
    """
    session_md_path = Path(session_md_path)
    content = session_md_path.read_text()

    pattern = rf"- \[ \] \*\*{re.escape(task_name)}\*\* (.+?)(?=\n-|\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)

    task_metadata = match.group(1).rstrip()
    task_line = f"- [ ] **{task_name}** {task_metadata}"

    plan_dir = None
    if "plan:" in task_metadata:
        plan_match = re.search(r"plan:\s*(\S+)", task_metadata)
        if plan_match:
            plan_dir = plan_match.group(1)

    result = (
        f"# Session: Worktree — {task_name}\n"
        f"\n"
        f"**Status:** Focused worktree for parallel execution.\n"
        f"\n"
        f"## Pending Tasks\n"
        f"\n"
        f"{task_line}\n"
    )

    blockers = _filter_section(content, "Blockers / Gotchas", task_name, plan_dir)
    if blockers:
        result += f"\n{blockers}"

    references = _filter_section(content, "Reference Files", task_name, plan_dir)
    if references:
        result += f"\n{references}"

    return result


def add_sandbox_dir(container: str, settings_path: str | Path) -> None:
    """Add container to permissions.additionalDirectories."""
    settings_path = Path(settings_path)
    if not settings_path.exists():
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings: dict[str, Any] = {"permissions": {"additionalDirectories": []}}
    else:
        with settings_path.open() as f:
            settings = json.load(f)

    perms = settings.setdefault("permissions", {})
    dirs = perms.setdefault("additionalDirectories", [])
    if container not in dirs:
        dirs.append(container)

    with settings_path.open("w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


@click.group(name="_worktree")
def worktree() -> None:
    """Manage git worktrees."""


@worktree.command()
def ls() -> None:
    """List active worktrees (excluding main)."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    main_path = result.stdout.strip()

    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

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
                slug = Path(path).name
                entries.append((slug, branch, path))
        else:
            i += 1

    for slug, branch, path in entries:
        click.echo(f"{slug}\t{branch}\t{path}")


def _create_session_commit(slug: str, base: str, session: str) -> str:
    """Pre-commit session.md, return commit hash."""
    try:
        session_content = Path(session).read_text()
    except (FileNotFoundError, PermissionError) as e:
        click.echo(f"Error reading session file {session}: {e}", err=True)
        raise SystemExit(1) from e

    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp_index:
        tmp_index_path = tmp_index.name

    try:
        env = {**os.environ, "GIT_INDEX_FILE": tmp_index_path}

        result = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=session_content,
            capture_output=True,
            text=True,
            check=True,
        )
        blob_hash = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", f"{base}^{{tree}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        base_tree = result.stdout.strip()

        subprocess.run(
            ["git", "read-tree", base_tree],
            env=env,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob_hash},agents/session.md",
            ],
            env=env,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            ["git", "write-tree"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        new_tree = result.stdout.strip()

        result = subprocess.run(
            [
                "git",
                "commit-tree",
                new_tree,
                "-p",
                base,
                "-m",
                f"Focused session for {slug}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    finally:
        Path(tmp_index_path).unlink()


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Validate clean state, exempt session context files."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    parent_status = result.stdout

    # Treat missing agent-core as clean
    result = subprocess.run(
        ["git", "-C", "agent-core", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    submodule_status = result.stdout if result.returncode == 0 else ""

    combined = parent_status + submodule_status

    exempt_filenames = {"session.md", "jobs.md", "learnings.md"}
    filtered_lines = []
    for line in combined.rstrip().split("\n"):
        if not line:
            continue
        tokens = line.split()
        if len(tokens) >= 2:
            filepath = tokens[-1]
            filename = Path(filepath).name
            if filename in exempt_filenames and filepath.startswith("agents/"):
                continue
        filtered_lines.append(line)
    filtered_output = "\n".join(filtered_lines)

    if filtered_output:
        click.echo(filtered_output)
        raise SystemExit(1)


@worktree.command()
@click.argument("slug")
@click.option("--base", default="HEAD", help="Base commit for worktree branch")
@click.option("--session", default="", help="Session file path")
def new(slug: str, base: str, session: str) -> None:
    """Create worktree at wt/{slug}/ with branch {slug}."""
    worktree_path = Path(f"wt/{slug}")

    # Check for directory collision
    if worktree_path.exists():
        click.echo(f"Error: existing directory {worktree_path}", err=True)
        raise SystemExit(1)

    # Check for branch collision
    result = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        click.echo(f"Error: existing branch {slug}", err=True)
        raise SystemExit(1)

    try:
        if session:
            branch_commit = _create_session_commit(slug, base, session)
            subprocess.run(
                ["git", "branch", slug, branch_commit],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), slug],
                check=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), "-b", slug, base],
                check=True,
                capture_output=True,
            )

        # Initialize submodules in the new worktree
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        project_root = result.stdout.strip()
        agent_core_local = Path(project_root) / "agent-core"
        if agent_core_local.exists() and (agent_core_local / ".git").exists():
            # Use --reference to avoid fetching from remote
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(worktree_path),
                    "submodule",
                    "update",
                    "--init",
                    "--reference",
                    str(agent_core_local),
                ],
                check=False,
                capture_output=True,
            )
            # Create branch in submodule matching worktree slug
            submodule_path = worktree_path / "agent-core"
            if submodule_path.exists():
                result = subprocess.run(
                    ["git", "-C", str(submodule_path), "checkout", "-B", slug],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    click.echo(result.stderr, err=True)
                    raise SystemExit(1)

        click.echo(str(worktree_path))
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating worktree: {e.stderr}", err=True)
        raise SystemExit(1) from e


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit with message from stdin."""
    subprocess.run(
        ["git", "add", *list(files)],
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--quiet", "--cached"],
        check=False,
    )
    has_staged = result.returncode == 1

    if has_staged:
        message = click.get_text_stream("stdin").read()
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(result.stdout.strip())


@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove worktree at wt/{slug}/ and its branch (forced)."""
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
        )
        has_uncommitted = bool(result.stdout.strip())
        if has_uncommitted:
            click.echo(f"Warning: {slug} has uncommitted changes")

        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            check=True,
            capture_output=True,
        )
    else:
        # Prune stale registration
        subprocess.run(
            ["git", "worktree", "prune"],
            check=True,
            capture_output=True,
        )

    result = subprocess.run(
        ["git", "branch", "-D", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        click.echo(result.stderr)

    click.echo(f"Removed worktree {slug}")
