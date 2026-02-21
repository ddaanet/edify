# Step 4.3

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Step 4.3: Stop Health Fallback Script

**Objective:** Create `agent-core/hooks/stop-health-fallback.sh` that fires on every Stop event. If SessionStart already ran (flag file exists), skips. If not (new session, handles #10373), runs health checks and displays status.

**Script Evaluation:** Medium — flag file check + same 3 health checks as Step 4.2 (same complexity, just skipped when flag present). "Small" would only apply if the health checks were extracted to a shared helper.

**Execution Model:** Haiku

**Prerequisite:**
- Verify Step 4.2 complete: sessionstart-health.sh exists and flag file logic works
- Verify `agent-core/hooks/stop-health-fallback.sh` does NOT exist

**Implementation:**

Script structure:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Extract session_id from stdin
session_id=$(python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("session_id",""))' 2>/dev/null || echo "")

# Check flag file — if SessionStart already fired, skip
if [ -n "$session_id" ] && [ -f "$TMPDIR/health-${session_id}" ]; then
    exit 0  # SessionStart already displayed health
fi

# Flag file absent: new session (#10373 bypass) — run health checks
if [ -n "$session_id" ]; then
    touch "$TMPDIR/health-${session_id}"
fi

# Run same 3 health checks as sessionstart-health.sh
[same health check logic]

# Output systemMessage
[same output format]
```

Note: Health check logic is identical to sessionstart-health.sh. To avoid drift, both scripts can source a shared function file, OR duplicate the checks (simpler, less coupling). Given the scripts are short, duplication is acceptable for Phase 5 deployment simplicity.

**Expected Outcome:** Script created at `agent-core/hooks/stop-health-fallback.sh`. When invoked:
- If flag file present: silent exit 0
- If flag file absent: runs health checks + creates flag + outputs systemMessage

**Error Conditions:**
- Same as Step 4.2 (learning-ages.py failure, git failure — non-fatal)

**Validation:**
```bash
chmod +x agent-core/hooks/stop-health-fallback.sh

# Test 1: Flag file present → silent skip
touch "$TMPDIR/health-fallback-test"
echo '{"session_id": "fallback-test"}' \
  | bash agent-core/hooks/stop-health-fallback.sh
echo "Exit code: $?"  # Expected: 0, no output

# Test 2: Flag file absent → runs checks
rm -f "$TMPDIR/health-fallback-test2" 2>/dev/null
output=$(echo '{"session_id": "fallback-test2"}' \
  | bash agent-core/hooks/stop-health-fallback.sh)
echo "Has output: $([ -n "$output" ] && echo yes || echo no)"  # Expected: yes
echo "$output" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("systemMessage" in d)'
# Expected: True

# Verify flag file written on fallback fire
test -f "$TMPDIR/health-fallback-test2" && echo "✓ Flag file created by fallback"
```

---


**Success criteria:**
- `python3 agent-core/bin/learning-ages.py agents/learnings.md --summary` → single line output
- `agent-core/hooks/sessionstart-health.sh` exists, executable, passes validation
- `agent-core/hooks/stop-health-fallback.sh` exists, executable, passes validation
- Flag file coordination works: SessionStart writes flag → Stop sees flag → Stop skips
- `pytest tests/ -v` → all existing tests pass (no regression)

**Depends on:** Phase 3 (auto-format hook) is independent, but Phase 4 Step 4.2 depends on Step 4.1 (--summary flag).

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
