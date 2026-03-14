# Cycle 4.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

## Cycle 4.6: Diagnostic output (H-3)

**RED Phase:**

**Test:** `test_diagnostics_output`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `format_diagnostics(git_output)` returns structured markdown containing the git status/diff output
- `format_diagnostics("")` with empty git output returns empty string (nothing to report)

**Expected failure:** `ImportError`

**Why it fails:** No diagnostics formatting function

**Verify RED:** `pytest tests/test_session_handoff.py::test_diagnostics_output -v`

---
