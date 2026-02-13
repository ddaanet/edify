# Cycle 2.2: Missing file handling — create from scratch

**Timestamp:** 2026-02-12T17:05:00Z

## Status: STOP_CONDITION (Refactoring exceeded line limit)

## Execution Summary

### RED Phase
- **Test command:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_missing_file -v`
- **Result:** FAIL as expected (FileNotFoundError when reading nonexistent file)
- **Expected failure matched:** ✓ File does not exist, function tries to read it

### GREEN Phase
- **Test command:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_missing_file -v`
- **Result:** PASS ✓
- **Regression check:** All 12 tests pass, including `test_add_sandbox_dir_happy_path` (0 failures)

### Refactoring
- **Lint issues found:** 0
- **Precommit validation:** FAILED
  - Line limit violation: 401 lines (exceeds 400 line limit)
  - Cause: Added `from typing import Any` import (1 line) + type annotation split across 2 lines

## Implementation Details

**File:** `src/claudeutils/worktree/cli.py`

**Changes to `add_sandbox_dir()` function:**

1. Added file existence check at start of function
2. If file doesn't exist:
   - Create parent directories with `mkdir(parents=True, exist_ok=True)`
   - Initialize settings dict with minimal structure: `{"permissions": {"additionalDirectories": []}}`
3. Proceed with normal append logic

**Type annotation:**
- Added `from typing import Any` to imports
- Annotated initial settings dict: `settings: dict[str, Any]`

**Behavior:**
- Handles both cases: existing file (read and update) or missing file (create new)
- Creates parent directories automatically when needed
- Initializes with correct nested structure for subsequent append operations

## Files Modified
- `src/claudeutils/worktree/cli.py` — Modified `add_sandbox_dir()` function, added typing import
- `tests/test_worktree_cli.py` — Added `test_add_sandbox_dir_missing_file()` test

## Test Coverage

**New test:** `test_add_sandbox_dir_missing_file`
- Verifies file creation when nonexistent
- Assertions: file created, valid JSON, correct nested structure, array contains new path
- Fixtures: Uses `tmp_path` with nested directory path

**Regression:** `test_add_sandbox_dir_happy_path` still passes with modified function

## Stop Condition

**Reason:** Precommit validation failed due to line limit exceeded

**Current state:** 401 lines (limit: 400)
- File was already at 397 lines (Cycle 2.1)
- Added 4 lines: import statement + type annotation
- Exceeds limit by 1 line

**Options for resolution:**
1. Extract architectural component (split CLI functions into separate module)
2. Reduce verbosity elsewhere in file (requires refactor agent expertise)
3. Defer this cycle and handle line limit holistically in refactor phase

**Recommendation:** Escalate to orchestrator for refactoring guidance. File needs architectural split or comprehensive line reduction, not trivial fixes.

## Decision Made

TDD cycle 2.2 completed (RED and GREEN phases successful), but refactoring gate blocked by precommit. Escalating for architectural refactoring of worktree/cli.py module.
