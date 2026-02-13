# Cycle 2.4: Deduplication logic — avoid adding existing paths

**Timestamp:** 2026-02-12T16:43:00Z

## Status: GREEN_VERIFIED

## Execution Summary

### RED Phase
- **Test command:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_deduplication -v`
- **Result:** FAIL as expected (AssertionError: duplicate path added to array)
- **Expected failure matched:** ✓ Function always appends without checking for existence

### GREEN Phase
- **Test command:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_deduplication -v`
- **Result:** PASS ✓
- **Regression check:** All 14 tests pass (0 failures)
  - New test: `test_add_sandbox_dir_deduplication`
  - Prior tests: `test_add_sandbox_dir_happy_path`, `test_add_sandbox_dir_missing_file`, `test_add_sandbox_dir_missing_keys`

### Refactoring
- **Lint issues found:** 0 (formatter reformatted test list assertions)
- **Precommit validation:** PASSED ✓
  - 763/764 passed, 1 xfail (expected)
  - No line limit violations
  - No complexity warnings

## Implementation Details

**File:** `src/claudeutils/worktree/cli.py`

**Changes to `add_sandbox_dir()` function:**

Added membership check before append to prevent duplicates:

**Before:**
```python
perms = settings.setdefault("permissions", {})
perms.setdefault("additionalDirectories", []).append(str(container))
```

**After:**
```python
perms = settings.setdefault("permissions", {})
dirs = perms.setdefault("additionalDirectories", [])
container_str = str(container)
if container_str not in dirs:
    dirs.append(container_str)
```

**Behavior:**
- Converts container to string once, storing in variable for clarity
- Checks if `container_str` already exists in `dirs` using simple `in` operator
- Only appends if not already present (idempotent)
- Uses exact string matching (no path normalization)
- Preserves order of existing paths

## Files Modified
- `src/claudeutils/worktree/cli.py` — Modified `add_sandbox_dir()` to add deduplication check before append
- `tests/test_worktree_cli.py` — Added `test_add_sandbox_dir_deduplication()` test

## Test Coverage

**New test:** `test_add_sandbox_dir_deduplication`
- Given settings file with `additionalDirectories: ["/path/a", "/path/b"]`
- Adding "/path/a" again: array unchanged (no duplicate)
- Adding "/path/c": array becomes `["/path/a", "/path/b", "/path/c"]`
- Adding "/path/a" again: array remains `["/path/a", "/path/b", "/path/c"]` (idempotent)
- Assertions: Deduplication works, order preserved, idempotence verified

**Regression:** All 14 prior tests pass

## Decision Made

TDD cycle 2.4 completed successfully. Deduplication logic makes `add_sandbox_dir()` idempotent—calling twice with the same path has same effect as calling once. Ready to proceed to Phase 2 checkpoint.
