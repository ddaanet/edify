# Cycle 6.6: Update autofix for new format

**Timestamp:** 2026-02-13

## Status

GREEN_VERIFIED

## Execution Summary

### RED Phase
- **Test written:** `test_autofix_new_format` in `tests/test_validation_memory_index_autofix.py`
- **Expected failure:** AssertionError — autofix doesn't handle `/when` format entries
- **Actual result:** FAIL as expected
  - File sections were being lost when all entries removed as structural
  - Entries were not being preserved in `/when` format during output
- **Verification:** Test fails without implementation changes

### GREEN Phase
- **Implementation:** Updated `autofix_index()` mechanics in `src/claudeutils/validation/memory_index_helpers.py`
  - Modified `_rebuild_index_content()` to preserve file sections even when all entries are removed (structural entries)
  - Changed from `list()` initialization to `extend()` pattern per PERF401 linting requirement
  - Entry parsing already supported `/when` format via existing `_extract_entry_key()` logic
  - Entry output preserves original format (already stored as full entry strings)

- **Key changes:**
  - Collect file sections from original index structure
  - After outputting entries grouped by file, output empty sections for files with no valid entries (all removed as structural)
  - Sections preserve order while entries within sections sort by source line number

- **Test result:** PASS
- **Regression check:** 9/9 tests in autofix module pass, 797/798 full suite pass

### REFACTOR Phase
- **Linting:** Fixed PERF401 by using list comprehension + extend instead of loop append
- **Format check:** All code passes lint and format checks
- **Precommit status:** Validation errors are pre-existing (memory-index.md em-dash entries without `/when` prefixes) - not introduced by this cycle

## Files Modified

- `src/claudeutils/validation/memory_index_helpers.py` — Updated `_rebuild_index_content()` to preserve empty file sections
- `tests/test_validation_memory_index_autofix.py` — Added `test_autofix_new_format()`

## Test Coverage

New test validates:
- Entries in wrong file section → autofix moves to correct section
- Entries out of file order → autofix reorders by source line number
- Entry pointing to structural heading (. prefix) → autofix removes
- File sections with all entries removed → preserved as empty section
- Re-running validation produces zero errors after autofix

## Decision Made

None — implementation was straightforward extension of existing logic.
