# Cycle 1.1

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: Shared helper — `_is_branch_merged(slug)` in utils.py

**Type:** Creation

**Prerequisite:** Read `src/claudeutils/worktree/utils.py` (lines 1-38) — understand existing helpers (`_git`, `wt_path`) and module structure.

**RED Phase:**

**Test:** `test_is_branch_merged` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- For merged branch: `_is_branch_merged("merged-branch")` returns `True`
- For unmerged branch: `_is_branch_merged("unmerged-branch")` returns `False`
- Set up: Create branch, commit to main (branch becomes ancestor), verify True
- Set up: Create branch, commit to branch (not merged), verify False

**Expected failure:** `ImportError` or `AttributeError` — function doesn't exist

**Why it fails:** `_is_branch_merged` not implemented in utils.py

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_is_branch_merged -v`

**GREEN Phase:**

**Implementation:** Add `_is_branch_merged(slug: str) -> bool` to utils.py

**Behavior:**
- Execute `git merge-base --is-ancestor <slug> HEAD`
- Return True if exit code 0 (branch is ancestor of HEAD)
- Return False if exit code 1 (branch not ancestor)
- Use `subprocess.run` directly (not `_git()`) — `_git()` returns `stdout.strip()`, not returncode. Codebase pattern for exit code checks uses `subprocess.run` directly (see merge.py line 269, cli.py line 370).

**Approach:** Single subprocess call with exit code check. Design specifies this exact command (design.md line 41).

**Changes:**
- File: `src/claudeutils/worktree/utils.py`
  Action: Add function after `wt_path()`, before EOF
  Location hint: After line 38

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_is_branch_merged -v`
**Verify no regression:** `pytest tests/test_worktree_utils.py -v`

---
