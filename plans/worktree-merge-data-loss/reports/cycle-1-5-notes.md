# Cycle 1.5 Execution Report

**Step:** `plans/worktree-merge-data-loss/steps/step-1-5.md`
**Type:** Transformation (TDD)
**Outcome:** ✅ SUCCESS

## Summary

Implemented guard logic to allow removal of merged branches using safe delete (`git branch -d`) with appropriate success message differentiation.

## RED Phase

Test `test_rm_allows_merged_branch` existed and failed as expected, but not for the expected reason specified in the step.

**Expected failure per step:** Output contains `"Removed worktree {slug}"` instead of `"Removed {slug}"`.

**Actual failure:** Branch was not deleted at all (returncode 0 means branch still exists).

## Root Cause Analysis

The haiku over-implementation in step 1-2 had multiple bugs:
1. **Worktree removal order bug:** Branch deletion happened BEFORE worktree was fully cleaned up
2. **Prune timing bug:** `git worktree prune` ran before directory removal, so it had nothing to prune
3. **Path resolution bug:** rm() used `wt_path(slug)` which returns sibling `-wt/` directory, but guard tests create worktrees inside repo at `wt/`. The `_probe_registrations` checked wrong path, failed to detect registration, and removal logic never executed properly.

## GREEN Phase Implementation

Fixed three issues:

**1. Added helper to query actual worktree path from git:**
```python
def _get_worktree_path_for_branch(slug: str) -> Path | None:
    """Get the actual worktree path for a branch from git."""
    # Parses git worktree list --porcelain to find path for branch
```

**2. Updated rm() to use actual worktree path:**
```python
# Get actual worktree path from git, fall back to wt_path() if not found
worktree_path = _get_worktree_path_for_branch(slug)
if worktree_path is None:
    worktree_path = wt_path(slug)
```

**3. Fixed worktree removal sequence:**
- Track `is_merged` status at guard check time
- Remove worktree registrations (if any)
- Remove directory
- Prune (always, not conditional)
- Delete branch (now happens AFTER worktree fully removed)
- Output correct message based on merge status

**4. Message differentiation:**
```python
if is_merged:
    click.echo(f"Removed {slug}")
else:
    click.echo(f"Removed worktree {slug}")
```

## Verification

**GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_merged_branch -v` ✅
**Regression:** `pytest tests/test_worktree_rm.py -v` ✅ (3/3 passed)
**All guards:** `pytest tests/test_worktree_rm_guard.py -v` ✅ (5/5 passed)

## Changed Files

- `src/claudeutils/worktree/cli.py`:
  - Added `_get_worktree_path_for_branch()` helper (line 310)
  - Updated `rm()` to track merge status and use actual worktree path
  - Fixed worktree removal sequence (prune after directory removal)
  - Added message differentiation based on merge status

## Notes

The haiku over-implementation from step 1-2 contained multiple bugs that were only exposed when testing the actual removal of merged branches. The worktree path resolution issue affected all rm operations but wasn't caught by existing tests because they all used `worktree new` which creates worktrees at the expected `-wt/` location.

The guard tests create worktrees with raw `git worktree add` at arbitrary locations, which is a valid use case and exposed the path resolution assumption.
