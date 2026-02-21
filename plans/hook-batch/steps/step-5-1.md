# Step 5.1

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 5

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
