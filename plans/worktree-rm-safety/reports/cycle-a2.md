# Cycle A.2: `_is_submodule_dirty()` function

**Status:** GREEN_VERIFIED
**Timestamp:** 2026-02-17

## RED Phase

**Test command:** `pytest tests/test_worktree_rm.py::test_is_submodule_dirty -v`

**Expected failure:** ImportError (function does not exist)

**Result:** FAIL as expected
- Test module attempted to import `_is_submodule_dirty` from `claudeutils.worktree.utils`
- ImportError raised confirming function doesn't exist yet
- Exact failure message: `ImportError: cannot import name '_is_submodule_dirty'`

## GREEN Phase

**Implementation location:** `src/claudeutils/worktree/utils.py` (lines 95-111)

**Function signature:**
```python
def _is_submodule_dirty() -> bool:
    """Check if agent-core submodule has uncommitted changes.

    Returns False if agent-core/ does not exist or if status is clean. Returns
    True if submodule has uncommitted changes.
    """
```

**Behavior implemented:**
1. Returns `False` if `agent-core/` directory does not exist (no submodule in current context)
2. Uses `subprocess.run(["git", "-C", "agent-core", "status", "--porcelain"], check=False)` to check submodule status
3. Returns `True` if porcelain output is non-empty (any changes detected)
4. Returns `False` if porcelain output is empty (clean state)
5. Uses `check=False` to gracefully handle subprocess errors

**Test command:** `pytest tests/test_worktree_rm.py::test_is_submodule_dirty -v`

**Result:** PASS
- All three test cases passed:
  1. No `agent-core/` directory → returns `False`
  2. Directory exists with clean mocked status (empty stdout) → returns `False`
  3. Directory exists with dirty mocked status (non-empty stdout) → returns `True`

**Regression check:** `just test 2>&1 | tail -30`
- Result: 979/980 passed, 1 xfail (expected)
- No new failures introduced
- All existing tests continue to pass

## REFACTOR Phase

**Linting:** `just lint`
- Output: Files reformatted (`src/claudeutils/worktree/utils.py`, `tests/test_worktree_rm.py`)
- No lint errors in modified files
- Pre-existing warning in `tests/fixtures_worktree.py` (RUF100) - outside scope of this cycle

**Precommit validation:** `just precommit`
- Result: PASS
- All checks passed (formatting, linting, tests)

**Files modified:**
- `src/claudeutils/worktree/utils.py` — Added `_is_submodule_dirty()` function
- `tests/test_worktree_rm.py` — Added `test_is_submodule_dirty()` test; updated import statement

**Refactoring notes:** None - implementation required no refactoring beyond linting

## Summary

- RED: ✓ Test failed with expected ImportError
- GREEN: ✓ Test passed, no regressions
- REFACTOR: ✓ Linting and precommit validation passed
- **Cycle complete and ready to commit**
