# Cycle 6.3

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

### Cycle 6.3: Validator warns on plan-archive orphans (referenced plans not deleted)

**RED Phase:**

**Test:** `test_validator_warns_on_archive_orphans`
**Assertions:**
- Plan referenced in plan-archive.md but still in plans/ directory returns warning
- Warning message: "Plan '<name>' archived but directory still exists"
- Plans in archive without directories are valid (expected state)

**Expected failure:** No plan-archive.md checking

**Why it fails:** Archive orphan detection not implemented

**Verify RED:** `pytest tests/test_validation_planstate.py::test_validator_warns_on_archive_orphans -v`

**GREEN Phase:**

**Implementation:** Read plan-archive.md, check for orphan references

**Behavior:**
- Read agents/plan-archive.md (if exists)
- Extract H2 headings as archived plan names
- Check if any archived plan still has directory in plans/
- If found: add warning (not error — may be intentional)

**Approach:** Parse markdown H2 headings, cross-reference with plans/ listing

**Changes:**
- File: `src/claudeutils/validation/planstate.py`
  Action: Add archive orphan checking in validate() function
  Location hint: After consistency checks

- File: `tests/test_validation_planstate.py`
  Action: Create test with plan-archive.md and orphaned directory
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_validator_warns_on_archive_orphans -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---
