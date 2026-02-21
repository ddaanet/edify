---
name: hook-batch-phase-5
model: haiku
---

# Phase 5: Hook Infrastructure + Integration

**Type:** General
**Target files:**
- `agent-core/hooks/hooks.json` (new — config source of truth)
- `agent-core/bin/sync-hooks-config.py` (new — merge helper)
- `agent-core/justfile` (modify — add hooks sync to sync-to-parent recipe)

**Design ref:** `plans/hook-batch/outline.md` (Phase 5)

**Prerequisites:**
- Note: Step 5.3 requires Sonnet model (justfile edit requires careful placement and context); all other steps use phase default haiku.
- Verify Phases 1-4 complete: all 5 hook scripts exist:
  - `agent-core/hooks/userpromptsubmit-shortcuts.py` (existing, Phase 1 modified)
  - `agent-core/hooks/pretooluse-recipe-redirect.py` (Phase 2)
  - `agent-core/hooks/posttooluse-autoformat.sh` (Phase 3)
  - `agent-core/hooks/sessionstart-health.sh` (Phase 4)
  - `agent-core/hooks/stop-health-fallback.sh` (Phase 4)
- Read `.claude/settings.json` hooks section — understand existing hook registrations (3 existing entries: UserPromptSubmit, PreToolUse Write|Edit, PostToolUse Bash). Merge must preserve all.
- Note: `settings.json` is in `denyWithinAllow` → Step 5.2 and 5.3/5.4 require `dangerouslyDisableSandbox: true`

