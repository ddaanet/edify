# Cycle 4.1: Click command setup

**Timestamp:** 2026-02-13

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_when_cli.py::test_when_command_exists -v`

**RED result:** FAIL as expected (ModuleNotFoundError: No module named 'claudeutils.when.cli')

**GREEN result:** PASS (1/1 test passed)

**Regression check:** 772/788 passed (no regressions)

**Refactoring:**
- Ran `just lint` — PASS
- Ran `just precommit` — PASS
- No complexity warnings or line limit issues

**Files modified:**
- `src/claudeutils/when/cli.py` (created) — Click command definition
- `tests/test_when_cli.py` (created) — Test for command existence and help
- `src/claudeutils/cli.py` (modified) — Added import and registration of when_cmd

**Stop condition:** None

**Decision made:** None — followed existing pattern from recall/statusline/validate commands
