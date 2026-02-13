### Cycle 4.4: Invoke resolver with joined query [2026-02-13]

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_when_cli.py::test_cli_invokes_resolver -v`
- **RED result:** FAIL as expected — CLI echoed "Operator: when, Query: writing mock tests" instead of calling resolver
- **GREEN result:** PASS — CLI now invokes resolver and prints resolved content with headings and navigation
- **Regression check:** 775/775 passed (all tests pass, no regressions)
- **Refactoring:** Applied noqa suppression for intentionally unused operator argument (Click requires parameter name to match decorator)
- **Files modified:**
  - `src/claudeutils/when/cli.py` — Connected CLI to resolver, added project root detection via CLAUDE_PROJECT_DIR env var
  - `tests/test_when_cli.py` — Added `test_cli_invokes_resolver` test; updated existing tests to mock resolver for argument validation testing
- **Stop condition:** none
- **Decision made:** Operator argument is required by Click decorator but not used in function body (resolver infers operator from trigger text). Used noqa suppression rather than underscore prefix to maintain Click's argument-to-parameter mapping.

