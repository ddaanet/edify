# Cycle 0.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.4: Gap penalties

**RED Phase:**

**Test:** `test_gap_penalties_reduce_score`
**Assertions:**
- `score_match("ac", "abc")` scores higher than `score_match("ac", "aXXXXc")` (shorter gap = higher score)
- `score_match("ac", "aXc")` has gap penalty of -3 (start) applied
- `score_match("ac", "aXXXc")` has penalty of -3 (start) + -2 (2 extensions at -1 each)

**Expected failure:** AssertionError — all gaps score the same

**Why it fails:** No gap penalty in scoring

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_gap_penalties_reduce_score -v`

**GREEN Phase:**

**Implementation:** Add gap penalties between matched characters.

**Behavior:**
- Starting a gap (first unmatched character after a match): penalty of -3
- Each additional gap character: penalty of -1
- No gap penalty before first match or after last match

**Approach:** Between consecutive match positions, calculate gap length. Apply start + extension penalties.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add gap penalty calculation between match positions
  Location hint: Within score_match, after match position determination

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_gap_penalties_reduce_score -v`
**Verify no regression:** `pytest tests/ -q`

---
