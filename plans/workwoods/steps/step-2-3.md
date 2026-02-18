# Cycle 2.3

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.3: Mtime comparison (stale = source_mtime > report_mtime)

**RED Phase:**

**Test:** `test_mtime_comparison_staleness`
**Assertions:**
- VetChain.stale == False when report_mtime > source_mtime (fresh)
- VetChain.stale == True when source_mtime > report_mtime (stale)
- VetChain.source_mtime matches expected mtime from test setup
- VetChain.report_mtime matches expected mtime from test setup

**Expected failure:** stale field always False or not computed correctly

**Why it fails:** Mtime comparison logic not implemented

**Verify RED:** `pytest tests/test_planstate_vet.py::test_mtime_comparison_staleness -v`

**GREEN Phase:**

**Implementation:** Use Path.stat().st_mtime to get filesystem mtimes and compare

**Behavior:**
- Get source_mtime via `source_path.stat().st_mtime`
- Get report_mtime via `report_path.stat().st_mtime` (if report exists)
- Compute stale as `source_mtime > report_mtime`
- Store both mtimes in VetChain

**Approach:** Path.stat() returns stat_result with st_mtime attribute (float, Unix timestamp)

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add mtime extraction and comparison in VetChain creation
  Location hint: When constructing VetChain objects in get_vet_status()

- File: `tests/test_planstate_vet.py`
  Action: Create test using os.utime() to set known mtimes (source newer and source older)
  Location hint: New test function, set mtimes explicitly before calling get_vet_status()

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_mtime_comparison_staleness -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---
