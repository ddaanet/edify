# Cycle 1.4: Validate format (operator prefix, pipe separator)

**Timestamp:** 2026-02-12

**Status:** GREEN_VERIFIED

## Execution Summary

### RED Phase
- **Test command:** `pytest tests/test_when_index_parser.py::test_format_validation -v`
- **Result:** FAILED as expected
  - Assertion: `assert len(entries) == 2` (actual: 4)
  - Empty triggers were accepted instead of being skipped
  - Invalid entries included: empty trigger with extras

### GREEN Phase
- **Test command:** `pytest tests/test_when_index_parser.py::test_format_validation -v`
- **Result:** PASSED
- **Implementation:**
  - Added validation check after trigger parsing: `if not trigger: continue`
  - Added logging with `logger.warning()` for skipped entries with empty triggers
  - Returns only valid entries (non-empty triggers)
  - Extra triggers: empty segments silently dropped (as per spec), no warnings

**Changes made:**
- `src/claudeutils/when/index_parser.py`: Added trigger non-empty validation, import logging module, logger configuration

### Regression Check
- **Full test suite:** 767/768 passed, 1 xfail — ✓ No regressions
- **Index parser tests:** 4/4 passed

### Refactoring
- Ran `just lint` — ✓ All checks passed (fixed f-string in logger call)
- Ran `just precommit` — ✓ All checks passed, no warnings

**Lint fix:** Replaced f-string with %-formatting in logging statement (G004 compliance)

### Files Modified
- `src/claudeutils/when/index_parser.py` (parsing logic + validation)
- `tests/test_when_index_parser.py` (test_format_validation)

### Stop Condition
- None

### Decision Made
- Validation occurs after trigger extraction, before entry construction (clear separation of parsing vs. validation)
- Empty trigger is the only validation criterion at parse time (design specifies trigger must be non-empty after stripping)
- Warning logged with line number and original line content for debugging
