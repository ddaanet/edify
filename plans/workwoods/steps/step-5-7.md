# Cycle 5.7

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.7: Blockers evaluation strategy (extract, tag, append)

**RED Phase:**

**Test:** `test_blockers_evaluate_strategy`
**Assertions:**
- Ours has "Blockers / Gotchas" section with main blockers
- Theirs has blockers specific to worktree work
- Result: Ours blockers preserved, theirs blockers appended with `[from: <slug>]` tag
- Tags appear at end of first line of each blocker

**Expected failure:** Theirs blockers not appended or not tagged

**Why it fails:** Blockers evaluation strategy not implemented

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_blockers_evaluate_strategy -v`

**GREEN Phase:**

**Implementation:** Extract theirs blockers, tag with [from: slug], append to ours

**Behavior:**
- Extract blockers from theirs via extract_blockers()
- For each blocker:
  - Add `[from: <slug>]` to end of first line
  - Append full blocker (all lines) to ours Blockers section
- Create Blockers section in ours if missing

**Approach:** Extract, tag, append pattern

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Implement Blockers evaluation in _resolve_session_md_conflict()
  Location hint: Blockers section processing, after keep-ours sections

- File: `src/claudeutils/worktree/merge.py`
  Action: Pass slug parameter to _resolve_session_md_conflict() (needed for tagging)
  Location hint: Function signature and call site in _phase3_merge_parent()

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with blockers in theirs, verify tagging and append
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_blockers_evaluate_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
