# Cycle 5.6

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.6: extract_blockers() function in session.py

**RED Phase:**

**Test:** `test_extract_blockers_function`
**Assertions:**
- extract_blockers(content) with single blocker `"- Issue X\n  Details here"` returns `[["- Issue X", "  Details here"]]`
- extract_blockers(content) with two blockers returns list of length 2, each containing their respective lines
- extract_blockers(content) with no Blockers section returns empty list `[]`
- Multi-line blocker with 3 continuation lines returns list item with 4 strings (bullet + 3 continuations)

**Expected failure:** NameError (extract_blockers not defined)

**Why it fails:** Function not implemented yet

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_extract_blockers_function -v`

**GREEN Phase:**

**Implementation:** Create extract_blockers() function in session.py

**Behavior:**
- Find "Blockers / Gotchas" section via find_section_bounds()
- Extract bullet items (same pattern as task extraction)
- Collect continuation lines per bullet
- Return list of line groups

**Approach:** Similar to extract_task_blocks() but simpler (no task name extraction)

**Changes:**
- File: `src/claudeutils/worktree/session.py`
  Action: Implement extract_blockers(content: str) -> list[list[str]]
  Location hint: New function after extract_task_blocks()

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with Blockers section containing multi-line items
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_extract_blockers_function -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
