# Cycle 1.9

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.9: MERGE_HEAD checkpoint — Phase 4 refuses single-parent commit when branch unmerged (exit 2, "merge state lost" message)

**Type:** Transformation

**Dependencies:** Requires Cycle 1.1 (`_is_branch_merged` in utils.py)

**Prerequisite:** Read `src/claudeutils/worktree/merge.py` (lines 261-299) — understand current Phase 4 logic (two-branch: MERGE_HEAD present vs staged changes present).

**RED Phase:**

**Test:** `test_phase4_refuses_single_parent_when_unmerged` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Set up: Create branch, make changes, initiate merge (Phases 1-3)
- Simulate MERGE_HEAD loss: remove `.git/MERGE_HEAD` after Phase 3
- Staged changes still present (merge did stage files)
- Branch is NOT merged (verified via `_is_branch_merged`)
- Call `_phase4_merge_commit_and_precommit(slug)`
- Exit code is 2 (error)
- Stderr contains: `"Error: merge state lost — MERGE_HEAD absent, branch not merged"`
- NO commit created: `git log -1 --format=%s` shows commit BEFORE Phase 4 call

**Expected failure:** Exit code 0 with single-parent commit (current behavior: `elif` at line 284 creates commit)

**Why it fails:** Current code creates commit when staged changes present, regardless of merge status

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_refuses_single_parent_when_unmerged -v`

**GREEN Phase:**

**Implementation:** Add checkpoint to Phase 4 `elif` branch

**Behavior:**
- Current flow: `if merge_in_progress → commit; elif staged → commit`
- New flow: `if merge_in_progress → commit; elif staged → check branch merged → if merged: commit, else: exit 2`
- Import `_is_branch_merged` from utils.py
- In `elif staged_check.returncode != 0:` block (line 284):
  - Before creating commit, check: `if not _is_branch_merged(slug): stderr + exit 2`
  - If merged: proceed with commit (idempotent case)

**Approach:** Insert merge check before commit in `elif` branch. Design specifies exact logic (design.md lines 105-109).

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add import for `_is_branch_merged`; insert checkpoint in `elif` block
  Location hint: Line 284 (inside `elif staged_check.returncode != 0:`)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_refuses_single_parent_when_unmerged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_merge_head.py -v`

---
