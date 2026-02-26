#!/usr/bin/env python3
"""Session scraper — 4-stage pipeline for Claude Code session analysis.

Stages: scan → parse → tree → correlate

Usage:
    session-scraper.py scan [--prefix PATH]
    session-scraper.py parse <session-id> --project DIR [--expand t42]
    session-scraper.py tree <session-id> --project DIR
    session-scraper.py correlate <session-id> --project DIR [--git-dir DIR]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

import click
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from claudeutils.parsing import extract_content_text  # noqa: E402
from claudeutils.paths import encode_project_path, get_project_history_dir  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
COMMIT_RE = re.compile(r"\[(?:[^\[\]]*?\s+)?([0-9a-f]{7,12})\]")
INTERACTIVE_TOOLS = frozenset({"ExitPlanMode", "AskUserQuestion"})
GIT_COMMIT_MARKERS = frozenset({"file changed", "files changed", "create mode"})


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class EntryType(StrEnum):
    USER_PROMPT = "user_prompt"
    SKILL_INVOCATION = "skill_invocation"
    TOOL_CALL = "tool_call"
    TOOL_INTERACTIVE = "tool_interactive"
    INTERRUPT = "interrupt"
    AGENT_ANSWER = "agent_answer"


class TimelineEntry(BaseModel):
    timestamp: str
    entry_type: EntryType
    session_id: str
    agent_source: str | None = None
    content: str
    detail: dict[str, Any] | None = None
    ref: str | None = None  # stable ref for targeted expansion (e.g. "t42")


class SessionTree(BaseModel):
    root_session_id: str
    project_dir: str
    entries: list[TimelineEntry]
    commit_hashes: set[str]
    agent_ids: list[str]

    model_config = {"arbitrary_types_allowed": True}


class CommitInfo(BaseModel):
    hash: str
    author: str
    date: str
    message: str
    files_changed: int
    insertions: int
    deletions: int
    branch: str | None = None


class CorrelationResult(BaseModel):
    session_commits: dict[str, list[CommitInfo]]  # session_id → commits
    commit_sessions: dict[str, list[str]]  # commit_hash → session_ids
    unattributed: list[CommitInfo]  # commits with no session match


# ---------------------------------------------------------------------------
# Stage 1: Scanner
# ---------------------------------------------------------------------------


def scan_projects(prefix: str | None = None) -> list[tuple[Path, str, int, int]]:
    """Return (history_dir, encoded_name, uuid_count, agent_count) per
    project."""
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return []

    encoded_prefix: str | None = None
    if prefix:
        try:
            encoded_prefix = encode_project_path(prefix)
        except ValueError:
            pass

    results = []
    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir():
            continue
        if encoded_prefix and not history_dir.name.startswith(encoded_prefix):
            continue
        uuid_count = sum(
            1 for f in history_dir.glob("*.jsonl") if UUID_RE.match(f.stem)
        )
        # Agents stored at: <history_dir>/<session-uuid>/subagents/agent-*.jsonl
        agent_count = sum(1 for _ in history_dir.glob("*/subagents/agent-*.jsonl"))
        results.append((history_dir, history_dir.name, uuid_count, agent_count))
    return results


# ---------------------------------------------------------------------------
# Stage 2: Parser
# ---------------------------------------------------------------------------


def _text_from(content: Any) -> str:
    """Extract text string from string or list content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "\n".join(parts)
    return ""


def _has_tool_results(content: list) -> bool:
    return any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)


def _extract_commit_hash(tool_output: str) -> str | None:
    """Extract git commit hash from Bash output, requiring commit context
    markers."""
    m = COMMIT_RE.search(tool_output)
    if m and any(marker in tool_output for marker in GIT_COMMIT_MARKERS):
        return m.group(1)
    return None


