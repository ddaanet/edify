# Cycle 3.3: Section Mode — Global Unique Heading Lookup

**Timestamp:** 2026-02-13

## Execution Summary

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_when_resolver.py::test_section_mode_resolves -v`
- **RED result:** FAIL as expected (section mode returned stub "section" string instead of resolved content)
- **GREEN result:** PASS (implemented full section mode resolution)
- **Regression check:** 779/780 passed (no regressions)
- **Refactoring:** Type annotations added to heading_to_files dict, TRY003 linting fix (error message moved outside exception raise)
- **Files modified:** src/claudeutils/when/resolver.py, tests/test_when_resolver.py
- **Stop condition:** None
- **Decision made:** ResolveError exception class created for section/trigger mode errors (unified error handling)

## Implementation Details

### Section Mode Implementation

Added `_resolve_section()` function to handle ".section" prefix queries:

1. **Heading Scan:** Walks all .md files in decisions_dir, collects H2 headings with file paths
2. **Case-Insensitive Lookup:** Normalizes query and heading to lowercase for matching
3. **Uniqueness Validation:** Raises ResolveError if heading exists in multiple files
4. **Content Extraction:** Uses existing `_extract_section()` to return heading + section content

### Test Coverage

- `test_section_mode_resolves`: Tests unique heading lookup with boundary verification and case-insensitive matching
- `test_mode_detection`: Updated to verify section mode resolves to content (not stub string)
- No changes to trigger mode tests; all pass

### Error Handling

- Created `ResolveError` exception class for uniform error signaling
- Updated `_resolve_trigger()` to raise ResolveError instead of ValueError for consistency
- Both modes now provide clear error messages for missing/ambiguous headings

## Verification

- All resolver tests pass
- Full test suite passes (779/780, 1 xfail from unrelated test)
- Lint/precommit validation passes with no warnings
