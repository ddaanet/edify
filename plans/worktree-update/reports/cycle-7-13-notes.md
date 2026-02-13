# Cycle 7.13: Phase 4 precommit validation — run and check exit code

**Status:** GREEN_VERIFIED
**Timestamp:** 2026-02-13
**Model:** haiku

## Summary

Implemented Phase 4 of the merge ceremony: merge commit and precommit validation.

## Phase Results

**RED Phase:**
- Test: `test_merge_precommit_validation`
- Expected failure: AssertionError - precommit not run, no merge commit
- Actual result: FAIL as expected (merge command didn't create merge commit)

**GREEN Phase:**
- Implementation in `src/claudeutils/worktree/merge.py`: Added `_phase4_merge_commit_and_precommit()`
- Checks for staged changes with `git diff --cached --quiet`
- Creates merge commit with message `🔀 Merge <slug>` if changes staged
- Runs `just precommit` and handles exit codes: 0 (success), ≠0 (failure exit 1)
- Test `test_merge_precommit_validation` now PASSES

**Regression Check:**
- All 796 tests pass (1 xfail for known markdown bug)
- Updated 6 existing merge tests to use new `mock_precommit` fixture
- Updated test assertions for MERGE_HEAD (now doesn't exist after Phase 4 completes)

## Changes Made

**Files modified:**
1. `src/claudeutils/worktree/merge.py`
   - Added `_phase4_merge_commit_and_precommit()` function
   - Updated `merge()` to call Phase 4 after Phase 3

2. `tests/conftest.py`
   - Added shared `mock_precommit` fixture to mock `just precommit` subprocess call
   - Avoids requiring actual justfile in test environments

3. `tests/test_worktree_merge_parent.py`
   - Added `test_merge_precommit_validation()` test
   - Updated `test_merge_parent_initiate()` to verify merge completes (MERGE_HEAD doesn't exist)
   - All tests now use `mock_precommit` fixture

4. `tests/test_worktree_merge_validation.py`
   - Updated both tests to use `mock_precommit` fixture

5. `tests/test_worktree_merge_submodule.py`
   - Updated all 3 merge tests to use `mock_precommit` fixture

6. `tests/test_worktree_merge_conflicts.py`
   - Updated all 3 merge tests to use `mock_precommit` fixture
   - Updated `test_merge_conflict_agent_core()` to verify merge is complete

7. `tests/test_worktree_merge_jobs_conflict.py`
   - Updated test to use `mock_precommit` fixture

## Quality

- All tests pass (796/797, 1 expected xfail)
- Lint passes (format + ruff check + mypy)
- No regressions introduced
- Code follows project conventions

## Architectural Notes

Phase 4 completes the merge ceremony by committing any staged changes and validating with precommit. The precommit check is mocked in tests to avoid requiring a justfile in test environments.

Exit code handling:
- Exit 0: Merge succeeds, precommit passes
- Exit 1: Conflicts during Phase 3 (abort) OR precommit validation fails
- Exit 2: Fatal error (branch not found, clean tree check failed)

## Next Steps

Phase 7 continues with cycles 7.14+ (remaining merge ceremony phases and final checkpoint).
