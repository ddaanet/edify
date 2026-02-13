# Cycle 6.6

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.6: Update autofix for new format

**Prerequisite:** Read `src/claudeutils/validation/memory_index_helpers.py` — understand `autofix_index()` mechanics (placement, ordering, structural entry removal)

**RED Phase:**

**Test:** `test_autofix_new_format`
**Assertions:**
- Entry `/when mock test` in wrong file section → autofix moves to correct section (based on heading location)
- Entries out of file order within section → autofix reorders
- Entry pointing to structural heading (`.` prefix) → autofix removes
- After autofix: re-running validation produces zero errors

**Expected failure:** AssertionError — autofix doesn't handle `/when` format entries

**Why it fails:** Autofix still expects em-dash format for parsing/rewriting

**Verify RED:** `pytest tests/test_validation_memory_index_autofix.py::test_autofix_new_format -v`

**GREEN Phase:**

**Implementation:** Update autofix to handle `/when` format.

**Behavior:**
- Parse entries using `/when` format (reuse parser)
- Section placement: determine correct section from heading location (unchanged logic)
- Ordering: sort entries by heading position in file (unchanged logic)
- Structural removal: detect entries matching structural headings and remove (unchanged logic)
- Output: write `/when` format entries (not em-dash)

**Approach:** Update entry parsing in autofix while preserving placement/ordering/removal mechanics.

**Changes:**
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Update `autofix_index()` entry parsing and output formatting for `/when` format
  Location hint: Entry parsing and reconstruction logic

**Verify GREEN:** `pytest tests/test_validation_memory_index_autofix.py::test_autofix_new_format -v`
**Verify no regression:** `pytest tests/ -q`

---
