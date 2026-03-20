# Step 1.2

**Plan**: `plans/plugin-migration/runbook-phase-1.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Create the plugin structure inside existing `agent-core/` directory. Checkpoint at end gates all downstream phases.

---

---

## Step 1.2: Create plugin hooks.json in wrapper format

**Objective**: Rewrite `agent-core/hooks/hooks.json` to contain all 9 surviving hook definitions in wrapper format, with `$CLAUDE_PLUGIN_ROOT` paths.

**Prerequisites**:
- Read `.claude/settings.visible.json` hooks section (current hook bindings — source of truth for matchers and event types)
- Read `agent-core/hooks/hooks.json` (current subset — will be fully rewritten)
- Read `plans/plugin-migration/outline.md` Component 2 hook inventory table (authoritative list of all hooks and their matchers)

**Implementation**:
1. Rewrite `agent-core/hooks/hooks.json` in wrapper format per D-4:
   ```json
   {
     "hooks": {
       "PreToolUse": [...],
       "PostToolUse": [...],
       "UserPromptSubmit": [...],
       "SessionStart": [...],
       "Stop": [...]
     }
   }
   ```
2. Include all 9 surviving hooks with correct matchers:
   - `pretooluse-block-tmp.sh` — PreToolUse, matcher: `Write|Edit`
   - `submodule-safety.py` — PreToolUse, matcher: `Bash` AND PostToolUse, matcher: `Bash` (two entries)
   - `pretooluse-recipe-redirect.py` — PreToolUse, matcher: `Bash`
   - `pretooluse-recall-check.py` — PreToolUse, matcher: `Task`
   - `posttooluse-autoformat.sh` — PostToolUse, matcher: `Write|Edit`
   - `userpromptsubmit-shortcuts.py` — UserPromptSubmit (no matcher)
   - `sessionstart-health.sh` — SessionStart, matcher: `*`
   - `stop-health-fallback.sh` — Stop, matcher: `*`
3. All command paths use `$CLAUDE_PLUGIN_ROOT/hooks/` prefix (not `$CLAUDE_PROJECT_DIR`)
4. Omit `pretooluse-symlink-redirect.sh` (deleted in Phase 2)
5. Preserve existing command prefixes where needed (`python3`, `bash`)

**Expected Outcome**:
- `agent-core/hooks/hooks.json` contains wrapper format with all 5 event types
- 9 hook entries total (submodule-safety appears in both PreToolUse and PostToolUse)
- All paths use `$CLAUDE_PLUGIN_ROOT/hooks/`

**Error Conditions**:
- If JSON validation fails → fix syntax before proceeding
- If hook count doesn't match 9 → verify against `plans/plugin-migration/outline.md` Component 2 table

**Validation**:
- `python3 -c "import json; d=json.load(open('agent-core/hooks/hooks.json')); assert 'hooks' in d; print('Events:', list(d['hooks'].keys()))"`
- Count hook entries across all events equals 9

---
