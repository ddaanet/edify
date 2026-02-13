# Cycle 2.1: Create `add_sandbox_dir()` — basic JSON read/write

**Timestamp:** 2026-02-12T16:36:00Z

## Status: GREEN_VERIFIED

## Execution Summary

### RED Phase
- **Test command:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_happy_path -v`
- **Result:** FAIL as expected (NameError: function `add_sandbox_dir` not defined)
- **Expected failure matched:** ✓ Function does not exist yet

### GREEN Phase
- **Test command:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_happy_path -v`
- **Result:** PASS ✓
- **Regression check:** All 11 tests pass (0 failures)

### Refactoring
- **Lint issues found:** 2 (D205 docstring format, PTH123 Path.open usage)
- **All fixed:** ✓
- **Precommit validation:** PASS ✓

## Implementation Details

**File:** `src/claudeutils/worktree/cli.py`

**Function:** `add_sandbox_dir(container: str | Path, settings_path: str | Path) -> None`

**Location:** Added after `derive_slug()` function, before CLI command group

**Behavior:**
1. Read settings file as JSON
2. Navigate to `permissions.additionalDirectories` array
3. Append new path (no deduplication)
4. Write JSON back with indent=2 formatting

**Code quality:**
- Used `Path.open()` for resource management
- Proper type hints (union types for input flexibility)
- Clear docstring with summary and description

## Files Modified
- `src/claudeutils/worktree/cli.py` — Added `add_sandbox_dir()` function
- `tests/test_worktree_cli.py` — Added `test_add_sandbox_dir_happy_path()` test

## Test Coverage

**New test:** `test_add_sandbox_dir_happy_path`
- Happy path: settings file with existing array
- Assertions: path appended, structure preserved, valid JSON, array order maintained
- Fixtures: Uses `tmp_path` for isolated test environment

## Notes

- Function is minimal and focused on happy path (no error handling for missing keys)
- Array order preserved (append not prepend)
- JSON indent=2 maintains readability
