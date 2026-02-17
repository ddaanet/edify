# Phase 3: `test-counts` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phase 1 (script scaffold, importlib infrastructure, `write_report` function)

**Parsing targets:** `**Test:**` fields in RED phases (test function names) + "All N tests pass" checkpoint claims.

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

## Cycle 3.2: test-counts — count mismatch (checkpoint claims more tests than exist, exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_test_counts` from Cycle 3.1 — understand checkpoint claim extraction and comparison logic.

**RED Phase:**

**Test:** `test_test_counts_mismatch`
**Assertions:**
- Running `test-counts` on `VIOLATION_TEST_COUNTS` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section shows: checkpoint location, claimed count (5), actual count (3)
- Report lists the 3 actual test function names
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_TEST_COUNTS` — three `**Test:**` fields (`test_alpha`, `test_beta`, `test_gamma`) and checkpoint "All 5 tests pass".

**Expected failure:** `AssertionError` — current `check_test_counts` from 3.1 returns PASS for all inputs; violation comparison is not yet implemented.

**Why it fails:** 3.1 GREEN only implements the happy path (no violations). The mismatch detection branch (claimed != actual) is not added until this cycle's GREEN phase.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_test_counts_mismatch -v`

---

**GREEN Phase:**

**Implementation:** Add count-mismatch detection and FAIL path to `check_test_counts`.

**Behavior:**
- After collecting unique function count and checkpoint claims: if `claimed_count != actual_count` → violation
- Violation record: `checkpoint_location` (approximate line context), `claimed_count`, `actual_count`, `test_function_list`
- Write FAIL report with violations, exit 1

**Approach:** `int(match.group(1))` for claimed count; `len(unique_names)` for actual. If mismatch: append violation. Multiple checkpoint claims in same runbook are checked independently — each may match or mismatch.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add comparison logic in `check_test_counts`; update handler to exit 1 on violations
  Location hint: Inside `check_test_counts`, after collecting test names and checkpoint claims

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_test_counts_mismatch -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 3.3: test-counts — parametrized test accounting (test_foo[param1]/[param2] count as 1, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_test_counts` — understand the base-name deduplication logic from Cycle 3.1.

**RED Phase:**

**Test:** `test_test_counts_parametrized`
**Assertions:**
- Running `test-counts` on `VIOLATION_TEST_COUNTS_PARAMETRIZED` fixture exits with code 0
- Report contains `**Result:** PASS`
- Unique function count is 1 (not 2) for `test_foo[param1]` and `test_foo[param2]`

**Fixture:** `VIOLATION_TEST_COUNTS_PARAMETRIZED` — two `**Test:**` fields: `` `test_foo[param1]` `` and `` `test_foo[param2]` ``; checkpoint "All 1 tests pass".

**Expected failure:** `AssertionError` — current implementation stores raw names (no stripping), yielding count 2 for `test_foo[param1]` and `test_foo[param2]` → mismatch with checkpoint claim of 1 → exits 1 instead of 0.

**Why it fails:** 3.1 GREEN collects raw names into the set. Parametrize-bracket stripping is not introduced until this cycle's GREEN phase.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_test_counts_parametrized -v`

---

**GREEN Phase:**

**Implementation:** Ensure parametrized test names are normalized to base function name before deduplication.

**Behavior:**
- Before adding each name to the unique-names set, strip any `[...]` parametrize suffix from the end
- `test_foo[param1]` and `test_foo[param2]` both normalize to `test_foo` → set size 1
- Checkpoint "All 1 tests pass" matches → PASS, exit 0

**Hint:** Use a regex or string operation to strip the bracket suffix from each extracted name before insertion. Apply normalization in the name-collection step. Affects all test counts — verify existing tests still pass with normalization applied.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add parametrize-suffix stripping when collecting unique function names in `check_test_counts`
  Location hint: Inside the test-name collection loop in `check_test_counts`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_test_counts_parametrized -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.
