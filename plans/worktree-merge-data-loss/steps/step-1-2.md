# Cycle 1.2

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.2: Branch classification — `_classify_branch(slug)` returns count and focused flag

**Type:** Creation

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` (lines 154-178) — understand marker text format `"Focused session for {slug}"` from `_create_session_commit`.

**RED Phase:**

**Test:** `test_classify_branch` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Focused-session-only branch (1 commit with marker): returns `(1, True)`
- Real-history branch (1 user commit): returns `(1, False)`
- Multi-commit branch (3 commits): returns `(3, False)`
- Set up: Create branch, make N commits, verify count
- Set up: Create branch with exact marker text `"Focused session for test-branch"`, verify focused=True
- Set up: Create branch with similar but different message `"Focused session test-branch"` (no "for"), verify focused=False

**Expected failure:** `AttributeError` — function doesn't exist

**Why it fails:** `_classify_branch` not implemented in cli.py

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`

**GREEN Phase:**

**Implementation:** Add `_classify_branch(slug: str) -> tuple[int, bool]` to cli.py

**Behavior:**
- Get merge-base between HEAD and slug: `git merge-base HEAD <slug>`
- Count commits: `git rev-list --count <merge_base>..<slug>`
- If count == 1: get commit message: `git log -1 --format=%s <slug>`
- Check if message matches exactly: `f"Focused session for {slug}"`
- Return (count, is_focused)

**Approach:** Three git commands in sequence. Design specifies exact logic (design.md lines 46-53).

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add helper function near other rm-related code
  Location hint: Before `rm()` function (before line 347)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`
**Verify no regression:** `pytest tests/test_worktree_rm.py -v`

---
