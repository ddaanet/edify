# Cycle 4.1: _is_dirty exclude_path with unstaged modifications

**Timestamp:** 2026-03-23

## Status: GREEN_VERIFIED

## Execution Summary

### RED Phase
- **Test command:** `pytest tests/test_git_helpers.py::test_is_dirty_excludes_path_with_unstaged_modifications tests/test_git_helpers.py::test_is_dirty_includes_files_outside_excluded_path -v`
- **RED result:** FAIL as expected
  - Test 1 failed with `AssertionError: assert True is False` — confirmed bug exists
  - Test 2 passed as expected (positive case)
  - Bug root cause verified: `_git()` at line 24 uses `.strip()` which removes leading space from porcelain output ` M file.py`, corrupting path extraction

### GREEN Phase
- **Implementation:** Modified `_is_dirty()` in `src/claudeutils/git.py` (lines 121-146)
  - Changed from using `_git()` helper to direct `subprocess.run()`
  - Used `.rstrip("\n")` instead of `.strip()` to preserve leading space in porcelain format
  - Path extraction at `line[3:]` now correctly extracts paths with space prefix intact
- **GREEN result:** PASS
  - Both new tests pass
  - Test 1: `_is_dirty(exclude_path="subdir")` returns `False` for unstaged file under subdir/
  - Test 2: `_is_dirty(exclude_path="subdir")` returns `True` for unstaged file under other/

### Regression Check
- **Result:** 30/30 passed
  - `tests/test_git_helpers.py` (11 tests)
  - `tests/test_worktree_rm_dirty.py` (6 tests)
  - `tests/test_planstate_aggregation.py` (4 tests)
  - `tests/test_status_rework.py` (9 tests)
- No regressions detected

### Refactoring
- **Format & Lint:** `ruff check` and `ruff format` applied
  - Fixed lint error: moved local imports to top-level (PLC0415)
  - All checks passed after fixes
- **Precommit validation:** PASS with no errors
  - 1775/1776 tests passed
  - 1 xfail (expected)
  - No complexity warnings or line-limit violations

## Files Modified
- `src/claudeutils/git.py` — Fixed `_is_dirty()` to bypass `_git()` and use `subprocess.run()` with `.rstrip()` instead of `.strip()`
- `tests/test_git_helpers.py` — Added two test cases for exclude_path with unstaged modifications

## Stop Condition
None

## Decision Made
Bypassed `_git()` helper in `_is_dirty()` to avoid `.strip()` corruption of porcelain format. The fix uses `subprocess.run()` directly with `.rstrip("\n")` to preserve the fixed-width XY+space prefix required for correct path extraction at `line[3:]`.

This is justified because:
1. `_is_dirty()` is the only caller that needs to preserve porcelain format structure
2. Other callers of `_git()` benefit from `.strip()` removal
3. Direct subprocess call is still minimal and clear
4. Bug root cause (documented in learnings.md) confirmed by this fix
