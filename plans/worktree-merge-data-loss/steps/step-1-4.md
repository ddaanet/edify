# Cycle 1.4

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.4: Guard refuses unmerged real history (exit 1, stderr message with count)

**Type:** Creation

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` (lines 347-382) — understand current `rm()` flow and structure.

**RED Phase:**

**Test:** `test_rm_refuses_unmerged_real_history` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Scenario A (real history): Create branch with 2 unmerged commits (not focused-session marker)
  - Call `worktree rm <slug>` via CliRunner
  - Exit code is 1 (refused)
  - Stderr contains: `"Branch {slug} has 2 unmerged commit(s). Merge first."`
  - Worktree directory still exists (not removed)
  - Branch still exists: `git rev-parse --verify <slug>` succeeds
- Scenario B (orphan): Create orphan branch (`git checkout --orphan`), commit on it
  - Call `worktree rm <slug>` via CliRunner
  - Exit code is 1 (refused)
  - Stderr contains: `"Branch {slug} is orphaned (no common ancestor). Merge first."`
  - Branch still exists

**Expected failure:** Exit code 0 (current behavior proceeds with removal) for both scenarios

**Why it fails:** Guard logic not implemented — rm proceeds unconditionally

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_refuses_unmerged_real_history -v`

**GREEN Phase:**

**Implementation:** Add guard logic to `rm()` in cli.py

**Behavior:**
- Before ANY destructive operations (before `_probe_registrations`)
- Check if branch exists: `git rev-parse --verify <slug>`
- If branch exists:
  - Check if merged: `_is_branch_merged(slug)` (from Cycle 1.1)
  - If not merged:
    - Get classification: `_classify_branch(slug)` (from Cycle 1.2)
    - If not focused-session-only (count != 1 or not focused):
      - If count == 0 (orphan): stderr `"Branch {slug} is orphaned (no common ancestor). Merge first."`
      - Else: stderr `"Branch {slug} has {count} unmerged commit(s). Merge first."`
      - Exit 1
- Proceed with removal (existing flow)

**Approach:** Insert guard block at function start. Design specifies exact flow (design.md lines 60-74).

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Insert guard logic at start of `rm()` function
  Location hint: After function docstring, before line 351

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_refuses_unmerged_real_history -v`
**Verify no regression:** `pytest tests/test_worktree_rm.py -v`

---
