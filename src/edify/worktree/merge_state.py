"""Merge state detection and untracked file recovery."""

import subprocess

import click

from edify.git import _git
from edify.worktree.git_ops import _is_branch_merged


def _detect_merge_state(slug: str) -> str:
    """Detect the current merge state for a branch.

    Returns one of: "merged", "clean", "parent_resolved", "parent_conflicts", or
    "submodule_conflicts".

    Detection order (D-5):
    1. merged: branch is ancestor of HEAD
    2. submodule_conflicts: MERGE_HEAD exists in plugin
    3. parent_resolved: MERGE_HEAD exists in parent, no unresolved conflicts
    4. parent_conflicts: MERGE_HEAD exists in parent, unresolved conflicts present
    5. clean: none of the above
    """
    if _is_branch_merged(slug):
        return "merged"

    submodule_merge_head = subprocess.run(
        ["git", "-C", "plugin", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )

    if submodule_merge_head.returncode == 0:
        return "submodule_conflicts"

    merge_head = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )

    if merge_head.returncode == 0:
        conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split(
            "\n"
        )
        conflicts = [c for c in conflicts if c.strip()]
        if conflicts:
            return "parent_conflicts"
        return "parent_resolved"

    return "clean"


def _parse_untracked_files(stderr: str) -> list[str]:
    """Parse file paths from git untracked-file collision error message."""
    files: list[str] = []
    lines = stderr.split("\n")
    in_file_list = False
    for line in lines:
        lower_line = line.lower()
        if (
            "untracked working tree file" in lower_line
            or "your local changes to the following files would be overwritten by merge"
            in lower_line
        ):
            in_file_list = True
            continue
        if in_file_list:
            if not line or (line and not line[0].isspace()):
                break
            files.append(line.strip())
    return files


def _add_and_commit_files(files: list[str], slug: str, stderr: str) -> None:
    """Add files to index and commit them to resolve untracked collision."""
    for file_path in files:
        try:
            subprocess.run(
                ["git", "add", file_path],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as err:
            click.echo(f"Merge failed: {stderr}")
            raise SystemExit(1) from err

    try:
        subprocess.run(
            ["git", "commit", "-m", f"Track files to resolve {slug} merge"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        click.echo(f"Merge failed: {err.stderr}")
        raise SystemExit(1) from err


def _recover_untracked_file_collision(
    slug: str, result: subprocess.CompletedProcess[str]
) -> bool:
    """Recover from untracked file collision by adding files and retrying merge.

    When git merge fails because untracked files would be overwritten, parse the
    file paths from stderr, add them to the index, and retry the merge.

    Returns True if recovery was successful and merge started, False if recovery
    failed.
    """
    stderr = result.stderr.strip() if result.stderr else ""
    files_to_add = _parse_untracked_files(stderr)

    if not files_to_add:
        return False

    _add_and_commit_files(files_to_add, slug, stderr)

    retry_result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", slug],
        capture_output=True,
        text=True,
        check=False,
    )

    if retry_result.returncode == 0:
        return True

    merge_head = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )
    if merge_head.returncode != 0:
        click.echo(f"Merge failed: {retry_result.stderr.strip()}")
        raise SystemExit(1)

    return True
