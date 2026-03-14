"""CLI commands for git utilities (_git group)."""

import click

from claudeutils.git import discover_submodules, git_diff, git_status


def _prefix_status_lines(raw_status: str, submodule_path: str) -> str:
    """Prefix each status line path with the submodule directory name.

    Git status --porcelain v1 format: XY PATH where XY is 2 chars + 1 space.
    Returns prefixed status string, or empty string if raw_status is empty.
    """
    prefixed_lines: list[str] = []
    for line in raw_status.splitlines():
        if not line:
            continue
        # Format: XY path (first 3 chars are XY status codes + separator space)
        status_code = line[:3]
        file_path = line[3:]
        prefixed_lines.append(f"{status_code}{submodule_path}/{file_path}")
    return "\n".join(prefixed_lines)


def _build_repo_section(header: str, status: str, diff: str) -> str:
    """Build a markdown section with header, status, and diff parts."""
    parts: list[str] = []
    if status:
        parts.append(status)
    if diff:
        parts.append(diff)
    return header + "\n\n".join(parts)


@click.group(name="_git", hidden=True)
def git_group() -> None:
    """Provide internal git utility commands."""


@git_group.command(name="changes")
def changes_cmd() -> None:
    """Emit unified parent + submodule status and diff.

    Output is structured markdown. Only dirty repos are shown. Submodule file
    paths are prefixed with the submodule directory name. Exit 0 always
    (informational).
    """
    sections: list[str] = []

    # Parent repo
    parent_status = git_status()
    parent_diff = git_diff()

    if parent_status or parent_diff:
        sections.append(_build_repo_section("## Parent\n", parent_status, parent_diff))

    # Submodules
    for submodule_path in discover_submodules():
        sub_status_raw = git_status(repo_dir=submodule_path)
        sub_diff = git_diff(repo_dir=submodule_path)

        if not sub_status_raw and not sub_diff:
            # Clean submodule — omit section
            continue

        prefixed_status = _prefix_status_lines(sub_status_raw, submodule_path)
        sections.append(
            _build_repo_section(
                f"## Submodule: {submodule_path}\n", prefixed_status, sub_diff
            )
        )

    if not sections:
        click.echo("Tree is clean.")
    else:
        click.echo("\n\n".join(sections))
