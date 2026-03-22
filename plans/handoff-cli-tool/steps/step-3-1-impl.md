# Cycle 3.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

**GREEN Phase:**

**Implementation:** Populate plan states from filesystem

**Behavior:**
- Import plan discovery from worktree module (`list_plans` or equivalent)
- Populate `plan_states` with actual lifecycle states from `plans/*/lifecycle.md`
- Pass real `all_plans` dict to `render_unscheduled`
- `render_pending` skips `Status:` line when state is empty/None

**Changes:**
- File: `status/cli.py`
  Action: Replace placeholder with plan discovery call
  Location: Lines 31-34 and 55-60

- File: `status/render.py`
  Action: Conditionalize Status line — omit when empty
  Location: `render_pending` (lines 53-56)

**Verify GREEN:** `just green`
