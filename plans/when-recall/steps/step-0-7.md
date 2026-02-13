# Cycle 0.7

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.7: Rank matches with limit

**RED Phase:**

**Test:** `test_rank_matches_returns_sorted_limited`
**Assertions:**
- `rank_matches("mock", ["mock patching", "mock test", "unrelated", "mocking framework", "something"])` returns list of (candidate, score) tuples
- Results sorted by score descending
- `limit=3` returns at most 3 results
- Zero-score candidates excluded from results
- Default limit is 5

**Expected failure:** ImportError or AttributeError — `rank_matches` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_rank_matches_returns_sorted_limited -v`

**GREEN Phase:**

**Implementation:** Create `rank_matches` function.

**Behavior:**
- Score each candidate against query using `score_match`
- Filter out zero/negative scores
- Sort remaining by score descending
- Return top `limit` results as list of (candidate, score) tuples

**Approach:** List comprehension → filter → sort → slice.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add `rank_matches(query, candidates, limit=5)` function
  Location hint: After `score_match` function

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_rank_matches_returns_sorted_limited -v`
**Verify no regression:** `pytest tests/ -q`

---
