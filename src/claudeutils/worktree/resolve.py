"""Conflict resolution strategies for worktree merge."""

import subprocess
from pathlib import Path

import click

from claudeutils.worktree.git_ops import _git
from claudeutils.worktree.session import (
    extract_blockers,
    extract_task_blocks,
    find_section_bounds,
)


def _merge_blockers(
    result_lines: list[str], ours: str, theirs: str, slug: str | None
) -> None:
    """Merge Blockers / Gotchas: deduplicate, tag, append.

    Mutates result_lines in place. Tags theirs with [from: slug].
    """
    theirs_blockers = extract_blockers(theirs)
    if not theirs_blockers:
        return

    ours_first_lines = {b[0] for b in extract_blockers(ours)}
    new_blockers = [b for b in theirs_blockers if b[0] not in ours_first_lines]
    if not new_blockers:
        return

    tagged_lines: list[str] = []
    for blocker in new_blockers:
        first_line = blocker[0]
        if slug:
            first_line = f"{first_line} [from: {slug}]"
        tagged_lines.append(first_line)
        tagged_lines.extend(blocker[1:])

    content = "\n".join(result_lines)
    bounds = find_section_bounds(content, "Blockers / Gotchas")
    if bounds is not None:
        result_lines[bounds[1] : bounds[1]] = tagged_lines
        return

    # Insert before first section that follows Blockers in canonical order
    insert_at = None
    for after_section in ("Reference Files", "Next Steps"):
        sb = find_section_bounds(content, after_section)
        if sb is not None and (insert_at is None or sb[0] < insert_at):
            insert_at = sb[0]
    if insert_at is not None:
        result_lines[insert_at:insert_at] = [
            "## Blockers / Gotchas",
            "",
            *tagged_lines,
            "",
        ]
    else:
        result_lines.extend(["", "## Blockers / Gotchas", "", *tagged_lines])


def _merge_session_contents(ours: str, theirs: str, slug: str | None = None) -> str:
    """Merge session.md contents with per-section strategies (D-5).

    Strategy table:
    - Status line, Completed This Session, Worktree Tasks,
      Reference Files, Next Steps: keep ours (implicit — ours is base)
    - Pending Tasks: additive (union by task name)
    - Blockers / Gotchas: evaluate (tag theirs with [from: slug], append)
    """
    ours_blocks = [
        b for b in extract_task_blocks(ours) if b.section != "Worktree Tasks"
    ]
    theirs_blocks = [
        b for b in extract_task_blocks(theirs) if b.section != "Worktree Tasks"
    ]
    ours_names = {b.name for b in ours_blocks}
    new_blocks = [b for b in theirs_blocks if b.name not in ours_names]

    result_lines = ours.split("\n")

    # Pending Tasks: additive strategy
    if new_blocks:
        new_task_lines: list[str] = []
        for block in sorted(new_blocks, key=lambda b: b.name):
            new_task_lines.extend(block.lines)

        bounds = find_section_bounds(ours, "Pending Tasks")
        if bounds is not None:
            insertion_point = bounds[1]
            if (
                insertion_point < len(result_lines)
                and result_lines[insertion_point] != ""
                and (not new_task_lines or new_task_lines[-1] != "")
            ):
                new_task_lines.append("")
            result_lines[insertion_point:insertion_point] = new_task_lines
        else:
            result_lines.extend(["", "## Pending Tasks", "", *new_task_lines])

    _merge_blockers(result_lines, ours, theirs, slug)

    return "\n".join(result_lines)


def resolve_session_md(conflicts: list[str], slug: str | None = None) -> list[str]:
    """Resolve session.md conflict: keep ours, merge new content from theirs."""
    if "agents/session.md" not in conflicts:
        return conflicts

    ours_content = _git("show", ":2:agents/session.md", check=False)
    theirs_content = _git("show", ":3:agents/session.md", check=False)
    merged = _merge_session_contents(ours_content, theirs_content, slug=slug)

    try:
        Path("agents/session.md").write_text(merged)
        _git("add", "agents/session.md")
    except subprocess.CalledProcessError:
        try:
            blob_hash = _git("hash-object", "-w", "agents/session.md")
            _git(
                "update-index",
                "--cacheinfo",
                f"100644,{blob_hash},agents/session.md",
            )
            click.echo(
                "session.md: staged via hash-object (git add failed)",
            )
        except subprocess.CalledProcessError:
            click.echo(
                "session.md: resolution failed, falling back to ours",
            )
            _git("checkout", "--ours", "agents/session.md")
            _git("add", "agents/session.md")

    return [c for c in conflicts if c != "agents/session.md"]


def resolve_learnings_md(conflicts: list[str]) -> list[str]:
    """Resolve agents/learnings.md conflict.

    Keep ours and append theirs-only content.
    """
    if "agents/learnings.md" not in conflicts:
        return conflicts

    ours_content = _git("show", ":2:agents/learnings.md", check=False)
    theirs_content = _git("show", ":3:agents/learnings.md", check=False)

    ours_lines = set(ours_content.split("\n"))
    theirs_lines = theirs_content.split("\n")
    theirs_only = [line for line in theirs_lines if line not in ours_lines]

    merged = ours_content
    if theirs_only:
        merged += "\n" + "\n".join(theirs_only)

    Path("agents/learnings.md").write_text(merged)
    _git("add", "agents/learnings.md")

    return [c for c in conflicts if c != "agents/learnings.md"]