def parse_session_file(path: Path, file_type: str = "uuid") -> list[TimelineEntry]:
    """Parse a single JSONL file into ordered TimelineEntry list."""
    entries: list[TimelineEntry] = []
    pending_tools: dict[
        str, dict[str, Any]
    ] = {}  # tool_use_id → {name, input, timestamp, session_id}
    pending_skill: TimelineEntry | None = None
    ref_n = 0
    agent_source: str | None = None

    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = e.get("type")
        timestamp = e.get("timestamp", "")
        session_id = e.get("sessionId", "")
        msg_content = e.get("message", {}).get("content", "")

        # Capture agent_source from first entry in agent files
        if agent_source is None and file_type == "agent":
            agent_source = e.get("agentId")
        cur_agent = e.get("agentId") or agent_source

        if etype == "assistant":
            pending_skill = None
            text_parts: list[str] = []
            if isinstance(msg_content, str):
                if msg_content.strip():
                    text_parts.append(msg_content)
            elif isinstance(msg_content, list):
                for block in msg_content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text" and block.get("text", "").strip():
                        text_parts.append(block["text"])
                    elif block.get("type") == "tool_use":
                        tid = block.get("id", "")
                        pending_tools[tid] = {
                            "name": block.get("name", ""),
                            "input": block.get("input", {}),
                            "timestamp": timestamp,
                            "session_id": session_id,
                        }
            if text_parts:
                full = "\n".join(text_parts)
                entries.append(
                    TimelineEntry(
                        timestamp=timestamp,
                        entry_type=EntryType.AGENT_ANSWER,
                        session_id=session_id,
                        agent_source=cur_agent,
                        content=full[:200],
                        detail={"full_text": full} if len(full) > 200 else None,
                    )
                )

        elif etype == "user":
            if isinstance(msg_content, list) and _has_tool_results(msg_content):
                # Resolve tool results → emit tool_call / tool_interactive entries
                for block in msg_content:
                    if (
                        not isinstance(block, dict)
                        or block.get("type") != "tool_result"
                    ):
                        continue
                    tool_use_id = block.get("tool_use_id", "")
                    info = pending_tools.pop(tool_use_id, None)
                    if info is None:
                        continue

                    tool_name = info["name"]
                    raw_output = block.get("content", "")
                    is_error = block.get("is_error", False)

                    if isinstance(raw_output, str):
                        tool_output = raw_output
                    elif isinstance(raw_output, list):
                        tool_output = " ".join(
                            item.get("text", "")
                            for item in raw_output
                            if isinstance(item, dict) and item.get("type") == "text"
                        )
                    else:
                        tool_output = ""

                    status = "error" if is_error else "success"
                    ref_n += 1
                    detail: dict[str, Any] = {
                        "input": info["input"],
                        "output": tool_output[:2000],
                        "status": status,
                    }

                    if tool_name == "Bash" and not is_error:
                        h = _extract_commit_hash(tool_output)
                        if h:
                            detail["commit_hash"] = h

                    et = (
                        EntryType.TOOL_INTERACTIVE
                        if tool_name in INTERACTIVE_TOOLS
                        else EntryType.TOOL_CALL
                    )
                    content_str = (
                        f"{tool_name}: {tool_output[:120]}"
                        if et == EntryType.TOOL_INTERACTIVE
                        else f"{tool_name}: {status}"
                    )
                    entries.append(
                        TimelineEntry(
                            timestamp=info["timestamp"],
                            entry_type=et,
                            session_id=info["session_id"],
                            agent_source=cur_agent,
                            content=content_str,
                            detail=detail,
                            ref=f"t{ref_n}",
                        )
                    )

            elif isinstance(msg_content, list):
                # Non-tool-result list: skill body injection or list-format prompt
                first_text = _text_from(msg_content)
                if (
                    first_text.startswith("Base directory for this skill")
                    and pending_skill
                ):
                    # Suppress skill body, attach to preceding skill_invocation detail
                    pending_skill.detail = pending_skill.detail or {}
                    pending_skill.detail["skill_body"] = first_text[:500]
                    pending_skill = None
                elif first_text.strip():
                    entries.append(
                        TimelineEntry(
                            timestamp=timestamp,
                            entry_type=EntryType.USER_PROMPT,
                            session_id=session_id,
                            agent_source=cur_agent,
                            content=first_text[:200],
                        )
                    )
                    pending_skill = None

            elif isinstance(msg_content, str):
                if msg_content.startswith(("<system-reminder>", "<local-command")):
                    pass  # suppress system/local-command injections
                elif "[Request interrupted by user]" in msg_content:
                    entries.append(
                        TimelineEntry(
                            timestamp=timestamp,
                            entry_type=EntryType.INTERRUPT,
                            session_id=session_id,
                            agent_source=cur_agent,
                            content="[Request interrupted by user]",
                        )
                    )
                    pending_skill = None
                elif "<command-name>" in msg_content:
                    cmd_m = re.search(
                        r"<command-name>([^<]+)</command-name>", msg_content
                    )
                    cmd = cmd_m.group(1).strip() if cmd_m else "?"
                    args_m = re.search(
                        r"<command-args>(.*?)</command-args>", msg_content, re.DOTALL
                    )
                    args = args_m.group(1).strip() if args_m else ""
                    # cmd may already include leading "/" (e.g. "/recall")
                    cmd_str = cmd if cmd.startswith("/") else f"/{cmd}"
                    summary = cmd_str + (f" {args}" if args else "")
                    skill_entry = TimelineEntry(
                        timestamp=timestamp,
                        entry_type=EntryType.SKILL_INVOCATION,
                        session_id=session_id,
                        agent_source=cur_agent,
                        content=summary,
                        detail={"raw": msg_content[:500]},
                    )
                    entries.append(skill_entry)
                    pending_skill = skill_entry
                else:
                    entries.append(
                        TimelineEntry(
                            timestamp=timestamp,
                            entry_type=EntryType.USER_PROMPT,
                            session_id=session_id,
                            agent_source=cur_agent,
                            content=msg_content[:200],
                        )
                    )
                    pending_skill = None

    return entries


