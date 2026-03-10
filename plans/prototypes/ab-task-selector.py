#!/usr/bin/env python3
"""Select task contexts for A/B testing from session history.

Two strategies:
  1. Sessions with /how invocations (Skill tool or _recall resolve CLI)
  2. Diverse task contexts from any session (for forced selection, prior /how
     usage is not required — any task can exercise index recognition)

Outputs JSON suitable for the forced selection harness.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from claudeutils.paths import encode_project_path

RECALL_HOW_RE = re.compile(r'_recall\s+resolve\b[^"]*"how\s+([^"]+)"')


def _extract_text(msg: dict) -> str:
    """Extract text content from a message."""
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def _is_user_task_message(text: str) -> bool:
    """Filter for messages that describe a task (not system/meta content)."""
    if len(text) < 15 or len(text) > 500:
        return False
    skip_markers = [
        "<system-reminder>",
        "<command-",
        "[Request interrupted",
        "```",  # code blocks are context, not task descriptions
    ]
    for marker in skip_markers:
        if marker in text:
            return False
    # Skip single-word/shortcut commands
    stripped = text.strip()
    if len(stripped.split()) < 3:
        return False
    return True


def _load_entries(jsonl_file: Path) -> list[dict]:
    """Load JSONL entries from a session file."""
    entries = []
    try:
        for line in jsonl_file.read_text().splitlines():
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    return entries


def _find_how_calls(entries: list[dict]) -> list[dict]:
    """Find /how invocations in entries (Skill tool + CLI resolve)."""
    how_calls = []
    for i, entry in enumerate(entries):
        msg = entry.get("message", {})
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")

        # Check Skill tool calls
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                inp = block.get("input", {})
                if not isinstance(inp, dict):
                    continue
                # Skill tool: skill="how"
                if inp.get("skill") == "how":
                    args = inp.get("args", "").strip()
                    if args:
                        how_calls.append(
                            {"trigger": args, "entry_index": i, "source": "skill"}
                        )
                # Bash tool: _recall resolve "how ..."
                cmd = inp.get("command", "")
                if isinstance(cmd, str):
                    for m in RECALL_HOW_RE.finditer(cmd):
                        trigger = m.group(1).strip().rstrip('"')
                        if trigger and len(trigger) < 80:
                            how_calls.append(
                                {"trigger": trigger, "entry_index": i, "source": "cli"}
                            )

        # Check string content for CLI patterns
        if isinstance(content, str):
            for m in RECALL_HOW_RE.finditer(content):
                trigger = m.group(1).strip().rstrip('"')
                if trigger and len(trigger) < 80:
                    how_calls.append(
                        {"trigger": trigger, "entry_index": i, "source": "cli"}
                    )

    return how_calls


def _extract_task_near(entries: list[dict], index: int, window: int = 10) -> str | None:
    """Extract best task description from user messages near an index."""
    candidates = []
    for j in range(max(0, index - window), min(len(entries), index + 2)):
        msg = entries[j].get("message", {})
        if not isinstance(msg, dict) or msg.get("role") != "user":
            continue
        text = _extract_text(msg)
        if _is_user_task_message(text):
            candidates.append(text.strip())
    return candidates[-1] if candidates else None


def extract_how_task_contexts(project_path: str) -> list[dict]:
    """Strategy 1: Tasks from sessions with /how invocations."""
    projects_dir = Path.home() / ".claude" / "projects"
    encoded = encode_project_path(project_path)

    tasks = []
    seen_triggers = set()

    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir() or not history_dir.name.startswith(encoded):
            continue
        for jsonl_file in sorted(history_dir.glob("*.jsonl")):
            # Skip sub-agent files
            if "/subagents/" in str(jsonl_file):
                continue
            entries = _load_entries(jsonl_file)
            how_calls = _find_how_calls(entries)
            if not how_calls:
                continue

            trigger_key = frozenset(h["trigger"].lower() for h in how_calls)
            if trigger_key in seen_triggers:
                continue
            seen_triggers.add(trigger_key)

            # Get context near the first /how call
            desc = _extract_task_near(entries, how_calls[0]["entry_index"])
            if not desc:
                continue

            tasks.append(
                {
                    "description": desc,
                    "how_queries": list({h["trigger"] for h in how_calls}),
                    "session_id": jsonl_file.stem[:8],
                    "source": "how_session",
                }
            )

    return tasks


def extract_diverse_task_contexts(project_path: str, max_tasks: int = 20) -> list[dict]:
    """Strategy 2: Diverse task contexts from any session.

    For forced selection, we need tasks that *could* exercise index recognition.
    Extract the first substantive user message from diverse sessions.
    """
    projects_dir = Path.home() / ".claude" / "projects"
    encoded = encode_project_path(project_path)

    tasks = []
    seen_descs = set()

    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir() or not history_dir.name.startswith(encoded):
            continue
        for jsonl_file in sorted(history_dir.glob("*.jsonl")):
            if "/subagents/" in str(jsonl_file):
                continue
            entries = _load_entries(jsonl_file)
            if len(entries) < 5:
                continue

            # Find first substantive user message
            for entry in entries[:20]:
                msg = entry.get("message", {})
                if not isinstance(msg, dict) or msg.get("role") != "user":
                    continue
                text = _extract_text(msg)
                if _is_user_task_message(text):
                    normalized = text.strip().lower()[:80]
                    if normalized not in seen_descs:
                        seen_descs.add(normalized)
                        tasks.append(
                            {
                                "description": text.strip(),
                                "how_queries": [],
                                "session_id": jsonl_file.stem[:8],
                                "source": "diverse",
                            }
                        )
                    break

            if len(tasks) >= max_tasks:
                break

    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Select task contexts for A/B test")
    parser.add_argument("project", help="Project path (for session history lookup)")
    parser.add_argument("-o", "--output", required=True, help="Output JSON path")
    parser.add_argument("-n", "--max-tasks", type=int, default=20, help="Max tasks")
    args = parser.parse_args()

    project = args.project

    # Strategy 1: sessions with /how
    how_tasks = extract_how_task_contexts(project)
    print(f"Strategy 1 (sessions with /how): {len(how_tasks)} tasks")

    # Strategy 2: diverse sessions
    diverse_tasks = extract_diverse_task_contexts(
        project, max_tasks=args.max_tasks + 10
    )
    print(f"Strategy 2 (diverse sessions):   {len(diverse_tasks)} tasks")

    # Merge: prefer how-session tasks, fill with diverse
    seen_sessions = {t["session_id"] for t in how_tasks}
    merged = list(how_tasks)
    for t in diverse_tasks:
        if t["session_id"] not in seen_sessions and len(merged) < args.max_tasks:
            merged.append(t)
            seen_sessions.add(t["session_id"])

    # Assign IDs
    for i, task in enumerate(merged):
        task["task_id"] = f"task-{i:03d}"

    print(f"\nMerged: {len(merged)} tasks")
    print()

    for task in merged:
        source_tag = "[how]" if task["source"] == "how_session" else "[div]"
        print(f"[{task['task_id']}] {source_tag} session={task['session_id']}")
        print(f"  {task['description'][:120]}")
        if task["how_queries"]:
            print(f"  /how: {', '.join(task['how_queries'][:3])}")
        print()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2))
    print(f"Written to: {out_path}")


if __name__ == "__main__":
    main()
