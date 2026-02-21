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

## Step 4.1: learning-ages.py --summary Flag

**Objective:** Add `--summary` flag to `agent-core/bin/learning-ages.py` that outputs a single-line health status instead of the full markdown report. Used by both health scripts.

**Script Evaluation:** Small — detect flag in sys.argv, add conditional output path reusing existing variables.

**Execution Model:** Haiku

**Prerequisite:** Read `agent-core/bin/learning-ages.py` main() lines 156-220 — identify where `total_entries`, `entries_7plus`, and `staleness_days` are computed relative to the report generation section.

**Implementation:**

Add `--summary` detection AFTER the existing computation block (after line 193 where `entries_7plus` is computed, before the `print("# Learning Ages Report")` line). The flag branches the output path, not the computation:
```
# --summary: branch output after computation, reuse existing variables
if '--summary' in sys.argv:
    [print one-liner summary using total_entries, entries_7plus, staleness_days]
    sys.exit(0)

# Normal: full markdown report follows
print("# Learning Ages Report")
...
```

One-liner output format:
- If consolidation date known: `"{total_entries} entries ({entries_7plus} ≥7 days, consolidation {staleness_days}d ago)"`
- If no prior consolidation: `"{total_entries} entries ({entries_7plus} ≥7 days, no prior consolidation)"`

Note: `--summary` runs full git blame computation (same as normal report). Acceptable latency for a once-per-session hook.

Argument detection: `'--summary' in sys.argv` (no argparse needed — simple flag check, single flag).

**Expected Outcome:**
```bash
python3 agent-core/bin/learning-ages.py agents/learnings.md --summary
# Output (one line): "47 entries (12 ≥7 days, consolidation 8d ago)"
# Exit: 0
```

**Error Conditions:**
- File not found still exits 1 with error to stderr (unchanged)
- No learning entries still exits 1 with error (unchanged)
- `--summary` with git blame errors: tolerate gracefully — use `entries_with_ages` that were successfully retrieved

**Validation:**
```bash
# Verify one-liner output: exactly 1 line matching expected format
output=$(python3 agent-core/bin/learning-ages.py agents/learnings.md --summary)
lines=$(echo "$output" | wc -l | tr -d ' ')
echo "Lines: $lines"  # Expected: 1
echo "Content: $output"
# Expected format A (prior consolidation): "<N> entries (<M> ≥7 days, consolidation <D>d ago)"
# Expected format B (no prior consolidation): "<N> entries (<M> ≥7 days, no prior consolidation)"
echo "$output" | grep -E "^[0-9]+ entries \([0-9]+ ≥7 days" || echo "FAIL: format mismatch"

# Verify normal mode still works (no regression)
python3 agent-core/bin/learning-ages.py agents/learnings.md | head -5
# Expected: first line is "# Learning Ages Report" (unchanged behavior)
python3 agent-core/bin/learning-ages.py agents/learnings.md | head -1 | grep -q "# Learning Ages Report" && echo "✓ Normal mode unchanged"
```

---

## Step 4.2: SessionStart Health Script

**Objective:** Create `agent-core/hooks/sessionstart-health.sh` that fires on session start, runs 3 health checks, writes flag file, outputs systemMessage.

**Script Evaluation:** Medium — JSON stdin parsing, 3 health checks including worktree age calculation, flag file coordination.

**Execution Model:** Haiku

**Prerequisite:**
- Verify Step 4.1 complete: `python3 agent-core/bin/learning-ages.py agents/learnings.md --summary` works
- Verify `agent-core/hooks/sessionstart-health.sh` does NOT exist

**Implementation:**

Script structure:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Extract session_id from stdin
session_id=$(python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("session_id",""))' 2>/dev/null || echo "")

# Write flag file (mark that SessionStart fired for this session)
if [ -n "$session_id" ]; then
    touch "$TMPDIR/health-${session_id}"
fi

# Health checks
[run 3 checks, collect results]

