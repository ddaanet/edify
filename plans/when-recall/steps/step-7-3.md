# Cycle 7.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.3: Verify uniqueness via fuzzy scoring

**RED Phase:**

**Test:** `test_uniqueness_verification`
**Assertions:**
- `verify_unique("how encode path", corpus)` returns True when trigger uniquely resolves to one heading
- `verify_unique("encode", corpus)` returns False when trigger matches multiple headings above threshold
- Uniqueness uses `fuzzy.rank_matches` — top match must be significantly above second match (score gap)

**Expected failure:** AttributeError — `verify_unique` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_compress_key.py::test_uniqueness_verification -v`

**GREEN Phase:**

**Implementation:** Create uniqueness verification using fuzzy engine.

**Behavior:**
- Score trigger against all headings in corpus
- Unique = top match score is significantly higher than second match (e.g., 2x or threshold gap)
- Return True/False

**Approach:** `rank_matches(trigger, corpus, limit=2)` then compare scores.

**Changes:**
- File: `src/claudeutils/when/compress.py`
  Action: Add `verify_unique(trigger, corpus)` function
  Location hint: After candidate generation

**Verify GREEN:** `pytest tests/test_when_compress_key.py::test_uniqueness_verification -v`
**Verify no regression:** `pytest tests/ -q`

---
