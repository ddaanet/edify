# Cycle C.2: Add --force flag to _worktree rm

**Status:** STOP_CONDITION (quality-check: warnings found)
**Timestamp:** 2026-02-17

## Phases

### RED Phase
- **Test command:** `pytest tests/test_worktree_rm.py::test_rm_force_bypasses_confirm tests/test_worktree_rm_dirty.py::test_rm_force_bypasses_dirty_check tests/test_worktree_rm_guard.py::test_rm_force_bypasses_guard -xvs`
- **Result:** FAIL as expected (--force flag not recognized)
- **Evidence:** All 3 tests failed with "No such option: --force" in initial run

### GREEN Phase
- **Test command:** Same as RED
- **Result:** PASS
- **Evidence:** All 3 tests passed after implementation
- **Full suite regression check:** 986/987 passed, 1 xfail (expected)

### REFACTOR Phase

#### Step 1: Format & Lint
- Ran `just lint`
- No formatting errors

#### Step 3: Quality Check
- Ran `just precommit`
- **WARNINGS FOUND:**
  - `src/claudeutils/worktree/cli.py`: 401 lines (exceeds 400 line limit) — added 11 lines
  - `tests/test_worktree_rm.py`: 415 lines (exceeds 400 line limit) — added 21 lines

## Files Modified
- `src/claudeutils/worktree/cli.py` (390 → 401 lines)
- `tests/test_worktree_rm.py` (394 → 415 lines)
- `tests/test_worktree_rm_dirty.py` (59 → 76 lines, under limit)
- `tests/test_worktree_rm_guard.py` (315 → 329 lines, under limit)

## Implementation Summary

**Changes to cli.py:**
- Added `--force` flag option to `rm` command
- Modified confirm check: skipped when `force=True`
- Modified dirty checks: both parent and submodule checks skipped when `force=True`
- Set `removal_type = "focused"` when force skips guard (uses `-D` for branch deletion)

**Tests added:**
- `test_rm_force_bypasses_confirm`: Verifies removal without --confirm when --force used
- `test_rm_force_bypasses_dirty_check`: Verifies removal despite dirty parent repo when --force used
- `test_rm_force_bypasses_guard`: Verifies removal of unmerged branch when --force used

## Stop Condition

**Quality check triggered refactoring escalation:** Line limit warnings require refactoring to consolidate or extract code. Delegating to refactor agent (Sonnet) for architectural refactoring guidance.

**Rollback point:** WIP commit `f2e64e2b` preserves working implementation for refactor agent to improve.

## Decision Made
None (implementation straightforward, escalation is due to quality threshold, not architecture).
