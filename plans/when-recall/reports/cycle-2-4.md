# Cycle 2.4: Structural heading detection (skip `.` prefix)

**Timestamp:** 2026-02-12

## Execution Summary

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_when_navigation.py::test_structural_headings_skipped_as_nav_targets -v`
- **RED result:** FAIL as expected (ImportError — `compute_siblings` and `is_structural` flag not implemented)
- **GREEN result:** PASS after implementation
- **Regression check:** 774/775 passed (1 xfail — known), no new failures
- **Refactoring:** Applied docformatter, linter formatting
- **Files modified:**
  - `src/claudeutils/when/navigation.py` — Added `is_structural` field, structural heading detection, `compute_siblings` function
  - `tests/test_when_navigation.py` — Added `test_structural_headings_skipped_as_nav_targets` test
- **Stop condition:** None
- **Decision made:** None

## Implementation Details

### Changes to `src/claudeutils/when/navigation.py`

1. **HeadingInfo dataclass:** Added `is_structural: bool = False` field to track structural headings (those starting with `.`)

2. **extract_heading_hierarchy function:** Updated to detect `.` prefix in heading text and set `is_structural` flag accordingly

3. **compute_siblings function:** New function that computes sibling links (other entries under the same parent heading) with special handling:
   - Returns empty list if parent heading is structural (containers don't participate in sibling grouping)
   - Returns list of `/when trigger` links for non-structural siblings
   - Dependency injection: Takes `entries: list[WhenEntry]` to map entry triggers to headings

### Test Coverage

The new test `test_structural_headings_skipped_as_nav_targets` verifies:
1. Ancestor walks correctly include structural headings in the ancestor chain
2. HeadingInfo objects for structural headings have `is_structural=True`
3. `compute_siblings` returns empty list for entries under structural parent headings

## Verification

- **RED phase:** Test failed as expected with `ImportError` before implementation
- **GREEN phase:** Test passes after implementation; no regressions in full suite
- **Code quality:** All linters pass (ruff, docformatter, mypy)
- **Precommit:** All validations pass

## Next Steps

This cycle completes structural heading detection needed for Phase 2 navigation features.
