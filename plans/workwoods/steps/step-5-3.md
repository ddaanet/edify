# Cycle 5.3

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.3: Completed This Session strategy (keep ours)

**RED Phase:**

**Test:** `test_completed_this_session_squash_strategy`
**Assertions:**
- Ours has "Completed This Session" with main work items
- Theirs has "Completed This Session" with worktree work items
- Result: Ours section preserved, theirs discarded (worktree completions are worktree-scoped)

**Expected failure:** Theirs completed items appear in merged result

**Why it fails:** Squash strategy not applied to Completed section

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_completed_this_session_squash_strategy -v`

**GREEN Phase:**

**Implementation:** Apply squash (keep ours) strategy for Completed This Session section

**Behavior:**
- Locate "Completed This Session" section in ours and theirs
- Keep ours section content unchanged
- Discard theirs section content

**Approach:** Section-by-section merge, Completed section uses keep-ours

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add Completed This Session to section strategy mapping
  Location hint: In _resolve_session_md_conflict() section processing

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with completed items in both ours and theirs
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_completed_this_session_squash_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
