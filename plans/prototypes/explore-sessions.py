#!/usr/bin/env python3
"""Explore session JSONL format across all ~/code/ projects."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
CODE_PREFIX = "-Users-david-code"
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
)

# Count sessions per project
project_counts = {}
total = 0
for d in sorted(PROJECTS_DIR.iterdir()):
    if d.is_dir() and d.name.startswith(CODE_PREFIX):
        sessions = [f for f in d.glob("*.jsonl") if UUID_RE.match(f.name)]
        if sessions:
            label = d.name[len(CODE_PREFIX) + 1 :] or "(root)"
            project_counts[label] = len(sessions)
            total += len(sessions)

print("=== Sessions per project ===")
for label, count in sorted(project_counts.items(), key=lambda x: -x[1]):
    print(f"  {label}: {count}")
print(f"  TOTAL: {total}")

# Analyze entry types across a sample of sessions
print("\n=== Entry type analysis (largest 5 sessions) ===")
all_sessions = []
for d in PROJECTS_DIR.iterdir():
    if d.is_dir() and d.name.startswith(CODE_PREFIX):
        all_sessions.extend(f for f in d.glob("*.jsonl") if UUID_RE.match(f.name))

# Sort by size (largest first)
all_sessions.sort(key=lambda f: f.stat().st_size, reverse=True)

global_types = Counter()
subtype_examples = defaultdict(list)

for sf in all_sessions[:5]:
    types = Counter()
    for line in sf.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
            t = e.get("type", "?")
            types[t] += 1
            global_types[t] += 1

            # Collect subtypes
            st = e.get("subtype")
            if st and len(subtype_examples[f"{t}/{st}"]) < 1:
                subtype_examples[f"{t}/{st}"].append(sf.name[:12])
        except json.JSONDecodeError:
            pass

    proj = sf.parent.name[len(CODE_PREFIX) + 1 :] or "(root)"
    size_kb = sf.stat().st_size // 1024
    print(f"\n  {proj}/{sf.name[:12]}... ({size_kb}KB)")
    for t, c in types.most_common():
        print(f"    {t}: {c}")

print("\n=== Global type distribution ===")
for t, c in global_types.most_common():
    print(f"  {t}: {c}")

if subtype_examples:
    print("\n=== Subtypes found ===")
    for st in sorted(subtype_examples):
        print(f"  {st}")

# Analyze content block types in assistant messages
print("\n=== Assistant content block types (sample) ===")
block_types = Counter()
interactive_tools = Counter()

for sf in all_sessions[:10]:
    for line in sf.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
            if e.get("type") != "assistant":
                continue
            content = e.get("message", {}).get("content", "")
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict):
                    continue
                bt = b.get("type", "?")
                block_types[bt] += 1
                if bt == "tool_use":
                    name = b.get("name", "?")
                    interactive_tools[name] += 1
        except json.JSONDecodeError:
            pass

for bt, c in block_types.most_common():
    print(f"  {bt}: {c}")

print("\n=== Tool usage frequency (top 20) ===")
for name, c in interactive_tools.most_common(20):
    print(f"  {name}: {c}")

# Check for interrupt patterns
print("\n=== Interrupt detection ===")
interrupt_count = 0
interrupt_examples = []
for sf in all_sessions[:20]:
    prev_type = None
    for line in sf.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
            t = e.get("type")
            content = e.get("message", {}).get("content", "")

            # Check for "[Request interrupted by user]" pattern
            if isinstance(content, str) and "interrupted" in content.lower():
                interrupt_count += 1
                if len(interrupt_examples) < 3:
                    interrupt_examples.append(str(content)[:100])

            # queue-operation might indicate interrupts
            if t == "queue-operation":
                op = e.get("operation", "")
                if op not in ("enqueue",):
                    interrupt_count += 1

            prev_type = t
        except json.JSONDecodeError:
            pass

print(f"  Interrupt signals found: {interrupt_count}")
for ex in interrupt_examples:
    print(f"  Example: {ex}")
