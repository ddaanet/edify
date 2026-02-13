# Cycle 3.5: Section content extraction

**Timestamp:** 2026-02-13

## Execution Summary

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_when_resolver.py::test_section_content_extraction -v`
- **RED result:** FAIL as expected (ImportError: cannot import _extract_section_content)
- **GREEN result:** PASS
- **Regression check:** 781/782 passed (all passing tests maintained)

## Changes

### Implementation Details

**File modified:** `src/claudeutils/when/resolver.py`

Added `_extract_section_content(heading, file_content)` helper function that:
- Finds target heading line in file content
- Detects heading level from the number of leading `#` characters
- Scans forward collecting lines until next heading of same or higher level
- Returns content including heading but excluding next boundary heading
- Handles both nested (H2/H3) and flat (all H2) heading structures

Refactored existing `_extract_section(file_path, heading)` to use the new helper function internally.

### Test Coverage

**File modified:** `tests/test_when_resolver.py`

Added `test_section_content_extraction()` test covering:
- Nested H2/H3 structure: extracting H3 heading returns only that child's content
- Flat H2 structure: extracting H2 heading returns content until next H2
- Last heading in file: extraction extends to EOF
- Boundary exclusivity: next heading not included in extracted content
- Import added to top-level imports for consistency

## Phase Checkpoint

Section mode (cycle 3.4) and section content extraction (cycle 3.5) are complete. Resolver can now:
- Locate unique headings globally across decision files (cycle 3.4)
- Extract content boundaries correctly for both nested and flat heading structures (cycle 3.5)

Next cycle (3.6) will integrate both components into a unified section lookup workflow.

## Verification

- Lint: ✓ No errors
- Precommit: ✓ No warnings
- Full test suite: ✓ 781/782 passed (1 xfail expected)
- Tree state: ✓ Clean
