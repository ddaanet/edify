# Cycle 1.1

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: `_detect_merge_state` identifies `merged` state

**RED Phase:**

**Test:** `test_detect_state_merged`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- `_detect_merge_state("branch")` returns `"merged"` when branch is already an ancestor of HEAD
- Returns `"clean"` for same repo before branch is merged (control assertion)

**Expected failure:** `ImportError` — `_detect_merge_state` does not yet exist in `merge.py`

**Why it fails:** Function not implemented.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_detect_state_merged -v`

**Test setup:** Create repo, add a commit on a branch, merge it into main with `git merge --no-edit branch`. Monkeypatch chdir. Call `_detect_merge_state("branch")` directly (import from `claudeutils.worktree.merge`).

**GREEN Phase:**

**Implementation:** Add `_detect_merge_state(slug: str) -> str` to `merge.py` with only the `merged` and `clean` states. Submodule and parent MERGE_HEAD checks are added in later cycles.

**Behavior:**
- Check `_is_branch_merged(slug)` (already in utils.py) — return `"merged"` if True
- Otherwise return `"clean"`

Note: Detection of `submodule_conflicts`, `parent_resolved`, and `parent_conflicts` states is added in Cycles 1.2 and 1.4. This minimal implementation is sufficient to pass Cycle 1.1's test.

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add `_detect_merge_state(slug: str) -> str` function near top of file (after existing helpers, before `_phase1_validate_clean_trees`)
  Location hint: After `_format_git_error`, before `_check_clean_for_merge`

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_detect_state_merged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_merge_head.py -v`

---
