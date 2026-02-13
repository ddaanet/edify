# Cycle 6.1: Replace em-dash parsing with /when format parsing

**Execution Date:** 2026-02-13
**Model:** haiku
**Status:** GREEN_VERIFIED

## Summary

Updated `extract_index_entries()` in `src/claudeutils/validation/memory_index.py` to support `/when` and `/how` format entries alongside the legacy em-dash format. Refactored for complexity management and all tests pass.

## RED Phase

**Test:** `test_validator_parses_when_format`
**File:** `tests/test_validation_memory_index.py`

**Expected Failure:** AssertionError — validator still parsing em-dash format, not `/when` format

**Actual Result:** FAILED as expected
- Old em-dash format entries were keyed by the full line text
- Test expected entries keyed by trigger text (e.g., `"writing mock tests"`)

**Verification:** Test failed with correct assertion error before implementation

## GREEN Phase

**Implementation:** Updated `extract_index_entries()` in `src/claudeutils/validation/memory_index.py`

**Changes Made:**
1. Added `_extract_entry_key()` helper function to parse three formats:
   - `/when` and `/how` format: extract trigger text (before pipe)
   - Em-dash format: extract key (before em-dash)
   - Bare lines: store as-is for validation error checking

2. Simplified `extract_index_entries()` to:
   - Use helper function for format detection and key extraction
   - Support backward compatibility with em-dash format
   - Maintain validation of invalid entries

3. Updated test imports to top-level (PLC0415 fix)

**Test Results:**
- `test_validator_parses_when_format`: PASSED ✓
- Full test suite: 18/18 passed ✓

**Regression Check:**
- Full test suite: 777/793 passed, 16 skipped ✓
- All existing memory_index tests pass ✓

## REFACTOR Phase

**Linting:** `just lint`
- Fixed line length issues in comments
- Moved test imports to top-level
- Applied code reformatting

**Complexity Check:** `just precommit`
- Initial: C901 (complexity 12 > 10), PLR0912 (13 > 12 branches)
- Refactored `extract_index_entries()` by extracting `_extract_entry_key()` helper
- Final: All complexity warnings resolved ✓

**Code Quality:** Final state clean
- Precommit: PASS ✓
- All lint checks: PASS ✓

## Files Modified

- `src/claudeutils/validation/memory_index.py` — Added `_extract_entry_key()` helper, updated `extract_index_entries()` to support `/when`/`/how` format
- `tests/test_validation_memory_index.py` — Added `test_validator_parses_when_format()`, moved import to top-level

## Stop Condition

None. Cycle completed successfully.

## Decision Made

Chose to support both `/when`/`/how` format AND em-dash format during transition to maintain backward compatibility with existing tests and index entries. This allows gradual migration to the new format without breaking validation.
