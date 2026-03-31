# Step 2.1

**Plan**: `plans/plugin-migration/runbook-phase-2.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage.
Phase 5 must complete first (`.edify.yaml` exists for setup hook to read/update).

**Step numbering note:** Step 2.2 (originally "Apply hook script fixes from audit") was absorbed into Step 2.1 during /proof. Step 2.4 (originally "Wire setup hook into hooks.json") was absorbed into Step 2.3 during /proof. The gaps in step numbering are intentional — outline requirements traceability uses original step IDs.

---

---

## Step 2.1: Audit hook scripts for env var usage

**Objective**: Audit 4 hook scripts for `$CLAUDE_PROJECT_DIR` usage and hardcoded paths that may not resolve correctly under plugin context.

**Prerequisites**:
- Read outline.md Component 2 hook script changes table (authoritative list of which scripts need audit)
- Read each of the 4 scripts:
  - `plugin/hooks/pretooluse-recipe-redirect.py`
  - `plugin/hooks/pretooluse-recall-check.py`
  - `plugin/hooks/sessionstart-health.sh`
  - `plugin/hooks/stop-health-fallback.sh`

**Implementation**:
1. For each script, check:
   - Uses of `$CLAUDE_PROJECT_DIR` — these are correct (available in all hook types, resolves to project root)
   - Hardcoded `plugin/` paths — these need `$CLAUDE_PLUGIN_ROOT` substitution (or `$EDIFY_PLUGIN_ROOT` after setup hook runs)
   - Relative path references — must use absolute paths via env vars
2. Record findings per script in a report at `plans/plugin-migration/reports/hook-audit.md`:
   - Script name
   - Finding: no-change-needed OR specific edits required (with line numbers)
   - Rationale
3. Apply fixes per audit findings:
   - Replace hardcoded `plugin/` paths with `$CLAUDE_PLUGIN_ROOT` or `$EDIFY_PLUGIN_ROOT`
   - Fix any relative path references to use absolute resolution
4. Delete `plugin/hooks/pretooluse-symlink-redirect.sh` — purpose eliminated by plugin migration
5. Verify no remaining bare references: `grep -r 'plugin/' plugin/hooks/*.py plugin/hooks/*.sh` returns no matches (except comments)

**Expected Outcome**:
- `plans/plugin-migration/reports/hook-audit.md` exists with per-script findings
- Each script classified as no-change or with specific edits listed
- Audit fixes applied to all scripts requiring changes
- `pretooluse-symlink-redirect.sh` deleted
- No remaining bare `plugin/` references in hook scripts

**Error Conditions**:
- If a script uses env vars not available in plugin context → escalate (design assumption violated)
- If a script has complex path resolution logic → document and escalate for careful review
- If audit found no changes needed → skip fix step, proceed to deletion
- If grep finds unexpected references → investigate and fix or escalate

**Validation**:
- Audit report exists with entries for all 4 scripts
- No scripts left unaudited
- `grep -r 'plugin/' plugin/hooks/*.py plugin/hooks/*.sh` returns no matches (except comments)
- `ls plugin/hooks/pretooluse-symlink-redirect.sh` returns "No such file"

---
