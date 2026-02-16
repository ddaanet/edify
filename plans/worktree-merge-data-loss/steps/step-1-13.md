# Cycle 1.13

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.13: Parent repo file preservation — end-to-end test: branch with parent + submodule changes → merge → verify all files present in HEAD

**Type:** Integration (regression test for original incident)

**Dependencies:** Requires Cycles 1.9-1.12 complete (full Phase 4 modifications)

**Note:** This test may pass even without fixes if the original bug was environment-specific (design.md line 204). The test has value as a regression guard.

**RED Phase:**

**Test:** `test_merge_preserves_parent_repo_files` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Set up: Create worktree branch
- In worktree: Add parent repo file (`parent-change.txt` in repo root, NOT in submodule)
- In worktree: Add submodule change (`agent-core/submodule-change.txt`)
- Commit both changes in worktree
- Switch to main, run full merge (Phases 1-4)
- Verify parent repo file exists in main after merge: `Path("parent-change.txt").exists()`
- Verify submodule file exists: `Path("agent-core/submodule-change.txt").exists()`
- Verify merge commit has 2 parents: `git log -1 --format=%p HEAD` → two parent hashes
- Verify branch is ancestor of HEAD: `git merge-base --is-ancestor <slug> HEAD` succeeds

**Expected failure:** Parent repo file missing (reproduces original incident) OR test passes (incident was environment-specific)

**Why it fails (if it fails):** Original bug: Phase 4 created single-parent commit, dropping parent changes

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_merge_preserves_parent_repo_files -v`

**GREEN Phase:**

**Implementation:** Phase 4 modifications from Cycles 1.9-1.12 prevent single-parent commits

**Behavior:**
- MERGE_HEAD checkpoint (Cycle 1.9): refuses commit if MERGE_HEAD absent and branch unmerged
- Ancestry validation (Cycle 1.12): verifies branch is ancestor after commit
- Defense-in-depth: both checks catch the single-parent bug from different angles

**Approach:** No additional code — test verifies Cycles 1.9-1.12 collectively prevent data loss

**Changes:**
- File: `tests/test_worktree_merge_correctness.py`
  Action: Integration test exercises full merge flow
  Location hint: N/A (test-only cycle)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_merge_preserves_parent_repo_files -v`
**Verify no regression:** `pytest tests/test_worktree_merge_*.py -v` (all merge tests including existing)

---
