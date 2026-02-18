# Cycle 6.1

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

### Cycle 6.1: Validator detects missing artifacts (no recognized files)

**Prerequisite:** Read validation/jobs.py (lines 47-79) to understand validator structure and pattern.

**RED Phase:**

**Test:** `test_validator_detects_missing_artifacts`
**Assertions:**
- Plan directory with no recognized artifacts returns error
- Error message: "Plan '<name>' has no recognized artifacts"
- Empty directory treated as no artifacts
- plans/reports/ excluded from validation (not a plan)

**Expected failure:** ImportError (planstate validator doesn't exist)

**Why it fails:** No validation/planstate.py module yet

**Verify RED:** `pytest tests/test_validation_planstate.py::test_validator_detects_missing_artifacts -v`

**GREEN Phase:**

**Implementation:** Create planstate validator with artifact detection

**Behavior:**
- Call list_plans(plans_dir) from planstate module
- For each plan: check if infer_state() returned None (no artifacts)
- If None: add error "Plan '<name>' has no recognized artifacts"
- Return list of error messages

**Approach:** Scan all plans/, check for None results from infer_state()

**Changes:**
- File: `src/claudeutils/validation/planstate.py`
  Action: Create validate(root: Path) -> list[str] function
  Location hint: New file, follow validation/jobs.py structure

- File: `tests/test_validation_planstate.py`
  Action: Create test with tmp_path, empty plan directory
  Location hint: New file

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_validator_detects_missing_artifacts -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---
