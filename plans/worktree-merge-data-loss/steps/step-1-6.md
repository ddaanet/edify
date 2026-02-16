# Cycle 1.6

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.6: Guard allows focused-session-only removal (exit 0, `git branch -D` force delete, "Removed {slug} (focused session only)")

**Type:** Transformation

**RED Phase:**

**Test:** `test_rm_allows_focused_session_only` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create branch with exactly 1 commit having marker text: `"Focused session for test-branch"`
- Branch is NOT merged (unmerged but allowed due to focused-session marker)
- Call `worktree rm <slug>` via CliRunner
- Exit code is 0 (success)
- Branch deleted: `git rev-parse --verify <slug>` fails
- Stdout contains: `"Removed {slug} (focused session only)"` (design.md line 82)
- Branch deleted despite being unmerged (force delete required — `-d` alone would fail for unmerged branch)

**Expected failure:** Exit code 1 (guard refuses) or wrong message/deletion method

**Why it fails:** Guard from Cycle 1.4 blocks all unmerged branches; need exception for focused-session-only

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_focused_session_only -v`

**GREEN Phase:**

**Implementation:** Update guard to allow focused-session-only branches

**Behavior:**
- In guard logic (from Cycle 1.4):
  - If branch not merged AND focused-session-only (count == 1 and focused == True):
    - Allow removal to proceed
  - Track removal type: set local variable `removal_type` (`"merged"` or `"focused"`) before proceeding — used by branch deletion code (Cycles 1.5-1.6) to choose `-d` vs `-D` flag and success message
- For focused-session-only: use `git branch -D <slug>` (force delete)
- Success message: `"Removed {slug} (focused session only)"`

**Approach:** Modify guard conditional from Cycle 1.4 to pass through focused branches; update branch deletion to use `-D` flag when appropriate

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Update guard conditional (from 1.4) to allow focused branches; modify branch deletion to use `-D` for focused-only
  Location hint: Guard block + branch deletion (lines ~351-373)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_focused_session_only -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py::test_rm_refuses_unmerged_real_history -v`

---
