# Cycle 1.5: Malformed Entry Handling

**Timestamp:** 2026-02-12

## Status

GREEN_VERIFIED

## Test Execution

**Test command:** `pytest tests/test_when_index_parser.py::test_malformed_entries_skipped_gracefully -v`

**RED result:** FAIL as expected
- Assertion: `AssertionError: assert 3 == 2`
- Current implementation included "/when" (empty trigger) as valid entry, should skip it

**GREEN result:** PASS after implementation
- Graceful error handling added to parse_index function
- Malformed entries skipped, function never raises exceptions
- All 7 index_parser tests pass

**Regression check:** 770/771 passed (baseline: 770/771)
- No regressions introduced
- One expected xfail (markdown fixture known issue) unchanged

## Implementation Details

**File modified:** `src/claudeutils/when/index_parser.py`

**Changes:**
- Added try/except wrapper around file read with OSError/FileNotFoundError handling
- Wrapped entry parsing in try/except to catch ValidationError
- Line format check now uses explicit `line.startswith(("/when ", "/how "))` to skip malformed prefixes
- Logging warnings for empty triggers and validation errors

**File modified:** `tests/test_when_index_parser.py`

**Tests added:**
- `test_malformed_entries_skipped_gracefully()` - Core test verifying graceful degradation
- `test_empty_file_returns_empty_list()` - Edge case: empty file
- `test_headers_only_returns_empty_list()` - Edge case: only headers, no entries

## Refactoring

**Lint status:** PASS after reformatting
- Initial lint error: BLE001 - blind Exception catch
- Fixed: Changed `except Exception` to `except ValidationError`
- Added ValidationError import from pydantic

**Precommit status:** PASS (no warnings)
- No complexity warnings
- No line limit warnings
- Code quality baseline met

## Files Modified

- `src/claudeutils/when/index_parser.py`
- `tests/test_when_index_parser.py`

## Stop Conditions

None. Cycle completed successfully.

## Architecture Decision

Added ValidationError import to scope exception handling per BLE001 lint rule. Graceful degradation pattern: skip malformed entries with logging, never raise exceptions during parsing.
