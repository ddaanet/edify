# Cycle 2.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 2

---

**GREEN Phase:**

**Implementation:** Replace `.strip()` with format-preserving trim

**Behavior:**
- `git_status()` returns `result.stdout.rstrip('\n')` — preserves leading spaces per line
- Empty stdout → empty string (unchanged)
- `git_diff()` similarly changed for consistency (though diff doesn't have same issue)

**Changes:**
- File: `git.py`
  Action: Change `return result.stdout.strip()` to `return result.stdout.rstrip('\n')`
  Location: `git_status` (line 98), optionally `git_diff` (line 118)

**Verify GREEN:** `just green`