# ---------------------------------------------------------------------------
# Stage 3: Aggregator
# ---------------------------------------------------------------------------


def build_session_tree(root_session_id: str, project_dir: str) -> SessionTree:
    """Aggregate main session + direct sub-agents into a SessionTree."""
    history_dir = get_project_history_dir(project_dir)
    all_entries: list[TimelineEntry] = []
    commit_hashes: set[str] = set()
    agent_ids: list[str] = []

    def _ingest(path: Path, ftype: str) -> None:
        for entry in parse_session_file(path, ftype):
            all_entries.append(entry)
            if entry.detail and "commit_hash" in entry.detail:
                commit_hashes.add(entry.detail["commit_hash"])

    main_path = history_dir / f"{root_session_id}.jsonl"
    if main_path.exists():
        _ingest(main_path, "uuid")

    # Discover direct sub-agents from <history_dir>/<session-uuid>/subagents/
    subagents_dir = history_dir / root_session_id / "subagents"
    if subagents_dir.exists():
        seen: set[str] = set()
        for agent_file in sorted(subagents_dir.glob("agent-*.jsonl")):
            try:
                first_line = agent_file.read_text().split("\n")[0].strip()
                first_entry = json.loads(first_line) if first_line else {}
            except (json.JSONDecodeError, OSError):
                continue
            agent_id = first_entry.get("agentId", "")
            if not agent_id or agent_id in seen:
                continue
            seen.add(agent_id)
            agent_ids.append(agent_id)
            _ingest(agent_file, "agent")

    all_entries.sort(key=lambda entry: entry.timestamp)
    return SessionTree(
        root_session_id=root_session_id,
        project_dir=project_dir,
        entries=all_entries,
        commit_hashes=commit_hashes,
        agent_ids=agent_ids,
    )


# ---------------------------------------------------------------------------
# Stage 4: Correlator
# ---------------------------------------------------------------------------


