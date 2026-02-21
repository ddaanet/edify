# Step 5.2

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Step 5.2: Create sync-hooks-config.py

**Objective:** Create `agent-core/bin/sync-hooks-config.py` that reads hooks.json and merges into `.claude/settings.json`, preserving existing hooks and deduplicating by command string.

**Script Evaluation:** Medium — JSON read/merge/write with dedup logic.

**Execution Model:** Haiku

**Prerequisite:**
- Step 5.1 complete: hooks.json exists
- Read `.claude/settings.json` current hooks section to understand structure

**Implementation:**

Script logic:
1. Find `settings.json`: use `$CLAUDE_PROJECT_DIR` env var if set, else `Path(__file__).parent.parent.parent / '.claude' / 'settings.json'` (agent-core/bin/../.. = project root)
2. Find `hooks.json`: `Path(__file__).parent.parent / 'hooks' / 'hooks.json'` (agent-core/hooks/hooks.json)
3. Read both JSON files
4. For each event key in hooks.json (e.g., "PreToolUse"):
   - Get existing event list from settings.json (or empty list)
   - For each entry in hooks.json event list:
     - Find matching matcher entry in settings.json (by `matcher` field, or no-matcher for UserPromptSubmit)
     - For each hook in the entry's `hooks` list: check if command string already in existing hooks → skip if duplicate
     - Append non-duplicate hooks to matching matcher entry (or create new matcher entry)
5. Write updated settings.json (json.dumps with indent=2, preserve field order)

**Key merge cases:**
- UserPromptSubmit (no matcher): merge hooks into existing no-matcher entry; skip if command already present
- PreToolUse Bash: find existing `{"matcher": "Bash", "hooks": [...]}` entry; append new hooks if not duplicate
- PostToolUse Write|Edit: create new `{"matcher": "Write|Edit", "hooks": [...]}` entry (no existing Write|Edit matcher in PostToolUse)
- SessionStart: create new event key in settings.json hooks (currently absent)
- Stop: create new event key in settings.json hooks (currently absent)

**Idempotency contract:** Running sync-hooks-config.py multiple times produces same result. Command string dedup prevents duplicate entries.

```python
#!/usr/bin/env python3
"""Merge agent-core/hooks/hooks.json into .claude/settings.json.

Idempotent: deduplicates by command string. Preserves existing hooks.
"""
import json
import os
import sys
from pathlib import Path

def find_settings_path():
    """Find .claude/settings.json — use CLAUDE_PROJECT_DIR or parent of agent-core."""
    env_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if env_dir:
        return Path(env_dir) / '.claude' / 'settings.json'
    # agent-core/bin/sync-hooks-config.py → ../.. = project root
    script_dir = Path(__file__).parent
    return script_dir.parent.parent / '.claude' / 'settings.json'
```

**Expected Outcome:** `sync-hooks-config.py` created at `agent-core/bin/sync-hooks-config.py`. When run, merges hooks.json entries into settings.json without duplicates.

**Error Conditions:**
- hooks.json not found → exit 1 with error to stderr: "hooks.json not found at {path}"
- settings.json not found → exit 1: "settings.json not found at {path}"
- JSON parse error → exit 1 with parse error message
- Write failure → exit 1 (settings.json in denyWithinAllow; requires dangerouslyDisableSandbox)

**Note:** This step requires `dangerouslyDisableSandbox: true` — all python3 calls are blocked by `Bash(python3:*)` deny rule.

**Validation:**
```bash
# Dry-run validation: parse the script
python3 -c 'import ast; ast.parse(open("agent-core/bin/sync-hooks-config.py").read()); print("✓ Syntax OK")'

# Test idempotency (requires dangerouslyDisableSandbox):
python3 agent-core/bin/sync-hooks-config.py
python3 agent-core/bin/sync-hooks-config.py  # second run same result
python3 -c 'import json; d=json.load(open(".claude/settings.json")); print(list(d["hooks"].keys()))'
# Expected: [..., "SessionStart", "Stop"]
```

---
