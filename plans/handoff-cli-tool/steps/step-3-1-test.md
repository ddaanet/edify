# Cycle 3.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.1: Plan state discovery

**Finding:** M#7 + MN-5

**Prerequisite:** Read `src/claudeutils/session/status/cli.py:31-34, 55-60`. Discover `list_plans` import path — `Grep` for `def list_plans` in `src/`.

---

**RED Phase:**

**Test:** `test_status_shows_plan_states`
**Assertions:**
- Task with `plan_dir = "plans/foo"` where `plans/foo/lifecycle.md` exists → status output contains actual lifecycle state (e.g., `Status: planned`), not `Status: ` (empty)
- `render_unscheduled` receives populated dict → orphan plans shown in output
- Task with plan_dir but no lifecycle.md → `Status:` line omitted (not blank)

**Expected failure:** `AssertionError` — `plan_states` populated with empty strings, `render_unscheduled` always receives empty dict

**Why it fails:** Lines 31-34 hardcode empty strings; lines 55-60 pass empty dict.

**Verify RED:** `pytest tests/test_session_status.py::test_status_shows_plan_states -v`

---
