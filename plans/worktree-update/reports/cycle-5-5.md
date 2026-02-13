# Cycle 5.5: Add `--task` option with `--session-md` default

**Timestamp:** 2026-02-12

## Execution Summary

- **Status:** STOP_CONDITION (quality-check: warnings found)
- **Test command:** `pytest tests/test_worktree_new.py::test_new_task_option -v`
- **RED result:** FAIL as expected
- **GREEN result:** PASS
- **Regression check:** 7/7 passed (all previous explicit mode tests still pass)
- **Refactoring:** none (precommit validation failed, awaiting refactor agent)
- **Files modified:**
  - `src/claudeutils/worktree/cli.py`
  - `tests/test_worktree_new.py`
- **Stop condition:** Architectural refactoring required
- **Decision made:** none

## Phase Results

### RED Phase
Wrote test `test_new_task_option` with assertions for:
- `--task` option works with default `--session-md`
- `--task` and slug are mutually exclusive
- `--session` is ignored with warning when `--task` provided
- Help text shows new options

Expected failure: click.UsageError (missing --task option)
Actual failure: Exit code 2 (--task option not recognized)
Status: VERIFIED - failure type matches

### GREEN Phase
Implementation added to `new()` command:
1. Made slug argument optional: `@click.argument('slug', required=False)`
2. Added `--task` option with help text
3. Added `--session-md` option with default 'agents/session.md'
4. Validation logic at function start:
   - Raise UsageError if both slug and --task provided
   - Raise UsageError if neither provided
   - Print warning and ignore --session if --task provided
5. When --task provided: derive slug, generate focused session
6. Type assertion before wt_path call to satisfy mypy

Test result: PASS
Regression check: 7/7 tests passed in test_worktree_new.py
Full test suite: 771/772 passed, 1 xfail (expected)
Status: VERIFIED - no regressions

### REFACTOR Phase
Lint: PASS (after formatting)
Precommit: FAILED - Quality issues found:
- `src/claudeutils/worktree/cli.py:283:5` - Too many branches (15 > 12)
- `src/claudeutils/worktree/cli.py:283:5` - Too many statements (58 > 50)
- `src/claudeutils/worktree/cli.py:283:5` - Too complex (14 > 10)
- File line limit: 421 > 400 (exceeds by 21 lines)
- Test file line limit: 457 > 400 (exceeds by 57 lines)

WIP commit created: e592cf4

Status: STOP - Escalating to refactor agent

## Architectural Notes

The `new()` function now handles two modes:
1. **Explicit mode:** slug argument provided directly
2. **Task mode:** --task option with session.md lookup

Both modes converge on a single slug that's used for branch creation.
The function complexity increased due to validation and session generation logic.
Line count growth is from:
- Test expansion: Added 40+ lines with new test function
- CLI expansion: Added ~20 lines of options and validation logic

Refactoring needed to extract task handling into separate function and potentially split test file.
