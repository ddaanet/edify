"""Phase 4 remerge functions for all merge paths."""

import subprocess
from pathlib import Path

import click

from claudeutils.validation.learnings import parse_segments
from claudeutils.worktree.git_ops import _git
from claudeutils.worktree.resolve import (
    _merge_session_contents,
    _segments_to_content,
    _segments_to_content_with_conflicts,
    diff3_merge_segments,
)


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

    base_segs = parse_segments(base_content)
    ours_segs = parse_segments(ours_content)
    theirs_segs = parse_segments(theirs_content)
    merged_segments, conflicts = diff3_merge_segments(
        base_segs,
        ours_segs,
        theirs_segs,
    )

    if conflicts:
        click.echo(
            f"learnings.md: {len(conflicts)} segment conflict(s): {conflicts}",
            err=True,
        )
        click.echo(
            "Resolve agents/learnings.md and re-run merge.",
            err=True,
        )
        conflict_content = _segments_to_content_with_conflicts(
            merged_segments,
            conflicts,
            ours_segs,
            theirs_segs,
        )
        Path("agents/learnings.md").write_text(conflict_content)
        raise SystemExit(3)

    Path("agents/learnings.md").write_text(_segments_to_content(merged_segments))
    _git("add", "agents/learnings.md")

    kept = sum(1 for h in merged_segments if h != "" and h in ours_segs)
    appended = sum(1 for h in merged_segments if h != "" and h not in ours_segs)
    dropped = sum(
        1
        for h in theirs_segs
        if h != "" and h in base_segs and h not in merged_segments
    )
    if appended > 0 or dropped > 0:
        click.echo(
            f"learnings.md: kept {kept} + appended {appended} new"
            f" (dropped {dropped} consolidated)"
        )


def remerge_session_md(slug: str | None = None, *, from_main: bool = False) -> None:
    """Structural session.md merge for all paths; skips when no MERGE_HEAD."""
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )
    if merge_head_check.returncode != 0:
        return

    if not Path("agents/session.md").exists():
        return

    if from_main:
        # Branch session is authoritative; working tree already has our content.
        # Just stage it to resolve the conflict marker without merging main's tasks.
        ours_content = _git("show", "HEAD:agents/session.md", check=False)
        Path("agents/session.md").write_text(ours_content)
        _git("add", "agents/session.md")
        return

    ours_content = _git("show", "HEAD:agents/session.md", check=False)
    theirs_content = _git("show", "MERGE_HEAD:agents/session.md", check=False)
    merged = _merge_session_contents(ours_content, theirs_content, slug=slug)

    Path("agents/session.md").write_text(merged)
    _git("add", "agents/session.md")
