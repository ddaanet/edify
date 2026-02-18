# Cycle 2.1

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.1: Source→report mapping for all convention types (parametrized)

**Prerequisite:** Read design Vet Chain Conventions table for standard naming patterns.

**RED Phase:**

**Test:** `test_source_report_mapping_conventions`
**Assertions (parametrized):**
- outline.md → reports/outline-review.md mapping detected
- design.md → reports/design-review.md mapping detected
- runbook-outline.md → reports/runbook-outline-review.md mapping detected
- runbook-phase-1.md → reports/phase-1-review.md mapping detected

**Expected failure:** ImportError or NameError (vet module doesn't exist)

**Why it fails:** No vet.py module or get_vet_status() function

**Verify RED:** `pytest tests/test_planstate_vet.py::test_source_report_mapping_conventions -v`

**GREEN Phase:**

**Implementation:** Create vet.py with get_vet_status() that scans source artifacts and maps to report paths

**Behavior:**
- Scan plan_dir for recognized source artifacts (outline.md, design.md, etc.)
- For each source, derive expected report path via naming convention
- Check if report exists at expected path
- Create VetChain for each source→report pair

**Approach:** Mapping table (dict) from source filename to report filename pattern

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Create module with get_vet_status(plan_dir: Path) -> VetStatus
  Location hint: New file

- File: `src/claudeutils/planstate/models.py`
  Action: Define VetStatus and VetChain dataclasses (if not already in Phase 1)
  Location hint: After PlanState definition

- File: `tests/test_planstate_vet.py`
  Action: Create parametrized test with tmp_path, test all four standard mappings
  Location hint: New file, use @pytest.mark.parametrize

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_source_report_mapping_conventions -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---
