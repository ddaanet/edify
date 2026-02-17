# Cycle 3.1

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.1: test-counts — happy path (checkpoint count matches test function count, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand current structure from Phase 1: importlib block, `write_report`, subcommand stubs.

**RED Phase:**

**Test:** `test_test_counts_happy_path`
**Assertions:**
- Running `test-counts` on `VALID_TDD` fixture exits with code 0
- Report file written to expected path
- Report contains `**Result:** PASS`
- Report `Summary` shows `Failed: 0`

**Fixture:** `VALID_TDD` — per Common Context spec, already includes `**Test:** \`test_foo\`` and checkpoint "All 1 tests pass".

**Expected failure:** `AssertionError` — `test-counts` handler is still a stub; no report written.

**Why it fails:** `test-counts` handler not yet implemented.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_test_counts_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_test_counts(content, path)` and wire to `test-counts` handler.

**Behavior:**
- Extract all `**Test:**` field values from RED phases using regex `r'\*\*Test:\*\*\s*`?([^`\n]+)`?'`
- Collect unique test function names (raw names, no suffix stripping yet)
- Extract checkpoint claims using regex `r'All\s+(\d+)\s+tests?\s+pass'` from the full content
- For each checkpoint claim: compare claimed count to unique function count accumulated to that point
- No mismatches → write PASS report, exit 0

**Approach:** Process document in order. Collect test names in a set (raw names). After all cycles, find all checkpoint claims. For single checkpoint at end: compare count. If no checkpoints, no violations. Write PASS report.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `check_test_counts(content, path)` function with test-name extraction and checkpoint parsing; wire to `test-counts` handler
  Location hint: After `check_lifecycle`, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_test_counts_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
