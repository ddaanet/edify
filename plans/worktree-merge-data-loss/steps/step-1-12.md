# Cycle 1.12

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.12: Post-merge ancestry validation — `_validate_merge_result(slug)` called after commit, verifies slug is ancestor of HEAD

**Type:** Creation

**RED Phase:**

**Test:** `test_validate_merge_result` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Scenario A (valid merge): Create branch, merge properly, slug IS ancestor of HEAD
  - Call `_validate_merge_result(slug)`
  - Exit code is 0 (success — validation passes)
  - No stderr output
- Scenario B (invalid merge): Simulate incomplete merge (slug NOT ancestor of HEAD)
  - Call `_validate_merge_result(slug)`
  - Exit code is 2 (error)
  - Stderr contains: `"Error: branch {slug} not fully merged"`
- Scenario C (diagnostic): After single-parent commit, call `_validate_merge_result(slug)` where ancestry passes
  - Stderr contains: `"Warning: merge commit has 1 parent(s)"` (parent count < 2 diagnostic)

**Expected failure:** `AttributeError` or `ImportError` — function doesn't exist

**Why it fails:** `_validate_merge_result` not implemented in merge.py

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_validate_merge_result -v`

**GREEN Phase:**

**Implementation:** Add `_validate_merge_result(slug: str) -> None` to merge.py AND wire it into `_phase4_merge_commit_and_precommit`

**Behavior:**
- Execute `git merge-base --is-ancestor <slug> HEAD` (same check as `_is_branch_merged`)
- If exit code 0: validation passes, return
- If exit code != 0: stderr `"Error: branch {slug} not fully merged"` + exit 2
- Also emit diagnostic logging for parent count when < 2:
  - `git cat-file -p HEAD` → count lines starting with "parent "
  - If parent_count < 2: stderr `"Warning: merge commit has {parent_count} parent(s)"`

**Integration wiring:** Call `_validate_merge_result(slug)` in `_phase4_merge_commit_and_precommit` after the commit block (after `if merge_in_progress` / `elif staged` / `else`) but before `just precommit`. Design specifies this placement (design.md line 155: "validate ancestry after any successful commit or skip, then precommit").

**Approach:** Defensive check using merge-base. Design specifies exact command (design.md lines 125-132, 137-143).

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add function after existing helper functions, before `_phase4_merge_commit_and_precommit`; add call to `_validate_merge_result(slug)` in `_phase4_merge_commit_and_precommit` after commit block, before precommit
  Location hint: Function near other Phase 4 helpers; call site between commit block and `just precommit` (line 287)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_validate_merge_result -v`
**Verify no regression:** `pytest tests/test_worktree_merge_*.py -v`
**Verify existing tests:** `pytest tests/test_worktree_merge_merge_head.py -v` (existing Phase 4 tests must still pass after wiring)

---
