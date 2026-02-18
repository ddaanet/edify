# Cycle 5.5

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.5: Keep-ours strategies (Worktree Tasks, Reference Files, Next Steps)

**Model:** Haiku (mechanical pattern — add 3 section names to existing strategy mapping)

**RED Phase:**

**Test:** `test_keep_ours_strategies` (parametrized)
**Parameters:**

| Section name | Description |
|-------------|-------------|
| Worktree Tasks | Main tracks worktree assignments; worktree's view is session-local |
| Reference Files | Worktree paths don't apply to main |
| Next Steps | Worktree direction is session-local |

**Assertions (per section):**
- Ours has section with main content
- Theirs has section with worktree content
- Result: Ours section preserved, theirs discarded

**Expected failure:** Theirs section content appears in merged result

**Why it fails:** Section not handled with keep-ours strategy

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_keep_ours_strategies -v`

**GREEN Phase:**

**Implementation:** Add all three section names to keep-ours strategy mapping

**Behavior:**
- Add "Worktree Tasks", "Reference Files", "Next Steps" to section strategy mapping
- All use identical keep-ours logic (already implemented for Status and Completed)

**Approach:** Add section names to existing strategy dict/mapping

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add Worktree Tasks, Reference Files, Next Steps to section strategy mapping with keep-ours
  Location hint: In _resolve_session_md_conflict() section processing

- File: `tests/test_worktree_merge_sections.py`
  Action: Create parametrized test covering all three sections
  Location hint: New test function with @pytest.mark.parametrize

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_keep_ours_strategies -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
