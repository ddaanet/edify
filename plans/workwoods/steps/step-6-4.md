# Cycle 6.4

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

### Cycle 6.4: Integration with validation CLI (replace jobs validator)

**RED Phase:**

**Test:** `test_cli_integration_calls_planstate_validator`
**Assertions:**
- `claudeutils validate` calls planstate validator
- `claudeutils validate planstate` subcommand exists
- Validator errors appear in CLI output
- Exit code 1 on validation errors

**Expected failure:** Planstate validator not registered in CLI

**Why it fails:** CLI doesn't know about planstate validator yet

**Verify RED:** `pytest tests/test_validation_planstate.py::test_cli_integration_calls_planstate_validator -v`

**GREEN Phase:**

**Implementation:** Register planstate validator in validation/cli.py

**Behavior:**
- Import validate_planstate from validation.planstate
- Add _run_validator("planstate", validate_planstate, all_errors, root) in _run_all_validators()
- Add @validate.command() for planstate subcommand

**Approach:** Follow same pattern as jobs validator (lines 70, 148-156 in cli.py)

**Changes:**
- File: `src/claudeutils/validation/cli.py`
  Action: Add planstate validator to _run_all_validators()
  Location hint: After jobs validator call (line ~70)

- File: `src/claudeutils/validation/cli.py`
  Action: Add planstate subcommand
  Location hint: After jobs subcommand (after line 156)

- File: `tests/test_validation_planstate.py`
  Action: Create CLI integration test using CliRunner
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_cli_integration_calls_planstate_validator -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---
