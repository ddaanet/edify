# Cycle 4.5: Error handling (print to stderr, exit 1)

**Timestamp:** 2026-02-13

## Execution Summary

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_when_cli.py::test_cli_error_handling -v`
- **RED result:** FAIL as expected — errors not caught and printed to stderr
- **GREEN result:** PASS — all assertions satisfied
- **Regression check:** 791/792 passed, 1 xfail (no regressions)

## Implementation Details

**RED Phase Outcome:**
- Test: `test_cli_error_handling` added to `tests/test_when_cli.py`
- Verified three error scenarios:
  1. Nonexistent trigger: exit code 1, "Did you mean:" in output
  2. Nonexistent section (. prefix): exit code 1, "not found" in output
  3. Nonexistent file (.. prefix): exit code 1, "not found" in output
- Initial failure: ResolveError raised but not caught, no stderr output, exit code 1 from Click

**GREEN Phase Implementation:**
- File: `src/claudeutils/when/cli.py`
- Changes:
  - Added `import sys` for exit code
  - Imported `ResolveError` from resolver
  - Wrapped `resolve()` call in try/except block
  - Catch `ResolveError`: print to stderr via `click.echo(str(e), err=True)`, exit with `sys.exit(1)`
- Result: All three error scenarios now handled correctly

## Refactoring

- **Linting:** `just lint` passed, formatter adjusted test file whitespace
- **Precommit:** `just precommit` passed with no warnings
- **Quality check:** No complexity or line limit warnings

## Files Modified

- `src/claudeutils/when/cli.py` — Added error handling with stderr output
- `tests/test_when_cli.py` — Added `test_cli_error_handling()` test

## Stop Condition

None. Cycle completed successfully.

## Decision Made

Error handling follows Click pattern: catch domain errors, print to stderr via `click.echo(..., err=True)`, exit with code 1. This integrates cleanly with Click's error handling model.
