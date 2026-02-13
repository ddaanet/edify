# Cycle 3.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.2: Trigger mode — fuzzy match against index entries

**Prerequisite:** Read `src/claudeutils/when/fuzzy.py` — understand score_match and rank_matches API

**RED Phase:**

**Test:** `test_trigger_mode_resolves`
**Assertions:**
- Given test index with entries including `/when writing mock tests`:
  - `resolve("when", "writing mock tests", index_path, decisions_dir)` returns string containing `"# When Writing Mock Tests"` (heading)
  - Output contains section content from the decision file
- Query `"mock test"` (approximate) also resolves to same heading (fuzzy match)
- Query includes operator prefix: internal query becomes `"when writing mock tests"` (not just `"writing mock tests"`)

**Expected failure:** AssertionError — resolve returns empty or wrong content

**Why it fails:** Trigger mode resolution not implemented

**Verify RED:** `pytest tests/test_when_resolver.py::test_trigger_mode_resolves -v`

**GREEN Phase:**

**Implementation:** Implement trigger mode in resolver.

**Behavior:**
- Build candidate list from index entries (format: `"{operator} {trigger}"` for fuzzy matching)
- Use `fuzzy.rank_matches(query_with_prefix, candidates)` to find best match
- If match found, locate corresponding heading in decision file
- Extract section content (done in Cycle 3.5)
- For this cycle: return heading name on successful match

**Approach:** Parse index, build candidate strings, fuzzy match, map back to entry.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Implement trigger mode — index loading, candidate building, fuzzy matching
  Location hint: Within `resolve` function, trigger mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_trigger_mode_resolves -v`
**Verify no regression:** `pytest tests/ -q`

---
