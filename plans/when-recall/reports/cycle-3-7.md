# Cycle 3.7: Error handling — trigger not found

**Timestamp:** 2026-02-13

## Summary

Implemented error handling for trigger mode when no fuzzy match is found. Error messages now include up to 3 closest fuzzy suggestions formatted as `/when <trigger>` for user guidance.

## Status

- RED: ✓ VERIFIED — Test failed as expected (error message missing suggestions)
- GREEN: ✓ VERIFIED — Test passes, no regressions (783/784 passed)
- REFACTOR: ✓ COMPLETED — Code quality checks pass

## Phase Results

### RED Phase

**Test written:** `test_trigger_not_found_suggests_matches` in `tests/test_when_resolver.py`

**Expected failure:** ResolveError raised without suggestions/proper format
**Actual failure:** Error message contained "No match for" but lacked "Did you mean:" and suggestions
**Result:** ✓ PASS — Test failed as expected

### GREEN Phase

**Implementation:** Modified `_resolve_trigger()` in `src/claudeutils/when/resolver.py`

**Changes:**
1. Added `_get_suggestions(query, candidates, limit=3)` helper: scores all candidates without threshold filtering, returns top N by match count
2. Added `_get_partial_match_score(query, candidate)` helper: counts query characters matched in order within candidate
3. Modified `_resolve_trigger()` to call `_handle_no_match()` when fuzzy.rank_matches() returns empty
4. Added `_handle_no_match()` helper: formats error with "Did you mean:" followed by up to 3 suggestions

**Test result:** ✓ PASS
**Regression check:** ✓ 783/784 tests pass, 1 xfail (pre-existing)

### REFACTOR Phase

**Quality checks executed:**

1. **Format/Lint:** `just lint` → passed (formatter reformatted code, no errors)
2. **Precommit validation:** `just precommit` → passed
   - No complexity warnings after extraction of helpers
   - No line limit violations (383 lines, <400)
   - All type annotations correct

**Refactoring applied:**

1. Extracted `_handle_no_match()` to reduce trigger function complexity
2. Extracted `_load_matched_entry()` to handle entry lookup
3. Shortened verbose docstrings to stay under line limit

**Result:** ✓ PASS — All quality checks pass

## Files Modified

- `src/claudeutils/when/resolver.py` (added helper functions, modified error handling)
- `tests/test_when_resolver.py` (added test case)

## Commit Information

- **WIP commit:** 50b266f (WIP: Cycle 3.7 Error handling — trigger not found)
- **Changes:** 2 files changed, 135 insertions(+), 27 deletions(-)

## Stop Conditions

- None — cycle completed successfully

## Decision Made

- **Suggestion scoring:** Used simple character-match counting (characters matched in order) rather than full fuzzy scoring to ensure suggestions are always available, even when query doesn't meet threshold
- **Helper extraction:** Split `_resolve_trigger()` into three helpers to reduce complexity below linting thresholds while keeping trigger logic readable
