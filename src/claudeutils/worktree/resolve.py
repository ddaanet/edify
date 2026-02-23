"""Conflict resolution strategies for worktree merge."""

import re
import subprocess
from pathlib import Path

import click

from claudeutils.validation.learnings import parse_segments
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

    # Strip [from: ...] tags so prior-merge tagged blockers still match
    tag_re = re.compile(r"\s*\[from: [^\]]+\]")
    ours_first_lines = {tag_re.sub("", b[0]) for b in extract_blockers(ours)}
    new_blockers = [
        b for b in theirs_blockers if tag_re.sub("", b[0]) not in ours_first_lines
    ]
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


def _format_conflict_segment(
    heading: str, ours_body: list[str], theirs_body: list[str]
) -> list[str]:
    """Format a conflicting segment with diff3 markers."""
    lines = [f"## {heading}"]
    lines.append("<<<<<<< ours")
    lines.extend(ours_body)
    lines.append("=======")
    lines.extend(theirs_body)
    lines.append(">>>>>>> theirs")
    return lines


def _segments_to_content_with_conflicts(
    merged: dict[str, list[str]],
    conflict_headings: list[str],
    ours: dict[str, list[str]],
    theirs: dict[str, list[str]],
) -> str:
    """Assemble content with diff3 conflict markers for conflicting segments."""
    parts: list[str] = []
    conflict_set = set(conflict_headings)
    for heading, body in merged.items():
        if heading == "":
            parts.extend(body)
        elif heading in conflict_set:
            parts.extend(
                _format_conflict_segment(
                    heading, ours.get(heading, []), theirs.get(heading, [])
                )
            )
        else:
            parts.append(f"## {heading}")
            parts.extend(body)
    return "\n".join(parts)


def resolve_learnings_md(conflicts: list[str]) -> list[str]:
    """Resolve agents/learnings.md conflict using segment-level diff3.

    If segment conflicts detected, writes conflict markers and leaves the file
    unresolved (not staged, not removed from conflicts list).
    """
    if "agents/learnings.md" not in conflicts:
        return conflicts

    base_content = _git("show", ":1:agents/learnings.md", check=False)
    ours_content = _git("show", ":2:agents/learnings.md", check=False)
    theirs_content = _git("show", ":3:agents/learnings.md", check=False)

    base_segs = parse_segments(base_content)
    ours_segs = parse_segments(ours_content)
    theirs_segs = parse_segments(theirs_content)

    merged_segs, conflict_headings = diff3_merge_segments(
        base_segs, ours_segs, theirs_segs
    )

    if conflict_headings:
        content = _segments_to_content_with_conflicts(
            merged_segs, conflict_headings, ours_segs, theirs_segs
        )
        Path("agents/learnings.md").write_text(content)
        # Leave in conflicts list — caller will report and exit 3
        return conflicts

    Path("agents/learnings.md").write_text(_segments_to_content(merged_segs))
    _git("add", "agents/learnings.md")
    return [c for c in conflicts if c != "agents/learnings.md"]


def _resolve_heading(
    heading: str,
    base: dict[str, list[str]],
    ours: dict[str, list[str]],
    theirs: dict[str, list[str]],
) -> tuple[list[str] | None, bool]:
    """Resolve a single heading across base/ours/theirs.

    Returns (body_or_none, is_conflict). None means delete/omit.
    """
    in_ours = heading in ours
    in_theirs = heading in theirs

    # Absent from ours — omit (deleted or never existed on our side)
    if not in_ours:
        return None, False

    # Absent from theirs — keep ours
    if not in_theirs:
        return ours[heading], False

    # Not in base — new on one or both sides; keep ours
    if heading not in base:
        return ours[heading], False

    # Preamble: additive merge
    if heading == "":
        ours_set = set(ours[heading])
        extra = [ln for ln in theirs[heading] if ln not in ours_set]
        return ours[heading] + extra, False

    # In all three — compare bodies for modification
    base_body = "\n".join(base[heading])
    ours_body = "\n".join(ours[heading])
    theirs_body = "\n".join(theirs[heading])
    ours_changed = ours_body != base_body
    theirs_changed = theirs_body != base_body

    if ours_changed and theirs_changed:
        return ours[heading], True
    return theirs[heading] if theirs_changed else ours[heading], False


def diff3_merge_segments(
    base: dict[str, list[str]],
    ours: dict[str, list[str]],
    theirs: dict[str, list[str]],
) -> tuple[dict[str, list[str]], list[str]]:
    """Three-way segment merge using diff3 semantics.

    Resolution matrix:
    - only ours modified: keep ours
    - only theirs modified: take theirs
    - both modified: conflict (returned in conflicts list, ours kept)
    - new in theirs only: append
    - new in ours only: keep
    - unchanged: keep
    """
    all_headings: list[str] = []
    seen: set[str] = set()
    for heading in list(base) + list(ours) + list(theirs):
        if heading not in seen:
            all_headings.append(heading)
            seen.add(heading)

    merged: dict[str, list[str]] = {}
    conflicts: list[str] = []

    for heading in all_headings:
        body, is_conflict = _resolve_heading(heading, base, ours, theirs)
        if body is not None:
            merged[heading] = body
        if is_conflict:
            conflicts.append(heading)

    # Append theirs-only new entries missed by iteration order
    for heading, body in theirs.items():
        if heading not in base and heading not in ours and heading not in merged:
            merged[heading] = body

    return merged, conflicts


def _segments_to_content(segments: dict[str, list[str]]) -> str:
    """Reassemble segments dict into file content string."""
    parts: list[str] = []
    for heading, body in segments.items():
        if heading == "":
            parts.extend(body)
        else:
            parts.append(f"## {heading}")
            parts.extend(body)
    return "\n".join(parts)


def remerge_learnings_md() -> None:
    """Segment-level diff3 merge for learnings.md; skips when no MERGE_HEAD."""
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )
    if merge_head_check.returncode != 0:
        return

    # Skip if learnings.md doesn't exist on disk (repo doesn't use it)
    if not Path("agents/learnings.md").exists():
        return

    merge_base = _git("merge-base", "HEAD", "MERGE_HEAD", check=False)
    base_content = _git("show", f"{merge_base}:agents/learnings.md", check=False)
    ours_content = _git("show", "HEAD:agents/learnings.md", check=False)
    theirs_content = _git("show", "MERGE_HEAD:agents/learnings.md", check=False)

    merged_segments, conflicts = diff3_merge_segments(
        parse_segments(base_content),
        parse_segments(ours_content),
        parse_segments(theirs_content),
    )
    merged_content = _segments_to_content(merged_segments)

    if conflicts:
        click.echo(
            f"learnings.md: {len(conflicts)} segment conflict(s): {conflicts}",
            err=True,
        )
        conflict_content = _segments_to_content_with_conflicts(
            merged_segments,
            conflicts,
            parse_segments(ours_content),
            parse_segments(theirs_content),
        )
        Path("agents/learnings.md").write_text(conflict_content)
        raise SystemExit(3)

    Path("agents/learnings.md").write_text(merged_content)
    _git("add", "agents/learnings.md")
