# Cycle 2.1: Extract Heading Hierarchy from File Content

**Timestamp:** 2026-02-12

## Status

GREEN_VERIFIED

## Test Execution

**Test command:** `pytest tests/test_when_navigation.py::test_extract_heading_hierarchy`

**RED result:** FAIL as expected
- Error: `ModuleNotFoundError: No module named 'claudeutils.when.navigation'`
- Module `src/claudeutils/when/navigation.py` did not exist

**GREEN result:** PASS after implementation
- Created `navigation.py` with `extract_heading_hierarchy` function
- Stack-based heading parser tracks parent relationships
- Returns dict mapping heading text to HeadingInfo (level, parent, line_number)
- Test assertions all pass: parent mapping, nesting levels (H2→H3→H4)

**Regression check:** 771/772 passed (baseline: 771/772)
- No regressions introduced
- One expected xfail (markdown fixture known issue) unchanged

## Implementation Details

**File created:** `src/claudeutils/when/navigation.py`

**Components:**
- `HeadingInfo` dataclass: Stores heading text, level, parent reference, line_number
- `extract_heading_hierarchy(content: str) -> dict[str, HeadingInfo]`: Main function
  - Parses markdown line-by-line
  - Maintains stack of (level, text) tuples to track nesting
  - Pops stack when encountering same-level or lower-level heading
  - Parent is the top of stack before pushing new heading

**File created:** `tests/test_when_navigation.py`

**Test cases:**
- `test_extract_heading_hierarchy()`: Comprehensive test covering multiple patterns
  - H2 sections with H3 subsections (A1, A2 under Section A)
  - Nested H4: A→B→C hierarchy
  - Verifies parent mapping and level values

## Refactoring

**Lint status:** PASS after reformatting
- Initial: Type hints used `Dict`, `list` from typing
- Fixed: Auto-formatted to lowercase builtins `dict`, `list` (Python 3.9+)
- Removed unused `Dict` import from typing

**Precommit status:** PASS (no warnings)
- No complexity warnings
- No line limit warnings
- Code quality baseline met

## Files Modified

- `src/claudeutils/when/navigation.py` (created)
- `tests/test_when_navigation.py` (created)

## Stop Conditions

None. Cycle completed successfully.

## Architecture Decision

Stack-based hierarchy extraction chosen for simplicity and clarity. Maintains O(n) complexity with single pass. Parent tracking via stack enables arbitrary nesting depth without additional complexity.
