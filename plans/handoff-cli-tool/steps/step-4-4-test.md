# Cycle 4.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

## Cycle 4.4: State caching (H-4)

**RED Phase:**

**Test:** `test_state_cache_create`, `test_state_cache_resume`, `test_state_cache_cleanup`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `save_state(input_md, step="write_session")` creates `tmp/.handoff-state.json` with `input_markdown`, `timestamp` (ISO format), `step_reached` fields
- `load_state()` returns `HandoffState` with same fields, or `None` if no state file
- `clear_state()` removes the state file
- `step_reached` values: `"write_session"`, `"diagnostics"`
- State file survives across function calls (not deleted on load)

**Expected failure:** `ImportError` — state caching functions don't exist

**Why it fails:** No state management module

**Verify RED:** `pytest tests/test_session_handoff.py::test_state_cache_create -v`

---