**Key decisions:**
- D-8: hooks.json is config source of truth for agent-core hooks; settings.json is generated output
- Existing project-local hooks (pretooluse-block-tmp.sh, pretooluse-symlink-redirect.sh) stay in `.claude/settings.json` only — NOT in hooks.json (they're project-local, not agent-core portable)
- sync-hooks-config.py is idempotent (dedup by command string)
- sync-to-parent recipe calls sync-hooks-config.py after symlink sync

---

## Step 5.1: Create hooks.json

**Objective:** Create `agent-core/hooks/hooks.json` containing all agent-core hook registrations (5 hook events). This is the source of truth — changes to hooks config happen here, not in settings.json.

**Script Evaluation:** Small — JSON file creation.

**Execution Model:** Haiku

**Prerequisite:** All 5 hook scripts exist (verify above).

**Implementation:**

Create `agent-core/hooks/hooks.json` with this content:

```json
{
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py",
          "timeout": 5
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/pretooluse-recipe-redirect.py"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/posttooluse-autoformat.sh"
        }
      ]
    }
  ],
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/sessionstart-health.sh"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/stop-health-fallback.sh"
        }
      ]
    }
  ]
}
```

**Notes:**
- UserPromptSubmit entry already exists in settings.json — sync-hooks-config.py will dedup by command string
- PreToolUse Bash matcher already exists (submodule-safety.py) — new recipe-redirect hook will be appended to existing matcher's hooks list
- PostToolUse Write|Edit is new (existing is Write|Edit PreToolUse only; PostToolUse only has Bash matcher)
- PostToolUse Bash matcher already exists (submodule-safety.py) — merge must preserve it; sync-hooks-config.py adds Write|Edit entry alongside existing Bash entry
- SessionStart and Stop are new event types not currently in settings.json

**Expected Outcome:** Valid JSON file at `agent-core/hooks/hooks.json`.

**Error Conditions:**
- JSON syntax error → re-validate with `python3 -c 'import json; json.load(open("agent-core/hooks/hooks.json"))'`

**Validation:**
```bash
python3 -c 'import json; d=json.load(open("agent-core/hooks/hooks.json")); print(list(d.keys()))'
# Expected: ['UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'SessionStart', 'Stop']
```

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

## Step 5.3: Update sync-to-parent Recipe

**Objective:** Add `python3 agent-core/bin/sync-hooks-config.py` call to `sync-to-parent` recipe in `agent-core/justfile`.

**Script Evaluation:** Small — single line addition to justfile recipe.

**Execution Model:** Sonnet (justfile edit requires careful placement and context)

**Prerequisite:**
- Read `agent-core/justfile` sync-to-parent recipe — identify end of recipe body for append location
- Step 5.2 complete: sync-hooks-config.py exists

**Implementation:**

Insert before `echo "Sync complete!"` at the end of the `sync-to-parent` recipe body (after the hooks section, before the closing echo):

```just
    echo "Syncing hook configuration..."
    python3 agent-core/bin/sync-hooks-config.py
```

Notes:
- Justfile recipes run from project root (not script directory)
- `agent-core/bin/sync-hooks-config.py` path is relative to project root — correct
- Recipe uses `#!/usr/bin/env bash` shebang with `set -euo pipefail` — script failure aborts sync
- sync-hooks-config.py writes settings.json → requires dangerouslyDisableSandbox when running `just sync-to-parent`
- The hooks section (symlink sync for hook scripts and hooks.json) already exists in sync-to-parent — insert the sync-hooks-config.py call AFTER the existing hooks section

**Expected Outcome:** `sync-to-parent` recipe ends with hook config sync call. Running `just sync-to-parent` deploys both symlinks and hook configuration.

**Error Conditions:**
- sync-hooks-config.py fails → recipe exits non-zero (set -euo pipefail); settings.json unchanged if write failed
  - Step 5.2 implementation must write atomically (write to temp file, rename to settings.json) to prevent partial write on interrupt — verify this is implemented in sync-hooks-config.py before running

**Validation:**
```bash
# Verify recipe contains new line
grep -n "sync-hooks-config" agent-core/justfile
# Expected: line number with "python3 agent-core/bin/sync-hooks-config.py"
```

---

## Step 5.4: Run sync-to-parent + Verify

**Objective:** Execute `just sync-to-parent` to deploy hooks, verify settings.json updated correctly, note restart requirement.

**Script Evaluation:** Direct — verification commands only.

**Execution Model:** Haiku

**Note:** This step requires `dangerouslyDisableSandbox: true` because sync-hooks-config.py writes `.claude/settings.json` (in `denyWithinAllow`).

**Prerequisite:**
- Steps 5.1-5.3 complete
- Clean working tree preferred (sync produces only settings.json changes)

**Implementation:**

```bash
# Run sync-to-parent (requires dangerouslyDisableSandbox for settings.json write)
just sync-to-parent
```

Then verify:
```bash
# Verify all new hook events present
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
hooks = d.get("hooks", {})
print("Events:", list(hooks.keys()))
'
# Expected output includes: SessionStart, Stop, and existing UserPromptSubmit, PreToolUse, PostToolUse

# Verify PreToolUse Bash has both submodule-safety AND recipe-redirect
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
bash_hooks = [e for e in d["hooks"].get("PreToolUse", []) if e.get("matcher") == "Bash"]
if bash_hooks:
    cmds = [h["command"] for h in bash_hooks[0]["hooks"]]
    print("Bash hooks:", cmds)
'
# Expected: both submodule-safety.py and pretooluse-recipe-redirect.py

# Verify existing Write|Edit PreToolUse hooks preserved (block-tmp, symlink-redirect)
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
we_hooks = [e for e in d["hooks"].get("PreToolUse", []) if e.get("matcher") == "Write|Edit"]
if we_hooks:
    cmds = [h["command"] for h in we_hooks[0]["hooks"]]
    print("Write|Edit hooks:", cmds)
'
# Expected: pretooluse-block-tmp.sh and pretooluse-symlink-redirect.sh still present

# Verify PostToolUse Bash (submodule-safety) preserved AND Write|Edit (autoformat) added
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
ptu = d["hooks"].get("PostToolUse", [])
bash_hooks = [e for e in ptu if e.get("matcher") == "Bash"]
we_hooks = [e for e in ptu if e.get("matcher") == "Write|Edit"]
print("PostToolUse Bash hooks:", [h["command"] for h in bash_hooks[0]["hooks"]] if bash_hooks else "MISSING")
print("PostToolUse Write|Edit hooks:", [h["command"] for h in we_hooks[0]["hooks"]] if we_hooks else "MISSING")
'
# Expected: Bash has submodule-safety.py; Write|Edit has posttooluse-autoformat.sh

# Verify UserPromptSubmit not duplicated
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
ups = d["hooks"].get("UserPromptSubmit", [])
all_cmds = [h["command"] for entry in ups for h in entry["hooks"]]
print("UPS commands:", all_cmds)
print("Duplicate?:", len(all_cmds) != len(set(all_cmds)))
'
# Expected: one UPS command, no duplicate
```

**Expected Outcome:** settings.json updated with 5 new/merged hook entries. All existing hooks preserved. No duplicates.

**Post-run note:** Session restart required. Hook scripts are discovered at session start. Note in commit message: "Restart session after deploying to activate new hooks."

**Error Conditions:**
- `just sync-to-parent` fails → check sync-hooks-config.py error output; verify dangerouslyDisableSandbox is set
- Settings verification fails (missing keys) → run sync-hooks-config.py directly with debug output
- Duplicate UPS command detected → investigate dedup logic in sync-hooks-config.py

---

## Phase 5 Completion + Final Integration Note

**Success criteria:**
- `agent-core/hooks/hooks.json` valid JSON with 5 event entries
- `agent-core/bin/sync-hooks-config.py` idempotent, handles all merge cases
- `agent-core/justfile` sync-to-parent calls sync-hooks-config.py
- `.claude/settings.json` has all new hooks merged (verified above)
- All existing hooks preserved: UPS, PreToolUse Write|Edit (block-tmp + symlink-redirect), PostToolUse Bash (submodule-safety)
- `pytest tests/ -v` → all tests pass

**Restart required:** Session restart activates new hooks (agents are discovered at session start).

**Depends on:** All phases 1-4 must be complete before Step 5.4 (sync deploys all scripts).
