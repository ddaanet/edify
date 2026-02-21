# Step 4.2

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 4

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
