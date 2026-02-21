# Step 3.2

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 3.2: Validate Auto-Format Behavior

**Objective:** Confirm the script handles edge cases correctly: non-.py skip, missing file, real .py formatting.

**Script Evaluation:** Small — validation commands only, no new files.

**Execution Model:** Haiku

**Implementation:**

```bash
# Verify script exists and is executable
test -x agent-core/hooks/posttooluse-autoformat.sh && echo "✓ Script exists and executable"

# Verify non-.py is skipped (exit 0, no output)
result=$(echo '{"tool_name":"Edit","tool_input":{"file_path":"agent-core/justfile"}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh 2>&1)
[ -z "$result" ] && echo "✓ Non-.py file skipped silently"

# Verify missing file_path is handled gracefully
result=$(echo '{}' | bash agent-core/hooks/posttooluse-autoformat.sh 2>&1)
echo "Exit code: $?" && echo "Output: '$result'"
# Expected: exit 0, no crash

# Verify ruff runs on a real Python file without crashing
echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"agent-core/bin/learning-ages.py\"}}" \
  | bash agent-core/hooks/posttooluse-autoformat.sh
echo "Exit code: $?" # Expected: 0
```

**Expected Outcome:** All validation checks pass — script handles edge cases gracefully, no crashes, non-.py files skipped.

**Error Conditions:**
- Any validation command exits non-zero → diagnose and fix script
- Script crashes on `{}` input → fix empty-input guard in Step 3.1

**Validation:**
- All check commands above exit 0
- `wc -l agent-core/hooks/posttooluse-autoformat.sh` → between 20-50 lines (compact Bash)

---


**Success criteria:**
- `agent-core/hooks/posttooluse-autoformat.sh` exists with execute permissions
- All Step 3.2 validation checks pass
- Script handles non-.py, empty input, and missing tool gracefully
- `pytest tests/ -v` → all existing tests still pass (no regression)

---
name: hook-batch-phase-4
model: haiku
---

# Phase 4: Session Health Checks

**Type:** General
**Target files:**
- `agent-core/bin/learning-ages.py` (modify — add `--summary` flag)
- `agent-core/hooks/sessionstart-health.sh` (new)
- `agent-core/hooks/stop-health-fallback.sh` (new)

**Design ref:** `plans/hook-batch/outline.md` (Phase 4)

**Prerequisites:**
- Read `agent-core/bin/learning-ages.py` full file — understand main() structure: `total_entries`, `entries_7plus`, `entries_with_ages`, `staleness_days` variables computed before report generation
- Note: `--summary` flag should reuse existing computation variables, not duplicate logic
- Read `agent-core/hooks/sessionstart-health.sh` — verify does NOT exist yet
- Verify SessionStart hook input JSON format includes `session_id` field (check Claude Code docs or hook testing)

**Key decisions:**
- D-4: Dual delivery — SessionStart (primary) + Stop fallback (handles #10373 for new sessions)
- Flag file `$TMPDIR/health-{session_id}` coordinates both scripts
- D-1: Command hooks (type: command)
- D-2: Bash for both scripts (simple command orchestration)
- SessionStart output: systemMessage (user-visible health status, not agent context injection)
- Stop output: systemMessage (same format, only when firing as fallback)
- Three health checks: git dirty tree, learnings health, stale worktrees

---
