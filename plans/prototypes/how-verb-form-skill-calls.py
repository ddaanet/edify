#!/usr/bin/env python3
"""Extract only Skill tool invocations of /how — cleanest signal for agent query
patterns."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from claudeutils.paths import encode_project_path

INFINITIVE_RE = re.compile(r"^to\s+(\w+)\b")
GERUND_RE = re.compile(r"^(\w+ing)\b")
BARE_RE = re.compile(r"^(\w+)\b")
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

    queries: list[tuple[str, str]] = []  # (args, session_id)

    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir() or not history_dir.name.startswith(encoded):
            continue
        for jsonl_file in sorted(history_dir.glob("*.jsonl")):
            try:
                for line in jsonl_file.read_text().splitlines():
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg = entry.get("message", {})
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content")
                    if not isinstance(content, list):
                        continue

                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") != "tool_use":
                            continue
                        inp = block.get("input", {})
                        if not isinstance(inp, dict):
                            continue
                        if inp.get("skill") == "how":
                            args = inp.get("args", "").strip()
                            if args:
                                queries.append((args, jsonl_file.stem[:8]))
            except Exception:
                continue

    # Deduplicate by (query, session)
    seen = set()
    unique = []
    for args, sid in queries:
        key = (args.lower(), sid)
        if key not in seen:
            seen.add(key)
            unique.append(args)

    print(f"Skill tool /how invocations: {len(unique)}")
    print()

    form_counts = Counter(classify(q) for q in unique)
    print("=== Verb Form Distribution (Skill tool only) ===")
    for form, count in form_counts.most_common():
        pct = count / len(unique) * 100 if unique else 0
        print(f"  {form:<15} {count:>4} ({pct:.1f}%)")
    print()

    print("=== All Queries ===")
    for q in sorted(set(q.lower() for q in unique)):
        form = classify(q)
        print(f"  [{form:>10}] /how {q}")


if __name__ == "__main__":
    main()
