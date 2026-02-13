# Cycle 6.3: Submodule-first removal ordering test

**Timestamp:** 2026-02-13

## Status

STOP_CONDITION: Precommit validation failure — line limit exceeded (401/400 lines)

## Execution Summary

### RED Phase
- Test: `test_rm_submodule_first_ordering`
- Expected: Test should fail (feature not yet tested)
- Actual: Test passes immediately
- Result: GREEN_VERIFIED (feature implementation already exists from cycle 6-1)

**Finding:** Cycle 6-1 implemented the submodule-first removal ordering and the `_remove_worktrees()` helper. This cycle's task was to write the test validating that ordering. Test correctly validates:
- Submodule worktree removed first via `git -C agent-core worktree remove --force`
- Parent worktree removed second via `git worktree remove --force`
- Both use `--force` flag
- Conditional execution based on registration flags

### GREEN Phase
- Implementation: Already exists (cycle 6-1)
- Test passes: ✓ (1/1)
- All tests pass: ✓ (779/780 passed, 1 xfail)
- No regressions: ✓

### REFACTOR Phase
- Linting: Fixed ANN202 (return type), ANN003 (**kwargs type), PLC0415 (import placement)
- Changes:
  - Moved `_remove_worktrees` import to top-level imports
  - Added proper type annotations: `subprocess.CompletedProcess[str]`
  - Added `**kwargs: object` annotation for mock_run

### Stop Condition: Line Limit Exceeded
- cli.py: 401 lines (limit: 400)
- Precommit validation failed
- Root cause: Implementation added in cycle 6-1 grew file size

## Files Modified
- `tests/test_worktree_commands.py` — added test_rm_submodule_first_ordering (39 lines)
- Linting reformatted both files

## Next Steps
Architectural refactoring needed to reduce cli.py below 400 lines. The file should be escalated to refactor agent for line-limit reduction. Possible approaches:
- Extract more helpers into separate module
- Consider splitting CLI commands into submodules
- Move utility functions to shared module

## Decision Made
None (feature validated, refactoring escalation required)
