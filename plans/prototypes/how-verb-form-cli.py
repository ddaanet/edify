#!/usr/bin/env python3
"""Extract _recall resolve invocations containing 'how' from sessions."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from claudeutils.paths import encode_project_path

# Match Bash tool calls containing _recall resolve with "how" args
RECALL_HOW_RE = re.compile(r'_recall\s+resolve\b.*?"how\s+([^"]+)"', re.DOTALL)
# Also match direct /how via CLI
DIRECT_HOW_RE = re.compile(
    r'claudeutils\s+_(?:when|how)\s+resolve\s+"?how\s+([^"\n]+)"?'
)

INFINITIVE_RE = re.compile(r"^to\s+(\w+)\b")
GERUND_RE = re.compile(r"^(\w+ing)\b")
NOT_GERUND = {
    "string",
    "ring",
    "king",
    "thing",
    "bring",
    "spring",
    "swing",
    "sing",
    "sting",
}


def classify(query: str) -> str:
    q = query.strip().lower()
    if not q:
        return "empty"
    if INFINITIVE_RE.match(q):
        return "infinitive"
    m = GERUND_RE.match(q)
    if m and m.group(1) not in NOT_GERUND:
        return "gerund"
    return "bare"


def main() -> None:
    projects_dir = Path.home() / ".claude" / "projects"
    encoded = encode_project_path("/Users/david/code/claudeutils")

    queries: list[str] = []

    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir() or not history_dir.name.startswith(encoded):
            continue
        for jsonl_file in sorted(history_dir.glob("*.jsonl")):
            try:
                for line in jsonl_file.read_text().splitlines():
                    if "how" not in line.lower():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg = entry.get("message", {})
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content")

                    text = ""
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        for block in content:
                            if not isinstance(block, dict):
                                continue
                            if block.get("type") == "tool_use":
                                inp = block.get("input", {})
                                if isinstance(inp, dict):
                                    cmd = inp.get("command", "")
                                    if isinstance(cmd, str):
                                        text += cmd + "\n"
                            elif block.get("type") == "text":
                                text += block.get("text", "") + "\n"

                    # Extract from _recall resolve "how ..."
                    for m in RECALL_HOW_RE.finditer(text):
                        q = m.group(1).strip().rstrip('"')
                        if len(q) < 80 and not q.startswith("<"):
                            queries.append(q)

                    # Extract from direct CLI
                    for m in DIRECT_HOW_RE.finditer(text):
                        q = m.group(1).strip().rstrip('"')
                        if len(q) < 80 and not q.startswith("<"):
                            queries.append(q)
            except Exception:
                continue

    # Deduplicate
    unique = sorted(set(q.lower().strip() for q in queries))

    print(f"CLI /how queries (unique): {len(unique)}")
    print()

    form_counts = Counter(classify(q) for q in unique)
    print("=== Verb Form Distribution (CLI _recall resolve) ===")
    for form, count in form_counts.most_common():
        pct = count / len(unique) * 100 if unique else 0
        print(f"  {form:<15} {count:>4} ({pct:.1f}%)")
    print()

    print("=== All Queries ===")
    for q in unique:
        form = classify(q)
        print(f"  [{form:>10}] how {q}")


if __name__ == "__main__":
    main()
