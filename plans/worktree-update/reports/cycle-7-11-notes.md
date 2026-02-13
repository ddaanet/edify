# Cycle 7.11: Phase 3 conflict handling — jobs.md auto-resolve

**Date:** 2026-02-13

## Summary

Implemented jobs.md conflict auto-resolution during merge operations. When `agents/jobs.md` appears in merge conflicts, it is automatically resolved by keeping the local version (marked authoritative as it contains plan status).

## Execution

### RED Phase
- **Test written:** `test_merge_conflict_jobs_md` in `test_worktree_merge_conflicts.py`
- **Expected failure:** AssertionError that jobs.md conflict not resolved
- **Actual result:** Test failed as expected (jobs.md remained in conflict list)

### GREEN Phase
- **Implementation:** Added `_resolve_jobs_md_conflict()` function in `src/claudeutils/worktree/merge.py`
- **Behavior:**
  - Checks if `"agents/jobs.md"` in conflict list
  - If present: runs `git checkout --ours agents/jobs.md && git add agents/jobs.md`
  - Prints warning: "jobs.md conflict: kept ours (local plan status)"
  - Returns conflict list with jobs.md removed
- **Integration:** Called after learnings.md resolution, before source file conflict abort
- **Test result:** PASS

### Regression Check
- Full test suite: 779/795 passed, 16 skipped
- No regressions introduced

### REFACTOR Phase
- **Formatting:** Auto-formatted by lint
- **Quality check:** Precommit validation passed
- **File split:** Moved test to dedicated `test_worktree_merge_jobs_conflict.py` to keep merge_conflicts.py under 400-line limit
  - Before split: merge_conflicts.py 513 lines → exceeds limit
  - After split: merge_conflicts.py 388 lines, merge_jobs_conflict.py 143 lines

## Files Modified

1. `src/claudeutils/worktree/merge.py` — Added `_resolve_jobs_md_conflict()` function
2. `tests/test_worktree_merge_conflicts.py` — Removed jobs.md test (moved to separate file)
3. `tests/test_worktree_merge_jobs_conflict.py` — New file with jobs.md conflict test

## Result

**Status:** GREEN_VERIFIED

- RED phase verified failure ✓
- GREEN phase verified pass ✓
- Regression check all tests pass ✓
- Precommit validation passes ✓
- Tree is clean ✓
