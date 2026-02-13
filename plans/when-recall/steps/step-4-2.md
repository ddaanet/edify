# Cycle 4.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.2: Operator argument (when/how)

**RED Phase:**

**Test:** `test_operator_argument_validation`
**Assertions:**
- CLI invoked with `claudeutils when when "writing mock tests"` → accepted (operator=when)
- CLI invoked with `claudeutils when how "encode paths"` → accepted (operator=how)
- CLI invoked with `claudeutils when what "some topic"` → rejected by Click (invalid choice)
- Error output contains "Invalid value" for invalid operator

**Expected failure:** AssertionError — operator not validated or all values accepted

**Why it fails:** Operator argument not yet constrained to when/how choices

**Verify RED:** `pytest tests/test_when_cli.py::test_operator_argument_validation -v`

**GREEN Phase:**

**Implementation:** Add operator as Click Choice argument.

**Behavior:**
- First positional argument: `operator` with `click.Choice(["when", "how"])`
- Invalid operators rejected by Click automatically with error message

**Approach:** `@click.argument("operator", type=click.Choice(["when", "how"]))`

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Add operator argument with Choice constraint
  Location hint: Command decorator arguments

**Verify GREEN:** `pytest tests/test_when_cli.py::test_operator_argument_validation -v`
**Verify no regression:** `pytest tests/ -q`

---
