#!/usr/bin/env python3
"""Scrape sessions for p:/pending: directives and extract task names from responses."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edify.paths import encode_project_path

PENDING_PATTERN = re.compile(r'^\s*(?:p|pending)\s*:\s*(.+)', re.IGNORECASE)
TASK_NAME_PATTERN = re.compile(r'\*\*(.+?)\*\*')
TASK_LINE_PATTERN = re.compile(r'(?:task\s*(?:name)?|name)\s*:\s*\*?\*?(.+?)\*?\*?\s*$', re.IGNORECASE | re.MULTILINE)

PROJECT_DIRS = [
    Path.home() / "code" / "edify",
]
# Worktree sibling container
wt_container = Path.home() / "code" / "edify-wt"
if wt_container.exists():
    for d in sorted(wt_container.iterdir()):
        if d.is_dir():
            PROJECT_DIRS.append(d)
# Old convention: edify-*
for d in sorted((Path.home() / "code").iterdir()):
    if d.is_dir() and d.name.startswith("edify-") and d.name != "edify-wt":
        PROJECT_DIRS.append(d)


def get_history_dir(project_dir: Path) -> Path:
    return Path.home() / ".claude" / "projects" / encode_project_path(str(project_dir))


def scan_session(session_file: Path) -> list[dict]:
    """Scan a session file for p:/pending: directives and their responses."""
    results = []
    entries = []

    try:
        for line in session_file.read_text().strip().split('\n'):
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        return []

    for i, entry in enumerate(entries):
        if entry.get("type") != "user":
            continue

        msg = entry.get("message", {})
        content = msg.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )

        m = PENDING_PATTERN.match(content.strip())
        if not m:
            continue

        user_text = m.group(1).strip()
        timestamp = entry.get("timestamp", "")

        # Find next assistant response
        response_text = ""
        for j in range(i + 1, min(i + 5, len(entries))):
            if entries[j].get("type") == "assistant":
                resp_msg = entries[j].get("message", {})
                resp_content = resp_msg.get("content", "")
                if isinstance(resp_content, list):
                    resp_content = " ".join(
                        block.get("text", "") for block in resp_content
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                response_text = resp_content
                break

        # Extract task name from response
        task_name = ""
        bold_matches = TASK_NAME_PATTERN.findall(response_text)
        if bold_matches:
            task_name = bold_matches[0]
        else:
            tl = TASK_LINE_PATTERN.search(response_text)
            if tl:
                task_name = tl.group(1).strip()

        results.append({
            "timestamp": timestamp,
            "user_text": user_text[:100],
            "task_name": task_name[:80] if task_name else "(no task name extracted)",
            "session_file": str(session_file.name),
            "response_preview": response_text[:200] if not task_name else "",
        })

    return results


def main():
    all_results = []
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
    )

    for project_dir in PROJECT_DIRS:
        history_dir = get_history_dir(project_dir)
        if not history_dir.exists():
            continue

        session_count = 0
        for session_file in history_dir.glob("*.jsonl"):
            if not uuid_pattern.match(session_file.name):
                continue
            session_count += 1
            results = scan_session(session_file)
            for r in results:
                r["project"] = project_dir.name
            all_results.extend(results)

        if session_count:
            print(f"Scanned {session_count} sessions in {project_dir.name}", file=sys.stderr)

    all_results.sort(key=lambda r: r["timestamp"])

    print(f"Total p:/pending: directives found: {len(all_results)}")
    print(f"{'='*80}")

    for r in all_results:
        ts = r["timestamp"][:10] if r["timestamp"] else "no-date"
        print(f"\n[{ts}] {r['project']}")
        print(f"  User: p: {r['user_text']}")
        print(f"  Task: {r['task_name']}")
        if r["response_preview"]:
            preview = r["response_preview"][:120].replace('\n', ' ')
            print(f"  Response: {preview}...")

    print(f"\n{'='*80}")
    print(f"Task names for git correlation:")
    for r in all_results:
        ts = r["timestamp"][:10] if r["timestamp"] else "?"
        print(f"  [{ts}] {r['task_name']}")


if __name__ == "__main__":
    main()
