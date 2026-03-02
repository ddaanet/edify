# Cycle: Section-Aware Task Line Validation

**Date:** 2026-03-02

## Summary

Implemented section-aware task line validation for session.md files. Inside task sections (In-tree Tasks, Worktree Tasks, Pending Tasks), every non-blank, non-indented, non-comment line must be a valid task line or it produces an error.

## Execution

### RED Phase

**Test file created:** `tests/test_validation_section_aware.py`

**Tests written:** 17 test cases covering:
- Valid task lines in each section type (In-tree, Worktree, Pending)
- Blank lines (should be ignored)
- Indented sub-items (should be ignored)
- HTML comments (should be ignored)
- Invalid checkbox values (should error)
- Invalid model values (should error)
- Unparseable lines (should error)
- All valid checkbox values accepted
- All valid model values accepted
- Mixed valid/invalid content

**Expected failure:** `ImportError: cannot import name 'check_task_section_lines'`

**Actual failure:** Import error as expected. RED phase verified.

### GREEN Phase

**Implementation:** Added `check_task_section_lines(lines: list[str])` to `src/claudeutils/validation/session_structure.py`

**Implementation details:**
- Takes raw file lines (preserves indentation info)
- Tracks current section as it scans lines
- For task sections only, validates non-indented non-blank lines
- Uses `parse_task_line()` from shared parsing module
- Validates checkbox against `VALID_CHECKBOXES`
- Validates model against `VALID_MODELS` via `_check_invalid_model_in_line()`
- Helper function `_check_invalid_model_in_line()` checks for invalid model values in pipe-separated metadata

**Test result:** All 17 tests pass on first implementation attempt.

**Regression check:** Full test suite passes (1520/1521 passed, 1 xfail)

### REFACTOR Phase

**Linting:** Fixed:
- Line length issues (split long f-strings across multiple lines)
- Docstring blank line issues (added summary + description pattern)
- Type annotation issues (added explicit type annotations for empty dicts)

**Code quality:**
- No complexity warnings
- No architectural changes needed
- Section-aware validation correctly integrated into validate() function

**Final lint status:** All my code passes lint checks

### Files Modified

- `src/claudeutils/validation/session_structure.py` — Added `check_task_section_lines()` function, `_check_invalid_model_in_line()` helper, integrated into validate()
- `tests/test_validation_section_aware.py` — Created new test file with 17 comprehensive test cases

## Design Decisions

### Parse Layer vs Validation Layer

Following the design decision from brief.md:
- Parse layer (`parse_task_line`) is permissive — accepts any character in checkbox position
- Validation layer is strict — checks checkbox validity, model validity, and presence of required fields
- This separates extraction concerns from validation concerns

### Indentation Detection

Because `parse_sections()` strips all lines, I modified the approach:
- `check_task_section_lines()` receives raw file lines, not pre-sectioned/stripped content
- Directly scans lines, tracking current section
- Checks indentation on raw lines before stripping for validation
- This preserves the distinction between task lines and nested content

### Invalid Model Detection

The `parse_task_line()` function only returns valid models. To catch invalid models like "gpt4", I:
- Added `_check_invalid_model_in_line()` helper function
- Parses pipe-separated metadata directly
- Identifies segments that look like model names but aren't in VALID_MODELS
- Reports them as errors

## Test Coverage

All test cases pass:
- ✓ Valid task sections produce no errors
- ✓ Blank lines are ignored
- ✓ Indented content is ignored
- ✓ HTML comments are ignored
- ✓ Invalid checkboxes are caught
- ✓ Invalid models are caught
- ✓ Unparseable lines are caught
- ✓ All valid checkboxes accepted
- ✓ All valid models accepted
- ✓ Tasks without models are valid
- ✓ Non-task sections are not checked

## Stop Conditions

None encountered. Cycle completed successfully.

## Integration

The new validation is integrated into the main `validate()` function in `session_structure.py`. It runs as part of the session.md validation pipeline in precommit checks.

The implementation correctly handles:
- Real session.md files with nested task metadata
- Task lines with metadata (model tier, worktree markers, commands)
- Mixed valid and invalid content
- Legacy Pending Tasks section format
