# Cycle 3.6: Output formatting (heading + content + navigation links)

**Timestamp:** 2026-02-13T18:35:00Z

## Status: GREEN_VERIFIED

## Test Execution

**Test command:** `pytest tests/test_when_resolver.py::test_resolve_output_format -v`

**RED phase result:** FAIL as expected
- Output did not include navigation sections (Broader:, Related:)
- AssertionError on missing navigation links

**GREEN phase result:** PASS
- Test passes after implementation
- Full resolve output now includes heading, content, and navigation links
- Heading formatted as H1 regardless of source level
- Navigation includes file link and sibling links

**Regression check:** All tests pass (782/783)
- One xfail expected (unrelated to this cycle)
- Updated test_trigger_mode_resolves to expect H1 format

## Implementation Summary

**Files modified:**
- `src/claudeutils/when/resolver.py` — Integrated navigation module output into resolve return value
- `tests/test_when_resolver.py` — Added test_resolve_output_format and updated test_trigger_mode_resolves

**Changes in resolver.py:**
1. Added import: `from claudeutils.when import navigation`
2. Modified `_resolve_trigger()` to:
   - Call `navigation.compute_ancestors()` after extracting section
   - Call `navigation.compute_siblings()` with entries list
   - Format heading as H1 regardless of source level
   - Append formatted navigation (Broader: and Related: sections)
3. Modified `_build_heading()` to return text only (without # markers) for reusability
4. Added heading text processing to find actual heading line in file (handles H2/H3/H4 levels)

**Approach used:**
- Heading text built from operator + trigger
- Actual heading line located by matching heading text (finds H2, H3, or H4)
- Section content extracted from actual heading
- Navigation computed using heading text without # markers
- All parts combined: formatted H1 heading + content + navigation

## Quality Checks

**Linting:** PASS
- Imports formatted by ruff (single-line import)
- Line length violations fixed (one comment shortened)
- All tests pass

**Precommit:** PASS
- No complexity warnings
- No line limit violations
- All validation checks passed

## Refactoring Notes

None — code is minimal and focused. Navigation integration follows existing patterns (defer to navigation module for computation, combine results in resolver).

## Files Changed

- `/Users/david/code/claudeutils-wt/when-recall/src/claudeutils/when/resolver.py` — 74 lines modified
- `/Users/david/code/claudeutils-wt/when-recall/tests/test_when_resolver.py` — 59 lines added/modified

## Next Cycle

3.7: Trigger mode error output with suggestions
