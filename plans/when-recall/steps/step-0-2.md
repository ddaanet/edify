# Cycle 0.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.2: Boundary bonus scoring

**RED Phase:**

**Test:** `test_boundary_bonuses_applied`
**Assertions:**
- `score_match("mp", "mock patching")` scores higher than `score_match("mp", "xmxpx")` (whitespace boundary bonus)
- `score_match("ep", "encode/path")` scores higher than `score_match("ep", "xexpy")` (delimiter boundary bonus)
- Whitespace boundary score > delimiter boundary score for equivalent matches (bonusBoundaryWhite=10 > bonusBoundaryDelimiter=9)

**Expected failure:** AssertionError — both score the same (no boundary bonuses yet)

**Why it fails:** `score_match` only applies base scoring, no boundary detection

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_boundary_bonuses_applied -v`

**GREEN Phase:**

**Implementation:** Add boundary detection to scoring.

**Behavior:**
- When matched character follows whitespace, add bonus of 10
- When matched character follows delimiter (/, -, _), add bonus of 9
- When matched character is at CamelCase transition, add bonus of 7
- First character match bonus multiplied by 2

**Approach:** At each match position, check preceding character type. Apply corresponding bonus constant.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add boundary type detection and bonus application in score calculation
  Location hint: Within `score_match` function, after determining match positions

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_boundary_bonuses_applied -v`
**Verify no regression:** `pytest tests/ -q`

---
