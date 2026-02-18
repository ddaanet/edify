# Cycle 2.4

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.4: Missing report handling (report_mtime = None → stale = True)

**RED Phase:**

**Test:** `test_missing_report_treated_as_stale`
**Assertions:**
- VetChain.stale == True when report file doesn't exist
- VetChain.report == None when report doesn't exist
- VetChain.report_mtime == None when report doesn't exist
- VetStatus.any_stale == True when any chain has stale=True

**Expected failure:** Exception or wrong stale value when report missing

**Why it fails:** Code assumes report exists, doesn't handle missing case

**Verify RED:** `pytest tests/test_planstate_vet.py::test_missing_report_treated_as_stale -v`

**GREEN Phase:**

**Implementation:** Check if report exists before getting mtime, treat missing as stale

**Behavior:**
- If report path doesn't exist: report=None, report_mtime=None, stale=True
- If report exists: get mtime normally, compare with source
- any_stale computed as: any(chain.stale for chain in chains)

**Approach:** Use Path.exists() before Path.stat()

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add existence check before mtime extraction, handle None case
  Location hint: In VetChain creation, before report_mtime extraction

- File: `src/claudeutils/planstate/models.py`
  Action: Add any_stale: bool convenience field to VetStatus
  Location hint: VetStatus dataclass

- File: `tests/test_planstate_vet.py`
  Action: Create test with source artifact but no report file
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_missing_report_treated_as_stale -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---
