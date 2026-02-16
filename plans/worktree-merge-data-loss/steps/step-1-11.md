# Cycle 1.11

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.11: No MERGE_HEAD + no staged changes — exit 2 if branch unmerged, skip if merged

**Type:** Transformation

**RED Phase:**

**Test:** `test_phase4_handles_no_merge_head_no_staged` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Scenario A (unmerged): Branch exists, no MERGE_HEAD, no staged changes, branch NOT merged
  - Call `_phase4_merge_commit_and_precommit(slug)`
  - Exit code is 2
  - Stderr contains: `"Error: nothing to commit and branch not merged"`
  - No commit created
- Scenario B (merged): Branch exists, no MERGE_HEAD, no staged changes, branch IS merged
  - Call `_phase4_merge_commit_and_precommit(slug)`
  - Exit code is 0 (success)
  - No commit created (skip — already merged, nothing to do)
  - Stdout contains: (no error message)

**Expected failure:** Both scenarios fall through with no action (current code: no `else` branch after line 285)

**Why it fails:** Current code has no `else` branch to handle no-MERGE_HEAD + no-staged case

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_handles_no_merge_head_no_staged -v`

**GREEN Phase:**

**Implementation:** Add `else` branch to Phase 4 commit logic

**Behavior:**
- After `if merge_in_progress:` and `elif staged_check.returncode != 0:`
- Add `else:` (no MERGE_HEAD, no staged changes)
  - Check if branch merged: `_is_branch_merged(slug)`
  - If merged: skip commit (nothing to commit — already merged). Function continues to validation/precommit.
  - If not merged: stderr `"Error: nothing to commit and branch not merged"` + exit 2

**Approach:** Add third branch to handle edge case. Design specifies exact logic (design.md lines 111-115).

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add `else:` block after `elif` (line 285)
  Location hint: After the `elif staged_check.returncode != 0:` block

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_handles_no_merge_head_no_staged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_correctness.py -v` (all Phase 4 logic tests)

---
