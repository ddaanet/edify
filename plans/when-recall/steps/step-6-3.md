# Cycle 6.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.3: Fuzzy bidirectional integrity

**RED Phase:**

**Test:** `test_fuzzy_bidirectional_integrity`
**Assertions:**
- Index entry `/when writing mock tests` with heading `### When Writing Mock Tests` → passes (fuzzy match succeeds)
- Index entry `/when writing mock tests` with NO matching heading → error "orphan entry"
- Heading `### When Auth Fails` with NO index entry → error "orphan heading"
- Fuzzy matching bridges compression: trigger `"write mock test"` matches heading `"When Writing Mock Tests"` (fuzzy, not exact)

**Expected failure:** AssertionError — validation still using exact lowercase match

**Why it fails:** Bidirectional integrity check not yet using fuzzy engine

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_fuzzy_bidirectional_integrity -v`

**GREEN Phase:**

**Implementation:** Replace exact match with fuzzy matching for entry↔heading validation.

**Behavior:**
- For each index entry: fuzzy match `"{operator} {trigger}"` against all headings
- Must resolve to exactly one heading (unique expansion)
- For each semantic heading: check that at least one index entry fuzzy-matches it
- Import `fuzzy.score_match` from `claudeutils.when.fuzzy`

**Approach:** Replace `key.lower() == title.lower()` checks with `fuzzy.rank_matches()` scoring. Threshold determines match/no-match.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Import fuzzy engine, replace exact match with fuzzy matching in orphan checks
  Location hint: `check_orphan_entries` and orphan heading validation

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_fuzzy_bidirectional_integrity -v`
**Verify no regression:** `pytest tests/ -q`

---
