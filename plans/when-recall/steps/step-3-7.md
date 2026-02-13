# Cycle 3.7

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.7: Error handling — trigger not found

**RED Phase:**

**Test:** `test_trigger_not_found_suggests_matches`
**Assertions:**
- `resolve("when", "nonexistent topic xyz", index_path, decisions_dir)` raises `ResolveError`
- Error message contains `"No match for"` and the query text
- Error message contains `"Did you mean:"` followed by up to 3 closest fuzzy matches
- Each suggestion formatted as `/when <trigger>`

**Expected failure:** ResolveError raised but without suggestions, or wrong message format

**Why it fails:** Error message doesn't include fuzzy suggestions

**Verify RED:** `pytest tests/test_when_resolver.py::test_trigger_not_found_suggests_matches -v`

**GREEN Phase:**

**Implementation:** Add error handling with fuzzy suggestions.

**Behavior:**
- When best fuzzy match is below threshold (no valid match): raise ResolveError
- Use `fuzzy.rank_matches(query, all_candidates, limit=3)` to get closest matches
- Format error: `"No match for '<query>'. Did you mean:\n  /when <suggestion1>\n  /when <suggestion2>"`
- If no suggestions at all: just `"No match for '<query>'."`

**Approach:** After rank_matches returns empty or below threshold, re-query for top 3 regardless of threshold for suggestions.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add ResolveError class and trigger-not-found error with suggestions
  Location hint: Error handling in trigger mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_trigger_not_found_suggests_matches -v`
**Verify no regression:** `pytest tests/ -q`

---
