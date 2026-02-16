# Cycle 1.10

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.10: [REGRESSION] Already-merged idempotency — Phase 4 allows commit when branch already merged (exit 0)

**Type:** Transformation (regression guard for Cycle 1.9)

**Note:** Cycle 1.9's implementation (`if not _is_branch_merged(slug): exit 2`) already handles the already-merged case correctly — merged branches pass the check and proceed to commit. This cycle verifies that behavior explicitly as a regression guard. The RED phase test should PASS against Cycle 1.9's implementation.

**RED Phase:**

**Test:** `test_phase4_allows_already_merged` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Set up: Create branch, merge to main (branch becomes merged)
- Stage changes (simulate re-merge with staged content)
- No MERGE_HEAD (already merged)
- Call `_phase4_merge_commit_and_precommit(slug)`
- Exit code is 0 (success)
- Commit created with staged changes

**Expected result:** Test PASSES against Cycle 1.9 implementation (regression guard — verifies `_is_branch_merged` correctly allows merged branches through the `elif` path)

**Why this test exists:** Documents and locks the idempotent behavior. If a future change to the `elif` branch breaks the merge check, this test catches it.

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_allows_already_merged -v` (expected: PASS)

**GREEN Phase:**

**Implementation:** No additional code needed — Cycle 1.9's `if not _is_branch_merged(slug)` handles this

**Behavior:**
- `elif staged_check.returncode != 0:` → checks `_is_branch_merged(slug)`
- If merged: creates commit (idempotent — re-merging already-merged branch)
- If not merged: exits 2 (Cycle 1.9 behavior)

**Changes:**
- File: `tests/test_worktree_merge_correctness.py`
  Action: Regression test verifies Cycle 1.9 implementation allows merged branches
  Location hint: N/A (test-only cycle)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_allows_already_merged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_refuses_single_parent_when_unmerged -v`

---
