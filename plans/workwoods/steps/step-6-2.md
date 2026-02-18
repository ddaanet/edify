# Cycle 6.2

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

### Cycle 6.2: Validator checks artifact consistency (steps/ without runbook-phase-*.md)

**RED Phase:**

**Test:** `test_validator_checks_artifact_consistency`
**Assertions:**
- Plan with steps/ directory but no runbook-phase-*.md files returns error
- Error message: "Plan '<name>' has steps/ without runbook-phase-*.md files"
- Plan with orchestrator-plan.md but no steps/ returns error
- Consistent artifacts (all present) pass validation

**Expected failure:** No consistency checking, only artifact presence validated

**Why it fails:** Consistency logic not implemented

**Verify RED:** `pytest tests/test_validation_planstate.py::test_validator_checks_artifact_consistency -v`

**GREEN Phase:**

**Implementation:** Add consistency checks for ready status artifacts

**Behavior:**
- If steps/ exists: verify runbook-phase-*.md files exist (at least one)
- If orchestrator-plan.md exists: verify steps/ exists
- Both conditions must hold for ready status
- Return error for inconsistent state

**Approach:** Explicit checks after artifact detection

**Changes:**
- File: `src/claudeutils/validation/planstate.py`
  Action: Add consistency checking in validate() function
  Location hint: After artifact presence check

- File: `tests/test_validation_planstate.py`
  Action: Create tests with inconsistent artifact combinations
  Location hint: New test functions for each inconsistency type

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_validator_checks_artifact_consistency -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---
