# Cycle 5.8

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.8: Integration test for per-section merge

**RED Phase:**

**Test:** `test_full_session_md_merge_integration`
**Assertions:**
- Status line: ours `"# Session Handoff: 2026-02-16"` preserved, theirs `"2026-02-15"` discarded
- Completed This Session: ours section with 2 items preserved, theirs section with 1 item discarded
- Pending Tasks: ours has task A+B, theirs has B+C → result contains A, B, C (no duplicate B)
- Worktree Tasks: ours section preserved, theirs discarded
- Blockers: ours has 1 blocker, theirs has 2 → result has 3 total, theirs two tagged with `[from: test-slug]`
- Reference Files: ours section preserved, theirs discarded
- Next Steps: ours section preserved, theirs discarded

**Expected failure:** Some sections not handled correctly in integration

**Why it fails:** Integration gaps between individual section strategies

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_full_session_md_merge_integration -v`

**GREEN Phase:**

**Implementation:** End-to-end test verifying all strategies work together

**Behavior:**
- Create complete ours and theirs session.md files
- Simulate git conflict (write conflict markers)
- Run _resolve_session_md_conflict()
- Verify each section strategy applied correctly

**Approach:** Large integration test covering all sections

**Changes:**
- File: `tests/test_worktree_merge_sections.py`
  Action: Create comprehensive integration test
  Location hint: New test function with complete session.md fixtures

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_full_session_md_merge_integration -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
