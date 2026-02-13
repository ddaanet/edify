# Cycle 3.2: Trigger mode resolution

**Timestamp:** 2026-02-13 | **Model:** haiku | **Status:** GREEN_VERIFIED

## RED Phase

**Test:** `test_trigger_mode_resolves`

**Expected Failure:** AssertionError — resolve() returns incorrect content

**Actual Result:** Test fails as expected
```
AssertionError: assert '# When Writing Mock Tests' in 'trigger'
```

**Verification:** RED phase complete ✓

## GREEN Phase

**Implementation:** Trigger mode resolution in `src/claudeutils/when/resolver.py`

**Key Components:**
- `_resolve_trigger()` — Parses index entries, builds fuzzy-matchable candidates with operator+trigger format, fuzzy matches query against candidates
- `_build_heading()` — Generates markdown heading from operator and trigger (e.g., "writing mock tests" → "## When Writing Mock Tests")
- `_extract_section()` — Reads decision file, extracts content from target heading through next same-level heading

**Test Result:**
```
tests/test_when_resolver.py::test_trigger_mode_resolves PASSED
tests/test_when_resolver.py::test_mode_detection PASSED
```

**Regression Check:** 778/779 tests pass (1 xfail expected)
- ✓ No test regressions introduced

## REFACTOR Phase

**Linting:**
```
Fixed:
- ARG001: Unused argument 'mode' → renamed to '_mode'
- TRY003 (2 instances): Long exception messages → assigned to variable first
- D205: Docstring formatting → added blank line between summary and description
```

**Quality Check:**
- `just lint` ✓ PASS
- `just precommit` ✓ PASS
- No complexity warnings
- No line-limit violations

## Files Modified

| File | Changes |
|------|---------|
| `src/claudeutils/when/resolver.py` | 226 lines added: `resolve()` routing, `_resolve_trigger()` implementation, `_build_heading()` helper, `_extract_section()` content extraction |
| `tests/test_when_resolver.py` | 24 lines modified: Updated `test_mode_detection()` for new behavior, added `test_trigger_mode_resolves()` |

## Commit

**WIP Commit:** `398d078 WIP: Cycle 3.2 Trigger mode resolution`

**Pre-commit Status:** Clean tree ✓

## Summary

Trigger mode resolution implemented and tested. Fuzzy matching against index entries locates best-match trigger, which maps to decision file heading. Section content extracted and returned on successful match. All tests pass, linting clean, precommit validation passes.

Next: Cycle 3.3 will implement section mode resolution (`.Section Title` syntax).
