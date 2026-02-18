# Cycle 5.4

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.4: Pending Tasks strategy (existing additive logic preserved)

**RED Phase:**

**Test:** `test_pending_tasks_additive_strategy`
**Assertions:**
- Ours has tasks A and B
- Theirs has tasks B and C
- Result: tasks A, B, C (union by task name, B not duplicated)
- Existing behavior preserved from current _resolve_session_md_conflict()

**Expected failure:** Test passes (existing logic works) OR refactoring breaks additive merge

**Why it might pass:** Additive logic already implemented

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_pending_tasks_additive_strategy -v`

**GREEN Phase:**

**Implementation:** Preserve existing Pending Tasks additive logic in refactored function

**Behavior:**
- Extract tasks from ours and theirs via extract_task_blocks()
- Compare by task name to find new tasks
- Insert new tasks at Pending Tasks section end
- Existing logic from lines 70-108 preserved

**Approach:** Integrate existing additive logic into new section-based structure

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Preserve Pending Tasks additive merge in refactored code
  Location hint: Pending Tasks section processing in _resolve_session_md_conflict()

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test verifying task union behavior
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_pending_tasks_additive_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
