# Cycle 1.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.2: Extract operator (when/how)

**RED Phase:**

**Test:** `test_operator_extraction`
**Assertions:**
- Line starting with `/when ` extracts operator `"when"`
- Line starting with `/how ` extracts operator `"how"`
- Line starting with `/what ` is skipped (not a valid operator)
- Line starting with bare text (no `/` prefix) is skipped

**Expected failure:** AssertionError — non-when/how lines incorrectly parsed or valid lines rejected

**Why it fails:** Operator validation not yet implemented (or only partial from 1.1)

**Verify RED:** `pytest tests/test_when_index_parser.py::test_operator_extraction -v`

**GREEN Phase:**

**Implementation:** Add operator validation to parser.

**Behavior:**
- Only lines starting with `/when ` or `/how ` are valid entries
- All other lines (including `/what`, `/why`, bare text, headers) are skipped
- Operator extracted as lowercase string without `/` prefix

**Approach:** Regex or string prefix check. Only `^/when ` and `^/how ` match.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Add operator prefix validation in parse loop
  Location hint: Entry detection logic

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_operator_extraction -v`
**Verify no regression:** `pytest tests/ -q`

---
