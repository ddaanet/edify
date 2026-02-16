# Cycle 1.5

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.5: Guard allows merged branch removal (exit 0, `git branch -d` safe delete, "Removed {slug}")

**Type:** Transformation

**RED Phase:**

**Test:** `test_rm_allows_merged_branch` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create branch, commit changes, merge to main (branch becomes merged)
- Call `worktree rm <slug>` via CliRunner
- Exit code is 0 (success)
- Branch deleted: `git rev-parse --verify <slug>` fails
- Stdout contains: `"Removed {slug}"` (no qualifier like "focused session only")
- Branch was merged before deletion (safe delete with `-d` succeeds for merged branches; no force required)

**Expected failure:** Output contains `"Removed worktree {slug}"` instead of expected `"Removed {slug}"` (current code at line 382 includes "worktree" in message)

**Why it fails:** Current rm outputs `"Removed worktree {slug}"` (line 382) — test asserts `"Removed {slug}"` without "worktree" qualifier. Also, current code has no per-branch-type message differentiation.

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_merged_branch -v`

**GREEN Phase:**

**Implementation:** Update rm() to use `-d` for merged branches and appropriate message

**Behavior:**
- After guard passes (branch is merged or focused-session-only)
- For merged branches: use `git branch -d <slug>` (safe delete)
- Success message: `"Removed {slug}"` (design.md line 81)

**Approach:** Modify existing branch deletion code (lines 369-373) to track merge status and use appropriate flags/messages

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Update branch deletion to use `-d` for merged, differentiate messages
  Location hint: Lines 369-373 (current branch delete) and line 382 (current success message)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_merged_branch -v`
**Verify no regression:** `pytest tests/test_worktree_rm.py -v`

---
