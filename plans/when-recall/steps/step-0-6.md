# Cycle 0.6

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.6: Minimum score threshold

**RED Phase:**

**Test:** `test_minimum_score_threshold`
**Assertions:**
- `score_match("x", "extremely long candidate string with many words")` returns 0.0 (short query, spurious match filtered)
- `score_match("when", "when auth fails")` returns positive (legitimate match above threshold)
- `score_match("zq", "writing mock tests")` returns 0.0 (no valid subsequence or below threshold)

**Expected failure:** AssertionError — single-char queries return positive scores for long strings

**Why it fails:** No minimum score threshold filtering

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_minimum_score_threshold -v`

**GREEN Phase:**

**Implementation:** Add minimum score threshold.

**Behavior:**
- After computing score, compare against a minimum threshold
- Threshold scales with query length (shorter queries need higher per-character scores to qualify)
- Return 0.0 if below threshold (not a meaningful match)

**Approach:** Define threshold as `min_score_per_char * len(query)`. If total_score / len(query) below threshold, return 0.0.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add threshold check at end of score_match
  Location hint: Before return statement

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_minimum_score_threshold -v`
**Verify no regression:** `pytest tests/ -q`

---
