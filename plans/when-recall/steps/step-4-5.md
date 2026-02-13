# Cycle 4.5

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.5: Error handling (print to stderr, exit 1)

**RED Phase:**

**Test:** `test_cli_error_handling`
**Assertions:**
- CLI with nonexistent trigger: exit code 1 (not 0)
- Error message printed to stderr (not stdout)
- Error message contains suggestion text ("Did you mean:" for trigger mode)
- CLI with nonexistent section: exit code 1, stderr contains "not found"
- CLI with nonexistent file: exit code 1, stderr contains "not found"

**Expected failure:** AssertionError — errors printed to stdout or exit code 0

**Why it fails:** Error handling not routing to stderr with correct exit code

**Verify RED:** `pytest tests/test_when_cli.py::test_cli_error_handling -v`

**GREEN Phase:**

**Implementation:** Add error handling with stderr output.

**Behavior:**
- Catch `ResolveError` from resolver
- Print error message to stderr via `click.echo(str(e), err=True)`
- Exit with code 1 via `sys.exit(1)` or `raise SystemExit(1)`

**Approach:** try/except around resolve call. Click's err=True for stderr.

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Add try/except for ResolveError, stderr output, exit code 1
  Location hint: Command function body, around resolve call

**Verify GREEN:** `pytest tests/test_when_cli.py::test_cli_error_handling -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 5: Bin Script Wrapper

**Type:** General
**Model:** haiku
**Dependencies:** Phase 4 (CLI must be registered in claudeutils)
**Files:** `agent-core/bin/when-resolve.py`

**Design reference:** Component Architecture (agent-core/bin/when-resolve.py)

---
