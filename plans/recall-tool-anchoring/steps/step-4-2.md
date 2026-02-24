# Step 4.2

**Plan**: `plans/recall-tool-anchoring/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Step 4.2: Update settings.json

**Objective:** Register hook and add script permissions.
**Script Evaluation:** Direct (inline edit)
**Execution Model:** Sonnet

**Implementation:**
Two edits to `.claude/settings.json`:

1. **Permissions:** Add `"Bash(agent-core/bin/recall-*:*)"` to `permissions.allow` array (after the existing `agent-core/bin/` entries).

2. **Hook registration:** Add new entry to `hooks.PreToolUse` array:
```json
{
  "matcher": "Task",
  "hooks": [
    {
      "type": "command",
      "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/pretooluse-recall-check.py"
    }
  ]
}
```

**Expected Outcome:** `recall-*.sh` scripts callable without permission prompts. Hook fires on every Task tool use.

**Error Conditions:** JSON syntax error → `just precommit` catches it.

**Validation:** `just precommit` passes. Verify JSON is valid.
