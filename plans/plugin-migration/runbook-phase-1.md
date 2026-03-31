### Phase 1: Plugin manifest and structure (type: general, model: sonnet)

Create the plugin structure inside existing `plugin/` directory. Checkpoint at end gates all downstream phases.

---

## Step 1.1: Create plugin manifest

**Objective**: Create `plugin/.claude-plugin/plugin.json` with plugin name and version matching `pyproject.toml`.

**Prerequisites**:
- Read `pyproject.toml` (extract current version — currently `0.0.2`)

**Implementation**:
1. Create directory `plugin/.claude-plugin/`
2. Create `plugin/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "edify",
     "version": "0.0.2",
     "description": "Opinionated agent framework for Claude Code"
   }
   ```
3. Version must match `pyproject.toml` `version` field exactly

**Expected Outcome**:
- `plugin/.claude-plugin/plugin.json` exists with valid JSON
- `name` is `edify`, `version` matches `pyproject.toml`

**Error Conditions**:
- If `.claude-plugin/` directory already exists → check contents, do not overwrite without verifying
- If `pyproject.toml` version format is unexpected → escalate

**Validation**:
- `cat plugin/.claude-plugin/plugin.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['name']=='edify'; print('OK:', d['version'])"`

---

## Step 1.2: Create plugin hooks.json in wrapper format

**Objective**: Rewrite `plugin/hooks/hooks.json` to contain all 9 surviving hook definitions in wrapper format, with `$CLAUDE_PLUGIN_ROOT` paths.

**Prerequisites**:
- Read `.claude/settings.visible.json` hooks section (current hook bindings — source of truth for matchers and event types)
- Read `plugin/hooks/hooks.json` (current subset — will be fully rewritten)
- Read `plans/plugin-migration/outline.md` Component 2 hook inventory table (authoritative list of all hooks and their matchers)

**Implementation**:
1. Rewrite `plugin/hooks/hooks.json` in wrapper format per D-4:
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
- `plugin/hooks/hooks.json` contains wrapper format with all 5 event types
- 9 hook entries total (submodule-safety appears in both PreToolUse and PostToolUse)
- All paths use `$CLAUDE_PLUGIN_ROOT/hooks/`

**Error Conditions**:
- If JSON validation fails → fix syntax before proceeding
- If hook count doesn't match 9 → verify against `plans/plugin-migration/outline.md` Component 2 table

**Validation**:
- `python3 -c "import json; d=json.load(open('plugin/hooks/hooks.json')); assert 'hooks' in d; print('Events:', list(d['hooks'].keys()))"`
- Count hook entries across all events equals 9

---

## Step 1.3: Validate plugin loading (checkpoint)

**Objective**: Verify plugin auto-discovery works with `claude --plugin-dir ./plugin`. Gates all downstream phases.

**Prerequisites**:
- Steps 1.1, 1.2 complete

**Implementation**:

**Automated checks (agent executes directly via `claude -p` headless mode):**

1. **FR-1 Skills**: Verify plugin skills discoverable from a clean directory (no `.claude/`):
   ```bash
   mkdir -p tmp/plugin-verify && cd tmp/plugin-verify && \
     claude -p "list your available slash commands" --plugin-dir ../../plugin 2>&1 | tee ../../tmp/plugin-verify-skills.txt && \
     cd ../..
   ```
   - Output must contain plugin skills (`/design`, `/commit`, `/orchestrate`, `/handoff`)
   - If skills missing → check `plugin.json` format, directory structure
2. **FR-1 Agents**: Verify plugin agents discoverable:
   ```bash
   cd tmp/plugin-verify && \
     claude -p "list your available agents" --plugin-dir ../../plugin 2>&1 | tee ../../tmp/plugin-verify-agents.txt && \
     cd ../..
   ```
   - Output must list agents from `plugin/agents/`
3. **FR-8 Coexistence**: Verify plan-specific agents coexist with plugin agents:
   ```bash
   claude -p "list your available agents" --plugin-dir ./plugin 2>&1 | tee tmp/plugin-verify-coexist.txt
   ```
   - Run from project root (has `.claude/agents/handoff-cli-tool-*.md`)
   - Output must contain both plugin agents AND plan-specific agents — no conflicts
4. **FR-1 Hooks**: Verify hooks fire from plugin:
   ```bash
   cd tmp/plugin-verify && \
     claude -p "write the word test to /tmp/hook-test.txt" --plugin-dir ../../plugin 2>&1 | tee ../../tmp/plugin-verify-hooks.txt && \
     cd ../..
   ```
   - `pretooluse-block-tmp.sh` should block the `/tmp` write — look for hook output in response

**Manual check (STOP — human performs):**

5. **NFR-1 Dev mode reload**: Edit one skill file (add a comment), then re-run check 1. Confirm the edit is reflected (skill content changed). This validates the edit-restart cycle is no slower than symlinks.

**Expected Outcome**:
- Plugin skills, agents, and hooks all discoverable via `--plugin-dir`
- No conflicts between plugin agents and plan-specific agents
- Dev mode reload works: edit-restart-verify cycle confirms change visible on next start

**Error Conditions**:
- If plugin not discovered → check `plugin.json` format, directory structure
- If hooks not loading → check wrapper format matches Claude Code expectations
- If agent conflicts → check namespace prefixing

**Validation**:
- Checks 1-4 must pass (automated, agent verifies output)
- Check 5: STOP and report NFR-1 result to orchestrator
- All downstream phases depend on this checkpoint passing
