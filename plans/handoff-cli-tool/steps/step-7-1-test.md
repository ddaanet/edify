# Cycle 7.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

Cross-subcommand contract test. Verifies parser consistency between handoff writes and status reads.

---

---

## Cycle 7.1: Cross-subcommand — handoff then status

**RED Phase:**

**Test:** `test_handoff_then_status`
**File:** `tests/test_session_integration.py`

**Assertions:**
- Create `tmp_path` git repo with `agents/session.md`
- CliRunner invokes `_handoff` with stdin (updates session.md)
- Then CliRunner invokes `_status` (reads updated session.md)
- Status output reflects the new status line from handoff input
- Status output reflects the updated completed section
- Verifies parser consistency: handoff writes → status reads the same format

**Expected failure:** Parser asymmetry between write and read paths

**Why it fails:** Integration verifies round-trip consistency

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_then_status -v`

---
