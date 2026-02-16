# Cycle 1.3

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.3: Classification edge case — orphan branch (merge-base failure)

**Type:** Transformation

**RED Phase:**

**Test:** `test_classify_orphan_branch` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create orphan branch (no common ancestor with HEAD): `git checkout --orphan orphan-test`
- Commit on orphan branch (unrelated history)
- Call `_classify_branch("orphan-test")`: returns `(0, False)`
- Rationale: Design specifies orphan returns `(0, False)` to be treated as real history (design.md line 55)

**Expected failure:** `subprocess.CalledProcessError` or incorrect return value (undefined behavior)

**Why it fails:** `merge-base` fails when no common ancestor exists, code doesn't handle this

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_classify_orphan_branch -v`

**GREEN Phase:**

**Implementation:** Add error handling to `_classify_branch`

**Behavior:**
- Wrap `merge-base` call in try-except
- If `merge-base` raises `subprocess.CalledProcessError` (no common ancestor)
- Return `(0, False)` — treat as real history

**Approach:** Catch subprocess exception from `_git()` when merge-base fails

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Modify `_classify_branch` to handle merge-base failure
  Location hint: Around merge-base call in function body

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_classify_orphan_branch -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`

---
