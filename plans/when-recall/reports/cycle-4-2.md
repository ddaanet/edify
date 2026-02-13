# Cycle 4.2: Operator argument (when/how)

**Timestamp:** 2026-02-13

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_when_cli.py::test_operator_argument_validation -v`

**RED result:** FAIL as expected — operator not constrained to valid choices, invalid 'what' operator accepted with exit_code 0

**GREEN result:** PASS — operator argument now validated with `click.Choice(["when", "how"])`

**Regression check:** 788/789 passed (1 xfail) — no regressions

**Refactoring:** none

**Files modified:**
- `src/claudeutils/when/cli.py` — Added `type=click.Choice(["when", "how"])` to operator argument
- `tests/test_when_cli.py` — Added `test_operator_argument_validation()` with assertions for valid/invalid operators

**Stop condition:** none

**Decision made:** none
