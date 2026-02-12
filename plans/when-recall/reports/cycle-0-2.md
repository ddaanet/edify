# Cycle 0.2: Boundary bonus scoring

**Timestamp:** 2026-02-12

- Status: STOP_CONDITION
- Test command: `pytest tests/test_when_fuzzy.py::test_boundary_bonuses_applied -v`
- RED result: FAIL as expected (AssertionError: whitespace_bonus > no_bonus failed, both scores equal at 32.0)
- GREEN result: PASS
- Regression check: 742/758 passed, 16 skipped (no regressions)
- Refactoring: STOPPED at precommit — complexity warning (C901: cyclomatic complexity 12 > 10)
- Files modified:
  - src/claudeutils/when/fuzzy.py (added boundary bonus scoring logic)
  - tests/test_when_fuzzy.py (added test_boundary_bonuses_applied test)
- Stop condition: Precommit validation failed with complexity warning — escalating to refactor agent
- Decision made: Implemented boundary detection for whitespace (bonus 10), delimiters (bonus 9), and CamelCase transitions (bonus 7). Added first character match multiplier (×2). DP algorithm now tracks all bonus types during match scoring.

## Refactoring Required

**Issue:** Function `score_match` cyclomatic complexity = 12, exceeds limit of 10

**Location:** `src/claudeutils/when/fuzzy.py:4-64`

**Reason:** Nested conditionals for boundary type detection (whitespace/delimiter/CamelCase) added complexity without extraction.

**Suggested approach:** Extract boundary bonus calculation into separate helper function to reduce main function complexity and improve readability.
