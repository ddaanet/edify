# Cycle 0.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.3: Consecutive match bonus

**RED Phase:**

**Test:** `test_consecutive_match_bonus`
**Assertions:**
- `score_match("mock", "mock patching")` scores higher than `score_match("mock", "mXoXcXk")` (consecutive characters)
- The score difference is approximately 4 points per additional consecutive character (bonusConsecutive=4)
- `score_match("ab", "ab")` returns exactly: 2*16 (base) + boundary + consecutive bonuses (verifiable math)

**Expected failure:** AssertionError — consecutive and separated score the same

**Why it fails:** No consecutive match bonus in scoring

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_consecutive_match_bonus -v`

**GREEN Phase:**

**Implementation:** Add consecutive match tracking.

**Behavior:**
- When a matched character immediately follows the previous matched character, add 4 per consecutive character
- Consecutive bonus accumulates (3 consecutive = 4+4)

**Approach:** Track previous match position. If current position == previous + 1, apply consecutive bonus.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add consecutive match detection and bonus in scoring loop
  Location hint: Within score_match, match position tracking

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_consecutive_match_bonus -v`
**Verify no regression:** `pytest tests/ -q`

---
