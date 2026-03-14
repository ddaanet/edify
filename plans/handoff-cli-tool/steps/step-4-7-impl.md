# Cycle 4.7

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

**GREEN Phase:**

**Implementation:** Wire the `handoff_cmd` Click command in `src/claudeutils/session/cli.py`, already registered in main `cli.py` from Step 1.2

**Behavior:**
- `handoff_cmd` Click command implementation
- Read stdin (if available) → `parse_handoff_input()`
- If no stdin: check for state file → `load_state()` → resume
- If no stdin and no state: `_fail("**Error:** No input on stdin and no state file", code=2)`
- Fresh pipeline: parse → save_state → overwrite_status → write_completed → diagnostics (git status/diff via _git changes) → clear_state
- Resume: load state → skip to `step_reached` → continue pipeline

**Changes:**
- File: `src/claudeutils/session/cli.py`
  Action: Implement `handoff_cmd` with full pipeline
  Location hint: Handoff command stub from Step 1.2

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
