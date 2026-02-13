# Cycle 0.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.1: Character subsequence matching

**RED Phase:**

**Test:** `test_subsequence_match_scores_positive`
**Assertions:**
- `score_match("abc", "aXbXc")` returns a positive float (characters found in order)
- `score_match("abc", "xyz")` returns 0.0 or negative (no subsequence match)
- `score_match("abc", "abc")` returns higher score than `score_match("abc", "aXbXc")` (exact > sparse)

**Expected failure:** ImportError or AttributeError — `score_match` doesn't exist

**Why it fails:** Module `src/claudeutils/when/fuzzy.py` not yet created

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_subsequence_match_scores_positive -v`

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/when/__init__.py` (empty) and `fuzzy.py` with `score_match(query, candidate)` function.

**Behavior:**
- Find each query character in candidate (in order, case-insensitive)
- If all characters found in order, return positive score (base 16 per matched character)
- If subsequence not found, return 0.0
- Track match positions for bonus calculations in later cycles

**Approach:** Smith-Waterman style DP matrix — build score[i][j] for query[i] matched at candidate[j]. For this cycle, base scoring only (no bonuses yet).

**Changes:**
- File: `src/claudeutils/when/__init__.py`
  Action: Create empty file
- File: `src/claudeutils/when/fuzzy.py`
  Action: Create with `score_match` function implementing character-level subsequence matching with base score
  Location hint: Module-level function

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_subsequence_match_scores_positive -v`
**Verify no regression:** `pytest tests/ -q`

---
