# Cycle 11.1: Update recall index parser for `/when` format

**Timestamp:** 2026-02-13

## Status: GREEN_VERIFIED

## Test Results

### RED Phase
- **Test command:** `pytest tests/test_recall_index_parser.py::test_recall_parser_when_format -v`
- **RED result:** FAIL as expected
  - Parser did not recognize `/when` or `/how` format entries
  - Only parsed old em-dash format entries

### GREEN Phase
- **Implementation:** Updated `parse_memory_index()` to detect and parse `/when` and `/how` prefixed entries
  - Detect `/when trigger | extras` and `/how trigger | extras` format
  - Extract trigger text as key
  - Extract keywords from trigger + extra keywords
  - Preserve backward compatibility with old em-dash format
  - Entry format examples:
    - `/when writing mock tests | mock patch, test doubles` → key="writing mock tests"
    - `/how structure test fixtures | setup, teardown` → key="structure test fixtures"
- **GREEN result:** PASS
  - `pytest tests/test_recall_index_parser.py::test_recall_parser_when_format -v` passes ✓
- **Regression check:** 805/806 passed, 1 xfail ✓
  - All existing em-dash format tests pass (backward compatibility maintained)

## Refactoring

### Formatting & Linting
- `just lint` passed (reformatted spacing around operator on line 151)

### Code Quality
- Precommit validation failure (memory-index.md format):
  - Validation error: memory-index.md entries missing `/when`/`/how` operator prefix
  - **Root cause:** Index file not yet migrated to new format (expected blocker)
  - **Impact:** Parser implementation correct; index file migration is separate phase work
  - **Status:** Not a code quality issue; validation infrastructure working as intended

## Files Modified

- `src/claudeutils/recall/index_parser.py` - Updated parser to support `/when`/`/how` format
- `tests/test_recall_index_parser.py` - Added comprehensive test for new format

## Stop Condition

**Status:** Precommit validation failure on memory-index.md format validation
- Parser implementation is complete and correct
- All tests pass with no regressions
- Memory-index.md migration (converting entries from em-dash to `/when`/`/how`) is separate work
- Code quality validated: linting passes, no warnings

## Decision Made

Parser designed to support both old (em-dash) and new (`/when`/`/how`) formats during transition period. This ensures:
- Existing tests remain passing
- Real memory-index.md file can be gradually migrated
- New format entries are correctly recognized and parsed

## Commit Status

- WIP commit created: `fb7cb9e` "WIP: Cycle 11.1 Update recall index parser for /when format"
- Ready for amend with final message pending resolution of precommit validation blocker
