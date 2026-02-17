# Cycle C.1: Add `--confirm` flag to `_worktree rm`

**Timestamp:** 2026-02-17T00:00:00Z
**Status:** STOP_CONDITION

## Summary

Implemented FR-4 requirement: prevent direct CLI removal without skill workflow by adding a `--confirm` flag.

## RED Phase

**Test:** `test_rm_refuses_without_confirm` in `tests/test_worktree_rm.py`

- Creates worktree with `init_repo` and `_create_worktree`
- Invokes `worktree rm test-feature` WITHOUT `--confirm`
- Asserts `exit_code == 2`
- Asserts output contains "confirm" or "skill"

**Result:** FAIL as expected (exit_code was 0, expected 2) ✓

## GREEN Phase

**Implementation:**

1. Added `--confirm` flag to `rm` command decorator in `src/claudeutils/worktree/cli.py:366-371`
2. Added guard at start of `rm` function body (lines 369-375):
   ```python
   if not confirm:
       click.echo(
           f"Use the worktree skill (wt merge {slug}) to remove worktrees safely. "
           "Pass --confirm to invoke directly.",
           err=True,
       )
       raise SystemExit(2)
   ```
3. Updated all `rm` invocations to include `--confirm` in:
   - `tests/test_worktree_rm.py` — 7 invocations
   - `tests/test_worktree_rm_guard.py` — 9 invocations
   - `tests/test_worktree_commands.py` — 9 invocations
   - `tests/test_worktree_session_automation.py` — 2 invocations

**Result:** All tests PASS (981/982 passed, 1 xfail expected) ✓

## Regression Check

Full test suite: **981/982 passed, 1 xfail** (the xfail is pre-existing markdown test) ✓

## REFACTOR Phase

### Step 1: Format & Lint
- `just lint` passed ✓
- Fixed FBT001 warning by adding `# noqa: FBT001` to function signature (Click option boolean is idiomatic)
- All formatting issues resolved ✓

### Step 2: Intermediate Commit
- Created WIP commit: `967323b8 WIP: Cycle C.1 Add --confirm flag to _worktree rm` ✓

### Step 3: Quality Check
- Ran `just precommit` — **WARNINGS FOUND**:
  - `src/claudeutils/worktree/cli.py`: 411 lines (exceeds 400 line limit)
  - `tests/test_worktree_rm.py`: 413 lines (exceeds 400 line limit)

### Step 4: Escalate Refactoring

**STOP CONDITION TRIGGERED:** Precommit quality check found warnings.

- cli.py grew from 397 → 411 lines (+14 lines) due to 9-line confirm guard + decorators
- test_worktree_rm.py grew from 393 → 413 lines (+20 lines) due to 23-line new test + imports

Both files now exceed the 400-line quality threshold. Requires refactoring to bring under limit.

## Files Modified

- `src/claudeutils/worktree/cli.py` — Added --confirm flag and guard check
- `tests/test_worktree_rm.py` — Updated existing tests, added new test
- `tests/test_worktree_rm_guard.py` — Updated all rm invocations to include --confirm
- `tests/test_worktree_commands.py` — Updated all rm invocations to include --confirm
- `tests/test_worktree_session_automation.py` — Updated all rm invocations to include --confirm

## Stop Condition

**Reason:** Precommit validation found line limit warnings

**Warnings:**
- cli.py: 411 lines (exceeds 400)
- test_worktree_rm.py: 413 lines (exceeds 400)

**Decision:** Stop and escalate to refactor agent for restructuring.

**State:** WIP commit created, clean tree, ready for refactoring.
