# Cycle 2.6: Format navigation links

**Timestamp:** 2026-02-12

## Status

GREEN_VERIFIED

## Execution Summary

**RED Phase:**
- Test: `test_format_navigation_output`
- Expected failure: `ImportError` — function not imported
- Actual failure: `ImportError: cannot import name 'format_navigation'` ✓
- Result: RED verified as expected

**GREEN Phase:**
- Implementation: `format_navigation(ancestors: list[str], siblings: list[str]) -> str`
- Location: `src/claudeutils/when/navigation.py`, end of module
- Behavior:
  - Format "Broader:" section with ancestor links (one per line)
  - Format "Related:" section with sibling links (one per line)
  - Blank line between sections
  - Omit sections with no links
  - Return empty string if both sections empty
- Test result: PASS ✓

**Regression check:**
- Full suite: 776/777 passed, 1 xfail
- No new failures ✓

## Refactoring

**Lint/format:** `just lint` → PASS
**Precommit:** `just precommit` → PASS (no warnings)
**No complex refactoring needed**

## Files Modified

- `src/claudeutils/when/navigation.py` — Added `format_navigation()` function (16 lines)
- `tests/test_when_navigation.py` — Added test import and `test_format_navigation_output` test (39 lines)

## Implementation Details

The function uses conditional section building:
1. Build "Broader:" section if ancestors non-empty
2. Build "Related:" section if siblings non-empty
3. Join sections with blank line separator
4. Return joined result (empty string if no sections)

String formatting is straightforward: `"\n".join()` for list items, `"\n\n".join()` for sections.

## Stop Condition

None. Cycle completed successfully.

## Decision Made

None. Implementation straightforward per spec.

## Test Evidence

```
test_format_navigation_output PASSED:
- Both sections present: sections separated by blank line ✓
- Ancestors only: Related section omitted ✓
- Siblings only: Broader section omitted ✓
- Both empty: returns empty string ✓
```
