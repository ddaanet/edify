#!/usr/bin/env python3
import json

# Run from project root
d = json.load(open("agent-core/hooks/hooks.json"))
assert "hooks" in d, "Missing 'hooks' wrapper key"
print("Events:", list(d["hooks"].keys()))

# Count all hook entries across all events
total = 0
for event, entries in d["hooks"].items():
    for entry in entries:
        total += len(entry.get("hooks", []))
        print(f"  {event}: {[h['command'] for h in entry.get('hooks', [])]}")

print(f"Total hook entries: {total}")
assert total == 9, f"Expected 9 hook entries, got {total}"
print("PASS: 9 hook entries confirmed")
