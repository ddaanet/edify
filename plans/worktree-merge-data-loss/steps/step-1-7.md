# Cycle 1.7

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.7: Guard integration — cli.py rm() calls guard before all destructive operations

**Type:** Transformation

**Dependencies:** Requires Cycles 1.1-1.6 complete

**RED Phase:**

**Test:** `test_rm_guard_prevents_destruction` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create branch with unmerged real history (2 commits, not focused)
- Create worktree directory on disk
- Add worktree task to session.md
- Call `worktree rm <slug>`
- Exit code is 1 (guard refused)
- **Negative assertions (regression test for incident):**
  - Worktree directory still exists on disk
  - Branch still exists
  - Session.md task NOT removed
  - `_probe_registrations` NOT called (verify via side effect absence: no worktree prune or removal occurred)

**Expected failure:** Side effects occur despite guard refusal — session.md task removed, worktree directory deleted, or `_probe_registrations` called. This tests the integration ordering, not the guard logic itself (which was added in Cycles 1.4-1.6).

**Why it fails:** Even with guard logic from Cycles 1.4-1.6, the rm() function structure may allow downstream operations to execute before the guard's early return. This cycle verifies the complete ordering: guard refusal prevents ALL downstream side effects (the original incident's root cause).

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_guard_prevents_destruction -v`

**GREEN Phase:**

**Implementation:** Reorder rm() to execute guard FIRST

**Behavior:**
- New rm() flow: `check_exists → guard → probe → warn → remove_session_task → remove_worktrees → branch -d/-D → rmtree → clean`
- Guard block from Cycles 1.4-1.6 executes before line 351 (`worktree_path = wt_path(slug)`)
- When guard exits 1, NONE of the following execute:
  - `_probe_registrations`
  - `remove_worktree_task`
  - `_remove_worktrees`
  - `shutil.rmtree`
  - `git branch -d/-D`

**Approach:** Restructure rm() function — guard at top, existing operations below

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Move guard logic (from 1.4-1.6) to function start; ensure early exit prevents all downstream operations
  Location hint: Entire rm() function (lines 347-382)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_guard_prevents_destruction -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py -v` (all Track 1 tests)

---
