#!/usr/bin/env python3
"""Session scraper — 6-stage pipeline for Claude Code session analysis.

Stages: scan → parse → tree → correlate → search → excerpt

Usage:
    session-scraper.py scan [--prefix PATH]
    session-scraper.py parse <session-id> --project DIR [--expand t42]
    session-scraper.py tree <session-id> --project DIR
    session-scraper.py correlate <session-id> --project DIR [--git-dir DIR]
    session-scraper.py search --project DIR --keyword TERM [--keyword TERM2]
    session-scraper.py excerpt <session-id> --project DIR --keyword TERM [--window 5]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

import click
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from claudeutils.paths import encode_project_path, get_project_history_dir  # noqa: E402

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
AGENT_RE = re.compile(r"^agent-")
COMMIT_RE = re.compile(r"\[(?:[^\[\]]*?\s+)?([0-9a-f]{7,12})\]")
INTERACTIVE_TOOLS = frozenset({"ExitPlanMode", "AskUserQuestion"})
GIT_COMMIT_MARKERS = frozenset({"file changed", "files changed", "create mode"})


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


class SearchHit(BaseModel):
    session_id: str
    project_dir: str
    ref: str | None
    entry_type: str
    timestamp: str
    keyword: str
    snippet: str  # content around the match


class SessionFile(BaseModel):
    path: Path
    project_dir: str
    file_type: Literal["uuid", "agent"]
    session_id: str

    model_config = {"arbitrary_types_allowed": True}


class CorrelationResult(BaseModel):
    session_commits: dict[str, list[CommitInfo]]  # session_id → commits
    commit_sessions: dict[str, list[str]]  # commit_hash → session_ids
    unattributed: list[CommitInfo]  # commits with no session match
    merge_parents: dict[str, list[str]]  # merge_hash → worktree session dirs


def _decode_project_path(encoded: str) -> str:
    """Best-effort decode of encoded project path (lossy — dashes are
    ambiguous)."""
    if encoded == "-":
        return "/"
    return encoded.replace("-", "/")


def scan_projects(prefix: str | None = None) -> list[SessionFile]:
    """Return one SessionFile per UUID session file across all projects."""
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return []

    encoded_prefix: str | None = None
    if prefix:
        try:
            encoded_prefix = encode_project_path(prefix)
        except ValueError:
            print(f"warning: invalid prefix path: {prefix}", file=sys.stderr)

    results: list[SessionFile] = []
    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir():
            continue
        if encoded_prefix and not history_dir.name.startswith(encoded_prefix):
            continue
        decoded = _decode_project_path(history_dir.name)
        for f in sorted(history_dir.glob("*.jsonl")):
            if UUID_RE.match(f.stem):
                results.append(
                    SessionFile(
                        path=f,
                        project_dir=decoded,
                        file_type="uuid",
                        session_id=f.stem,
                    )
                )
            elif AGENT_RE.match(f.stem):
                # Agent files: strip "agent-" prefix for session_id
                results.append(
                    SessionFile(
                        path=f,
                        project_dir=decoded,
                        file_type="agent",
                        session_id=f.stem.removeprefix("agent-"),
                    )
                )
    return results


def _text_from(content: Any) -> str:
    """Extract text from string or list content, joining all text blocks.

    Differs from claudeutils.parsing.extract_content_text which returns only the
    first text block — here we join all blocks for multi-block prompts.
    """
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
    except OSError as exc:
        print(f"warning: cannot read session file {path}: {exc}", file=sys.stderr)
        return []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"warning: malformed JSONL in {path}: {exc}", file=sys.stderr)
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
            # Key Decision 1: check subtype field first, fall back to content inspection
            msg_subtype = e.get("message", {}).get("subtype", "")
            has_tools = msg_subtype == "tool_result" or (
                isinstance(msg_content, list) and _has_tool_results(msg_content)
            )
            if has_tools and not isinstance(msg_content, list):
                pass  # tool_result with non-list content — suppress
            elif has_tools:
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
                # Non-tool-result list: skill body injection or list-format prompt.
                # Interrupt signals may appear as plain strings in the list, not
                # typed {type: "text"} blocks, so check raw items first.
                raw_strings = [item for item in msg_content if isinstance(item, str)]
                first_text = _text_from(msg_content)
                interrupt_text = first_text + "\n" + "\n".join(raw_strings)
                if "[Request interrupted by user]" in interrupt_text:
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
                elif (
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
            except (json.JSONDecodeError, OSError) as exc:
                print(
                    f"warning: cannot read agent file {agent_file.name}: {exc}",
                    file=sys.stderr,
                )
                continue
            agent_id = first_entry.get("agentId", "")
            if not agent_id or agent_id in seen:
                continue
            seen.add(agent_id)
            agent_ids.append(agent_id)
            _ingest(agent_file, "agent")

    all_entries.sort(key=lambda entry: entry.timestamp)
    # Re-number refs globally to avoid collisions across files
    ref_n = 0
    for entry in all_entries:
        if entry.ref is not None:
            ref_n += 1
            entry.ref = f"t{ref_n}"
    return SessionTree(
        root_session_id=root_session_id,
        project_dir=project_dir,
        entries=all_entries,
        commit_hashes=commit_hashes,
        agent_ids=agent_ids,
    )


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
    except subprocess.CalledProcessError as exc:
        print(
            f"warning: git log failed for commit {commit_hash}: {exc}", file=sys.stderr
        )
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

    # Find recent unattributed commits (not matched to any session).
    # Normalize extracted hashes to 7-char prefixes for comparison against full
    # hashes returned by git log.
    try:
        r = subprocess.run(
            ["git", "-C", git_dir, "log", "--format=%H", "--max-count=50"],
            capture_output=True,
            text=True,
            check=True,
        )
        known_prefixes = {h[:7] for h in hash_to_sessions}
        for line in r.stdout.strip().splitlines():
            h = line.strip()
            if h and h[:7] not in known_prefixes:
                info = _git_commit_info(h, git_dir)
                if info:
                    unattributed.append(info)
    except subprocess.CalledProcessError as exc:
        print(f"warning: git log failed for {git_dir}: {exc}", file=sys.stderr)

    # Merge commit parent tracing (FR-4): identify constituent worktree branches
    merge_parents: dict[str, list[str]] = {}  # merge_hash → [parent_session_dir, ...]
    try:
        r = subprocess.run(
            ["git", "-C", git_dir, "log", "--merges", "--format=%H", "--max-count=50"],
            capture_output=True,
            text=True,
            check=True,
        )
        projects_dir = Path.home() / ".claude" / "projects"
        for line in r.stdout.strip().splitlines():
            merge_hash = line.strip()
            if not merge_hash:
                continue
            # Get parent commits (parent 2+ are merged branches)
            try:
                pr = subprocess.run(
                    ["git", "-C", git_dir, "rev-parse", f"{merge_hash}^2"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                parent_hash = pr.stdout.strip()
                # Find branch(es) containing the parent commit
                br = subprocess.run(
                    [
                        "git",
                        "-C",
                        git_dir,
                        "branch",
                        "--contains",
                        parent_hash,
                        "--format=%(refname:short)",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                branches = [
                    b.strip() for b in br.stdout.strip().splitlines() if b.strip()
                ]
                # Map branch slugs to worktree session directories.
                # Match branch as a segment between '-' delimiters in the
                # encoded project path to avoid substring false positives
                # (e.g. branch "main" matching "-maintenance-").
                session_dirs: list[str] = []
                if projects_dir.exists():
                    for branch in branches:
                        for pdir in projects_dir.iterdir():
                            if not pdir.is_dir():
                                continue
                            # Check branch appears as exact segment(s) in encoded path
                            segments = pdir.name.split("-")
                            if branch in segments:
                                session_dirs.append(str(pdir))
                if session_dirs:
                    merge_parents[merge_hash] = session_dirs
            except subprocess.CalledProcessError:
                continue  # parent lookup failed for this merge
    except subprocess.CalledProcessError as exc:
        print(
            f"warning: merge commit scan failed for {git_dir}: {exc}", file=sys.stderr
        )

    return CorrelationResult(
        session_commits=session_commits,
        commit_sessions=commit_sessions,
        unattributed=unattributed,
        merge_parents=merge_parents,
    )


def _entry_full_text(entry: TimelineEntry) -> str:
    """Extract all searchable text from an entry (content + detail)."""
    parts = [entry.content]
    if entry.detail:
        if "full_text" in entry.detail:
            parts.append(entry.detail["full_text"])
        if "output" in entry.detail:
            parts.append(str(entry.detail["output"]))
        if "input" in entry.detail:
            inp = entry.detail["input"]
            if isinstance(inp, dict):
                for v in inp.values():
                    parts.append(str(v))
            else:
                parts.append(str(inp))
        if "skill_body" in entry.detail:
            parts.append(entry.detail["skill_body"])
    return "\n".join(parts)


def search_sessions(
    project_dirs: list[str],
    keywords: list[str],
    case_sensitive: bool = False,
) -> list[SearchHit]:
    """Search across sessions in given project directories for keyword matches.

    Returns SearchHit per matching entry (deduplicated by session+ref+keyword).
    """
    all_files = scan_projects(prefix=None)
    # Build lookup: encoded_dir_name -> list[SessionFile]
    # Accept both real paths and decoded paths
    encoded_targets: set[str] = set()
    for pdir in project_dirs:
        try:
            encoded_targets.add(encode_project_path(pdir))
        except ValueError:
            print(f"warning: cannot encode project path: {pdir}", file=sys.stderr)
        # Also try matching against decoded project_dir from scan
        encoded_targets.add(pdir)

    target_files: list[SessionFile] = []
    for sf in all_files:
        if sf.file_type != "uuid":
            continue
        # Check if this session's project matches any target
        try:
            encoded = encode_project_path(sf.project_dir)
        except ValueError:
            print(
                f"warning: cannot encode session project_dir: {sf.project_dir}",
                file=sys.stderr,
            )
            encoded = ""
        # Match against encoded name or decoded project_dir
        if encoded in encoded_targets or sf.project_dir in encoded_targets:
            target_files.append(sf)

    # Also match by checking the actual encoded dir name from the filesystem path.
    # This catches cases where encode_project_path(decoded) diverges from the
    # original encoded name (lossy decode via _decode_project_path).
    matched_sids: set[str] = {sf.session_id for sf in target_files}
    for sf in all_files:
        if sf.file_type != "uuid" or sf.session_id in matched_sids:
            continue
        actual_encoded = sf.path.parent.name
        if actual_encoded in encoded_targets:
            target_files.append(sf)
            matched_sids.add(sf.session_id)

    hits: list[SearchHit] = []
    seen: set[tuple[str, str, str]] = set()  # (session_id, ref_or_timestamp, keyword)

    kw_patterns = []
    for kw in keywords:
        flags = 0 if case_sensitive else re.IGNORECASE
        kw_patterns.append((kw, re.compile(re.escape(kw), flags)))

    for sf in target_files:
        entries = parse_session_file(sf.path, sf.file_type)
        for entry in entries:
            full_text = _entry_full_text(entry)
            for kw, pattern in kw_patterns:
                m = pattern.search(full_text)
                if not m:
                    continue
                # For entries without a stable ref, use timestamp as dedup key
                dedup_ref = entry.ref if entry.ref is not None else entry.timestamp
                key = (sf.session_id, dedup_ref, kw)
                if key in seen:
                    continue
                seen.add(key)
                start = max(0, m.start() - 60)
                end = min(len(full_text), m.end() + 60)
                snippet = full_text[start:end].replace("\n", " ")
                hits.append(
                    SearchHit(
                        session_id=sf.session_id,
                        project_dir=sf.project_dir,
                        ref=entry.ref,
                        entry_type=entry.entry_type,
                        timestamp=entry.timestamp,
                        keyword=kw,
                        snippet=snippet,
                    )
                )
    return hits


def extract_excerpts(
    session_id: str,
    project_dir: str,
    refs: list[str] | None = None,
    keywords: list[str] | None = None,
    window: int = 5,
) -> str:
    """Extract conversation excerpts around matching refs or keywords.

    Returns markdown-formatted excerpt with window entries before/after each
    match.
    """
    history_dir = get_project_history_dir(project_dir)
    path = history_dir / f"{session_id}.jsonl"
    if not path.exists():
        return f"Not found: {path}"

    entries = parse_session_file(path)
    if not entries:
        return "No entries in session."

    # Find target indices
    target_indices: set[int] = set()

    if refs:
        ref_set = set(refs)
        for i, entry in enumerate(entries):
            if entry.ref in ref_set:
                target_indices.add(i)

    if keywords:
        kw_patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]
        for i, entry in enumerate(entries):
            full_text = _entry_full_text(entry)
            if any(p.search(full_text) for p in kw_patterns):
                target_indices.add(i)

    if not target_indices:
        return "No matching entries found."

    # Build windows, merge overlapping
    windows: list[tuple[int, int]] = []
    for idx in sorted(target_indices):
        start = max(0, idx - window)
        end = min(len(entries) - 1, idx + window)
        if windows and start <= windows[-1][1] + 1:
            windows[-1] = (windows[-1][0], end)
        else:
            windows.append((start, end))

    # Format as markdown
    parts: list[str] = []
    parts.append(f"# Session excerpt: {session_id[:8]}")
    parts.append(f"**Project:** {project_dir}")
    parts.append(f"**Matches:** {len(target_indices)} entries\n")

    for wi, (start, end) in enumerate(windows):
        if wi > 0:
            parts.append("\n---\n")
        for i in range(start, end + 1):
            e = entries[i]
            marker = " **>>**" if i in target_indices else ""
            ref_str = f" [{e.ref}]" if e.ref else ""

            if e.entry_type == EntryType.USER_PROMPT:
                # Show full user prompt content
                text = e.content
                if e.detail and "full_text" in e.detail:
                    text = e.detail["full_text"]
                parts.append(f"### User{ref_str}{marker}")
                parts.append(text)
                parts.append("")
            elif e.entry_type == EntryType.AGENT_ANSWER:
                text = e.content
                if e.detail and "full_text" in e.detail:
                    text = e.detail["full_text"]
                parts.append(f"### Agent{ref_str}{marker}")
                parts.append(text)
                parts.append("")
            elif e.entry_type == EntryType.SKILL_INVOCATION:
                parts.append(f"*Skill: {e.content}*{marker}")
                parts.append("")
            elif e.entry_type == EntryType.TOOL_CALL:
                tool_summary = e.content[:80]
                parts.append(f"*Tool: {tool_summary}*{ref_str}{marker}")
                if i in target_indices and e.detail:
                    # Show detail for matched tool entries
                    if "output" in e.detail:
                        out = str(e.detail["output"])[:500]
                        parts.append(f"```\n{out}\n```")
                parts.append("")
            elif e.entry_type == EntryType.INTERRUPT:
                parts.append(f"*{e.content}*{marker}")
                parts.append("")
            elif e.entry_type == EntryType.TOOL_INTERACTIVE:
                parts.append(f"*Interactive: {e.content[:80]}*{ref_str}{marker}")
                parts.append("")

    return "\n".join(parts)


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
            json.dumps([sf.model_dump() for sf in results], indent=2, default=str)
        )
    else:
        # Group by project_dir for summary display
        by_project: dict[str, int] = defaultdict(int)
        for sf in results:
            by_project[sf.project_dir] += 1
        for project_dir, count in sorted(by_project.items()):
            click.echo(f"{project_dir}: {count} sessions")


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
    if result.merge_parents:
        click.echo(
            f"Merge commits with worktree provenance: {len(result.merge_parents)}"
        )
        for mh, dirs in result.merge_parents.items():
            click.echo(f"  {mh[:12]}  → {', '.join(Path(d).name for d in dirs)}")


@cli.command()
@click.option(
    "--project",
    "projects",
    multiple=True,
    required=True,
    help="Project directory path(s) to search (repeatable)",
)
@click.option(
    "--keyword",
    "keywords",
    multiple=True,
    required=True,
    help="Keyword(s) to search for (repeatable)",
)
@click.option("--case-sensitive", is_flag=True, help="Case-sensitive matching")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def search(
    projects: tuple[str, ...],
    keywords: tuple[str, ...],
    case_sensitive: bool,
    fmt: str,
) -> None:
    """Stage 5: search sessions for keyword matches across projects."""
    hits = search_sessions(list(projects), list(keywords), case_sensitive)
    if fmt == "json":
        click.echo(json.dumps([h.model_dump() for h in hits], indent=2, default=str))
        return
    # Group by session for summary
    by_session: dict[str, list[SearchHit]] = defaultdict(list)
    for h in hits:
        by_session[h.session_id].append(h)
    click.echo(f"Matches: {len(hits)} entries across {len(by_session)} sessions\n")
    for sid, session_hits in sorted(
        by_session.items(), key=lambda x: x[1][0].timestamp
    ):
        kws = sorted({h.keyword for h in session_hits})
        refs = [h.ref for h in session_hits if h.ref]
        click.echo(
            f"{session_hits[0].timestamp[:19]}  {sid[:8]}  "
            f"[{', '.join(kws)}]  "
            f"{len(session_hits)} hits  "
            f"refs: {', '.join(refs[:5])}"
        )
        click.echo(f"  project: {session_hits[0].project_dir}")


@cli.command()
@click.argument("session_id")
@click.option("--project", required=True, help="Project directory (absolute path)")
@click.option("--ref", "refs", multiple=True, help="Entry ref(s) to excerpt (e.g. t42)")
@click.option(
    "--keyword", "keywords", multiple=True, help="Keyword(s) to find and excerpt"
)
@click.option("--window", default=5, help="Number of entries before/after match")
def excerpt(
    session_id: str,
    project: str,
    refs: tuple[str, ...],
    keywords: tuple[str, ...],
    window: int,
) -> None:
    """Stage 6: extract conversation excerpts around matches."""
    if not refs and not keywords:
        click.echo("Provide --ref or --keyword to locate excerpt targets.", err=True)
        raise SystemExit(1)
    result = extract_excerpts(
        session_id,
        project,
        refs=list(refs) if refs else None,
        keywords=list(keywords) if keywords else None,
        window=window,
    )
    click.echo(result)


if __name__ == "__main__":
    cli()
