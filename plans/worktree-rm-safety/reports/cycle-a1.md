# Cycle A.1: _is_parent_dirty() - 2026-02-17

## Summary

Implemented `_is_parent_dirty()` utility function to detect uncommitted changes in the parent repo (both staged and unstaged files).

## Phase Results

### RED Phase
- **Status:** PASS (failed as expected)
- **Test command:** `pytest tests/test_worktree_rm.py::test_is_parent_dirty -v`
- **RED result:** ImportError — function does not exist (expected)

### GREEN Phase
- **Status:** PASS
- **Test command:** `pytest tests/test_worktree_rm.py::test_is_parent_dirty -v`
- **GREEN result:** Test passes
- **Regression check:** Full suite: 978/979 passed, 1 xfail (known bug) — no new failures

## Implementation Details

**Function:** `_is_parent_dirty()` in `src/claudeutils/worktree/utils.py`

**Behavior:**
- Returns `True` if working tree has any uncommitted changes (staged or unstaged)
- Returns `False` if tree is clean
- Uses `git status --porcelain` to detect changes (empty output = clean)
- Uses `check=False` to avoid raising on expected states

**Test coverage:** `tests/test_worktree_rm.py::test_is_parent_dirty`
- Asserts `False` on clean tree (after init_repo)
- Asserts `True` with untracked files
- Asserts `True` with staged files

## Refactoring

**Lint:** `just lint` passed (no new issues introduced)
**Precommit:** `just precommit` passed (all checks OK)

## Files Modified

- `src/claudeutils/worktree/utils.py` — Added `_is_parent_dirty()` function (9 lines)
- `tests/test_worktree_rm.py` — Added test function (17 lines) + import

## Stop Conditions

None — cycle completed successfully.

## Architecture Decisions

None — simple utility function implementing straightforward git status check.