def _git_commit_info(commit_hash: str, git_dir: str) -> CommitInfo | None:
    try:
        r = subprocess.run(
            [
                "git",
                "-C",
                git_dir,
                "log",
                "-1",
                "--format=%H\t%an\t%ai\t%s",
                "--numstat",
                commit_hash,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    lines = r.stdout.strip().splitlines()
    if not lines:
        return None
    parts = lines[0].split("\t", 3)
    if len(parts) < 4:
        return None
    hash_, author, date, message = parts
    files_changed = insertions = deletions = 0
    for line in lines[2:]:  # skip blank separator
        cols = line.split("\t")
        if len(cols) >= 2:
            files_changed += 1
            try:
                insertions += int(cols[0])
                deletions += int(cols[1])
            except ValueError:
                pass  # binary files show "-"
    return CommitInfo(
        hash=hash_,
        author=author,
        date=date,
        message=message,
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
    )


def correlate_session_tree(tree: SessionTree, git_dir: str) -> CorrelationResult:
    """Join session commit hashes against git history."""
    session_commits: dict[str, list[CommitInfo]] = {}
    commit_sessions: dict[str, list[str]] = {}
    unattributed: list[CommitInfo] = []

    # Build hash → sessions map from tree entries
    hash_to_sessions: dict[str, list[str]] = {}
    for entry in tree.entries:
        if entry.detail and "commit_hash" in entry.detail:
            h = entry.detail["commit_hash"]
            hash_to_sessions.setdefault(h, [])
            if entry.session_id not in hash_to_sessions[h]:
                hash_to_sessions[h].append(entry.session_id)

    for h, sessions in hash_to_sessions.items():
        info = _git_commit_info(h, git_dir)
        if info is None:
            continue
        for sid in sessions:
            session_commits.setdefault(sid, []).append(info)
        commit_sessions[h] = sessions

    # Find recent unattributed commits (not matched to any session)
    try:
        r = subprocess.run(
            ["git", "-C", git_dir, "log", "--format=%H", "--max-count=50"],
            capture_output=True,
            text=True,
            check=True,
        )
        known = set(hash_to_sessions.keys())
        for line in r.stdout.strip().splitlines():
            h = line.strip()
            if h and h[:7] not in known and h not in known:
                info = _git_commit_info(h, git_dir)
                if info:
                    unattributed.append(info)
    except subprocess.CalledProcessError:
        pass

    return CorrelationResult(
        session_commits=session_commits,
        commit_sessions=commit_sessions,
        unattributed=unattributed,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
def cli() -> None:
    """Session scraper — analyze Claude Code session histories."""


@cli.command()
@click.option("--prefix", default=None, help="Filter by project path prefix (absolute)")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def scan(prefix: str | None, fmt: str) -> None:
    """Stage 1: list all projects and session counts."""
    results = scan_projects(prefix)
    if fmt == "json":
        click.echo(
            json.dumps(
                [
                    {"encoded": enc, "uuid_sessions": u, "agent_files": a}
                    for _, enc, u, a in results
                ],
                indent=2,
            )
        )
    else:
        for _, enc, u, a in results:
            click.echo(f"{enc}: {u} sessions, {a} agent files")


@cli.command()
@click.argument("session_id")
@click.option("--project", required=True, help="Project directory (absolute path)")
@click.option(
    "--expand", "expand_ref", default=None, help="Show detail for ref (e.g. t42)"
)
@click.option("--all-detail", is_flag=True, help="Show detail for all entries")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def parse(
    session_id: str, project: str, expand_ref: str | None, all_detail: bool, fmt: str
) -> None:
    """Stage 2: parse a single session into a timeline."""
    history_dir = get_project_history_dir(project)
    path = history_dir / f"{session_id}.jsonl"
    if not path.exists():
        click.echo(f"Not found: {path}", err=True)
        raise SystemExit(1)
    entries = parse_session_file(path)
    if fmt == "json":
        click.echo(json.dumps([e.model_dump() for e in entries], indent=2, default=str))
        return
    for e in entries:
        ref = f" [{e.ref}]" if e.ref else ""
        click.echo(f"{e.timestamp[:19]}  {e.entry_type:<20}{ref}  {e.content[:90]}")
        if e.detail and (all_detail or (expand_ref and e.ref == expand_ref)):
            for k, v in e.detail.items():
                click.echo(f"    {k}: {str(v)[:200]}")


@cli.command()
@click.argument("session_id")
@click.option("--project", required=True, help="Project directory (absolute path)")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def tree(session_id: str, project: str, fmt: str) -> None:
    """Stage 3: build aggregated session tree with sub-agents."""
    t = build_session_tree(session_id, project)
    if fmt == "json":
        d = t.model_dump()
        d["commit_hashes"] = list(d["commit_hashes"])
        click.echo(json.dumps(d, indent=2, default=str))
        return
    click.echo(f"Root:    {session_id}")
    click.echo(f"Agents:  {len(t.agent_ids)}")
    click.echo(f"Entries: {len(t.entries)}")
    commits_str = (
        "  " + " ".join(sorted(t.commit_hashes)) if t.commit_hashes else "  (none)"
    )
    click.echo(f"Commits: {len(t.commit_hashes)}{commits_str}")
    click.echo()
    for e in t.entries:
        src = f"[{e.agent_source[:8]}]" if e.agent_source else "[main    ]"
        ref = f" [{e.ref}]" if e.ref else ""
        click.echo(
            f"{e.timestamp[:19]}  {src}  {e.entry_type:<20}{ref}  {e.content[:70]}"
        )


@cli.command()
@click.argument("session_id")
@click.option("--project", required=True, help="Project directory (absolute path)")
@click.option("--git-dir", default=None, help="Git repo dir (defaults to --project)")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def correlate(session_id: str, project: str, git_dir: str | None, fmt: str) -> None:
    """Stage 4: correlate session commits with git history."""
    t = build_session_tree(session_id, project)
    if not t.commit_hashes:
        click.echo("No commits found in session tree.", err=True)
        raise SystemExit(1)
    result = correlate_session_tree(t, git_dir or project)
    if fmt == "json":
        click.echo(json.dumps(result.model_dump(), indent=2, default=str))
        return
    click.echo(f"Attributed commits: {len(result.commit_sessions)}")
    for h, sessions in result.commit_sessions.items():
        click.echo(f"  {h}  ←  {', '.join(s[:8] for s in sessions)}")
    click.echo(f"Unattributed (recent 50): {len(result.unattributed)}")


if __name__ == "__main__":
    cli()
