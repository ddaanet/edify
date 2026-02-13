# Cycle 3.8: Error handling — section not found

**Status:** GREEN_VERIFIED

**Executed:** 2026-02-13

---

## Summary

Cycle 3.8 implements helpful error messages when section mode queries fail. When a section heading is not found, the error now lists available headings (up to 10) formatted with `.` prefix to guide users.

## RED Phase

**Test:** `test_section_not_found_lists_headings`

**Expected Failure:** Error message missing available headings list

**Actual Result:** FAIL as expected
```
AssertionError: assert "Section 'Nonexistent Section' not found." in 'Heading not found: Nonexistent Section'
```

Test correctly verified that section-not-found errors did not include helpful suggestions.

**Verification:** `pytest tests/test_when_resolver.py::test_section_not_found_lists_headings -v`

## GREEN Phase

**Implementation:**
- Modified `_resolve_section()` in `src/claudeutils/when/resolver.py` to build helpful error messages
- Extracted error message formatting into `_build_section_not_found_error()` helper function
- Error format: `"Section '<name>' not found.\nAvailable:\n  .Heading1\n  .Heading2"`
- Limited suggestions to first 10 items to prevent overwhelming output
- All headings collected from H2-level sections across all decision files

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  - Added `_build_section_not_found_error()` helper (lines 77-93)
  - Modified `_resolve_section()` to use helper when heading lookup fails (line 143)
- File: `tests/test_when_resolver.py`
  - Added `test_section_not_found_lists_headings()` test function

**Test Result:** PASS
```
tests/test_when_resolver.py::test_section_not_found_lists_headings PASSED
```

**Regression Check:** Full suite passes
```
Summary: 784/785 passed, 1 xfail
```

## REFACTOR Phase

**Formatting:** `just lint` — Reformatted resolver.py for style consistency

**Quality Check:** `just precommit`
- Initial result: Line limit exceeded (406 > 400 lines)
- Applied mitigation: Simplified docstring for `_build_section_not_found_error()` from 8 lines to 1 line
- Final result: 398 lines, all checks pass

**Refactoring Details:**
- Extracted error message building into separate helper function to reduce `_resolve_section()` complexity
- This improves code clarity and makes error handling testable independently
- No behavioral changes, only structural improvement

## Commits

**WIP Commit:** `747d79c`
```
WIP: Cycle 3.8 [Error handling — section not found]
```

**Files Modified:**
- `src/claudeutils/when/resolver.py` — Added error message formatting
- `tests/test_when_resolver.py` — Added test case

## Verification

- RED phase: Test failed as expected ✓
- GREEN phase: Test passes, no regressions ✓
- Refactor phase: Linting, precommit validation pass ✓
- Commit created and verified ✓

## Design Alignment

Cycle implements cycle spec exactly:
- Section-not-found error raised with ResolveError ✓
- Message contains "Section '<name>' not found." ✓
- Message contains "Available:" followed by list ✓
- Headings formatted as `.HeadingName` (one per line) ✓
- Limited to first 10 suggestions ✓
- Uses already-collected heading mapping from section mode ✓
