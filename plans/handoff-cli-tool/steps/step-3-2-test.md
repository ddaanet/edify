# Cycle 3.2

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.2: Session continuation header

**Finding:** M#8

---

**RED Phase:**

**Test:** `test_status_continuation_header`
**Assertions:**
- Dirty git tree → output starts with `Session: uncommitted changes — \`/handoff\`, \`/commit\``
- Clean git tree → no continuation header in output
- When plan_states contains `review-pending` for plan `foo` → header includes `, \`/deliverable-review plans/foo\``

**Expected failure:** `AssertionError` — continuation header feature entirely absent

**Why it fails:** No code checks git dirty state or renders continuation header.

**Verify RED:** `pytest tests/test_session_status.py::test_status_continuation_header -v`

---