# Output systemMessage
[print JSON with systemMessage]
```

**Health check 1 — Dirty tree:**
```bash
dirty=$(git status --porcelain 2>/dev/null)
if [ -n "$dirty" ]; then
    tree_status="⚠️ Dirty tree ($(echo "$dirty" | wc -l | tr -d ' ') files)"
else
    tree_status="✓ Clean tree"
fi
```

**Health check 2 — Learnings health:**
```bash
learnings_status=$(python3 "$CLAUDE_PROJECT_DIR/agent-core/bin/learning-ages.py" \
  "$CLAUDE_PROJECT_DIR/agents/learnings.md" --summary 2>/dev/null \
  || echo "⚠️ Learnings status unavailable")
```

**Health check 3 — Stale worktrees:**
Use `git worktree list --porcelain` to get worktree paths. For each non-main worktree, check last commit timestamp:
```bash
while IFS= read -r wt_path; do
    last_ts=$(git -C "$wt_path" log -1 --format="%ct" 2>/dev/null || echo "0")
    now=$(date +%s)
    age_days=$(( (now - last_ts) / 86400 ))
    if [ "$age_days" -gt 7 ]; then
        stale_wt="$stale_wt\n  $(basename "$wt_path") (${age_days}d)"
    fi
done < <(git worktree list --porcelain | grep "^worktree " | awk '{print $2}' | grep -v "^$(git rev-parse --show-toplevel)$" || true)
```

**Output format:**
```bash
message="Session Health:\n${tree_status}\nLearnings: ${learnings_status}"
[ -n "$stale_wt" ] && message="$message\n⚠️ Stale worktrees:$stale_wt"
printf '{"systemMessage": "%s"}\n' "$(echo "$message" | sed 's/"/\\"/g')"
```

Note: The `\n` in `message=` are literal backslash-n (not shell newlines) when using double-quoted strings in bash. This is intentional — the JSON value contains literal `\n` which Claude Code interprets as newlines in systemMessage rendering. Do NOT use `$'...'` syntax or actual shell newlines in the message variable, as those would break the JSON structure.

Note: Use `$CLAUDE_PROJECT_DIR` for paths to learning-ages.py. This env var is set by Claude Code for command hooks.

**Expected Outcome:** Script created at `agent-core/hooks/sessionstart-health.sh` with execute permissions. On invocation with valid stdin JSON containing session_id, outputs systemMessage with health status and creates flag file in `$TMPDIR`.

**Error Conditions:**
- python3 not available → exit 1, report (critical dependency)
- git not available → exit 1, report
- learning-ages.py fails → use fallback message, don't abort (Step 4.2's check 2 uses `|| echo "unavailable"`)
- session_id empty (missing field) → skip flag file creation, still run checks and output

**Validation:**
```bash
# Make executable
chmod +x agent-core/hooks/sessionstart-health.sh

# Test with fake session_id
echo '{"session_id": "test-session-123"}' \
  | bash agent-core/hooks/sessionstart-health.sh

# Expected: JSON output with systemMessage, no errors

# Verify flag file created
test -f "$TMPDIR/health-test-session-123" && echo "✓ Flag file created"

# Verify output has systemMessage key
echo '{"session_id": "verify-test"}' \
  | bash agent-core/hooks/sessionstart-health.sh \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print("systemMessage" in d)'
# Expected: True
```

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

## Phase 4 Completion

**Success criteria:**
- `python3 agent-core/bin/learning-ages.py agents/learnings.md --summary` → single line output
- `agent-core/hooks/sessionstart-health.sh` exists, executable, passes validation
- `agent-core/hooks/stop-health-fallback.sh` exists, executable, passes validation
- Flag file coordination works: SessionStart writes flag → Stop sees flag → Stop skips
- `pytest tests/ -v` → all existing tests pass (no regression)

**Depends on:** Phase 3 (auto-format hook) is independent, but Phase 4 Step 4.2 depends on Step 4.1 (--summary flag).
