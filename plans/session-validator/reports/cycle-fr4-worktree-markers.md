# Cycle FR-4: Worktree Marker Cross-Reference

**Timestamp:** 2026-03-02 15:30 UTC

## Status
GREEN_VERIFIED

## Phases

### RED Phase
- Test file: `tests/test_validation_session_worktrees.py`
- Expected failure: ImportError (module not yet created)
- Result: FAIL as expected
- 14 test cases written covering:
  - No worktrees / no markers (clean)
  - Marker matching existing worktree (pass)
  - Marker pointing to non-existent worktree (error)
  - Unreferenced worktree (warning)
  - Mixed valid/invalid markers
  - Non-task lines ignored
  - Multiple errors and warnings accumulate
  - Line numbers in error messages

### GREEN Phase
- Implementation: `src/claudeutils/validation/session_worktrees.py`
- Functions:
  - `get_worktree_slugs()` — Queries git worktree list, excludes main, accepts optional test parameter
  - `check_worktree_markers()` — Returns (errors, warnings) tuple for marker validation
- Integration: Added to `session_structure.py`'s `validate()` function
- Test runs: All 14 tests pass on first run
- Regression check: Full suite passes (1491/1492, 1 expected xfail)

### REFACTOR Phase
- Code formatting: `just lint` passes (minor reformatting of test file)
- Precommit validation: `just precommit` passes
- Updated test expectations:
  - `test_cross_section_duplicate` now passes `worktree_slugs={"slug"}`
  - `test_multiple_error_types` now passes `worktree_slugs=set()` and expects 3 errors

## Implementation Details

### `get_worktree_slugs()`
- Accepts optional `worktree_slugs` parameter for testing
- If None, runs `git worktree list --porcelain` and parses output
- Extracts slug from `.claude/worktrees/<slug>` path pattern
- Returns empty set on subprocess failure (robust error handling)

### `check_worktree_markers()`
- Parses task lines using shared `parse_task_line()` from `task_parsing.py`
- Checks if each marker slug exists in worktree_slugs set
- Returns tuple: (errors for missing worktrees, warnings for unreferenced worktrees)
- Error messages include line numbers for debugging
- Warnings list worktrees alphabetically

### Integration Design
- Added `worktree_slugs` parameter to `validate()` function
- Parameter is None by default (queries git)
- Tests pass mock set to avoid git queries in test environment
- Marker validation called after all other checks, errors accumulated with others

## Files Modified
- Created: `src/claudeutils/validation/session_worktrees.py` (95 lines)
- Created: `tests/test_validation_session_worktrees.py` (147 lines)
- Modified: `src/claudeutils/validation/session_structure.py` (added imports, parameter, validation call)
- Modified: `tests/test_validation_session_structure.py` (updated 2 tests to pass worktree_slugs)

## Acceptance Criteria Met
- [x] Each slug marker maps to entry in git worktree list output
- [x] Worktrees without markers produce warnings
- [x] Main worktree excluded from cross-reference
- [x] `.claude/worktrees/` prefix handled (extracted as slug)
- [x] Full test coverage with 14 test cases
- [x] No regressions (full suite green)
- [x] Precommit validation passing

## Next Steps
- Commit cycle changes
- Proceed to FR-1 (session section schema) or other remaining FRs
- FR-5 (status line validators) and FR-6 (plan archive check) independent
- FR-7 (command semantic validation) in progress (integrated but may need expansion)
