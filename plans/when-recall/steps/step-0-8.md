# Cycle 0.8

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.8: Prefix word inclusion

**RED Phase:**

**Test:** `test_prefix_word_disambiguates`
**Assertions:**
- `score_match("when writing mock tests", "When Writing Mock Tests")` > `score_match("when writing mock tests", "How to Write Mock Tests")` (prefix "when" boosts when-headed candidates)
- `score_match("how encode paths", "How to Encode Paths")` > `score_match("how encode paths", "When Encoding Paths")` (prefix "how" boosts how-headed candidates)
- Query without prefix: `score_match("writing mock tests", "When Writing Mock Tests")` and `score_match("writing mock tests", "How to Write Mock Tests")` are closer in score (less disambiguation)

**Expected failure:** AssertionError — scores don't reflect prefix disambiguation

**Why it fails:** This tests the design requirement that query includes prefix word for disambiguation, verifying the scoring naturally handles it via word boundary bonuses.

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_prefix_word_disambiguates -v`

**GREEN Phase:**

**Implementation:** This cycle validates that existing scoring naturally produces disambiguation. May require tuning constants if disambiguation is insufficient.

**Behavior:**
- Prefix word "when"/"how" in query matches prefix word in candidate heading
- Word boundary bonus at the heading's first word provides disambiguation
- No new code required IF existing scoring already disambiguates; otherwise tune boundary constants

**Approach:** Run assertions — if they pass, existing scoring is sufficient. If not, increase first-character or word-boundary bonuses.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Potentially adjust scoring constants if disambiguation insufficient
  Location hint: Scoring constant definitions

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_prefix_word_disambiguates -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 1: Index Parser

**Type:** TDD
**Model:** haiku
**Dependencies:** None (Pydantic only)
**Files:** `src/claudeutils/when/index_parser.py`, `tests/test_when_index_parser.py`

**Design reference:** Index Format section, D-1 (Two-field format)
**Existing pattern:** `src/claudeutils/recall/index_parser.py` — Pydantic BaseModel pattern for entry parsing

---
