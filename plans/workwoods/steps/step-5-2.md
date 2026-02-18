# Cycle 5.2

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.2: Status line strategy (keep ours)

**RED Phase:**

**Test:** `test_status_line_squash_strategy`
**Assertions:**
- Ours: `# Session Handoff: 2026-02-16` + `**Status:** Main work`
- Theirs: `# Session Handoff: 2026-02-15` + `**Status:** Worktree work`
- Result: Ours status line preserved, theirs discarded

**Expected failure:** Theirs status line appears in merged result

**Why it fails:** Per-section strategy not implemented, still using keep-ours for entire file

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_status_line_squash_strategy -v`

**GREEN Phase:**

**Implementation:** Refactor _resolve_session_md_conflict() to apply squash strategy for status line

**Behavior:**
- Status line = H1 title + `**Status:**` line
- Parse ours into sections
- For status line section: keep ours unchanged
- Discard theirs status line

**Approach:** Section-by-section processing, status line is special case (lines 0-2 typically)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Refactor _resolve_session_md_conflict() to parse sections first
  Location hint: Beginning of function, before task extraction

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with conflicting status lines
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_status_line_squash_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
