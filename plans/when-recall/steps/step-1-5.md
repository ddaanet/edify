# Cycle 1.5

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.5: Malformed entry handling (skip with warning)

**RED Phase:**

**Test:** `test_malformed_entries_skipped_gracefully`
**Assertions:**
- Index file with mix of valid and malformed entries: parse_index returns only valid entries
- Malformed line `/when` (no space after operator) → skipped
- Line with old format `Key — description` → skipped (no `/when` prefix)
- Completely empty file → returns empty list
- File with only headers (no entries) → returns empty list
- Warning count matches number of malformed entries (use caplog fixture)

**Expected failure:** AssertionError — malformed entries cause crash or are included in results

**Why it fails:** Graceful degradation for edge cases not fully tested

**Verify RED:** `pytest tests/test_when_index_parser.py::test_malformed_entries_skipped_gracefully -v`

**GREEN Phase:**

**Implementation:** Ensure robust error handling across all entry parsing.

**Behavior:**
- Any line that doesn't match `/when ` or `/how ` prefix → silently skip (not an entry)
- Lines matching prefix but failing validation → warning with line number
- File I/O errors → log warning, return empty list (graceful degradation per project convention)
- Never raise exceptions during parsing

**Approach:** Wrap entry parsing in try/except per line. Ensure parse_index never raises.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Add comprehensive error handling, logging for malformed entries
  Location hint: Main parsing loop and file read

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_malformed_entries_skipped_gracefully -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 2: Navigation Module

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 1 (WhenEntry model for sibling computation)
**Files:** `src/claudeutils/when/navigation.py`, `tests/test_when_navigation.py`

**Design reference:** navigation.py module responsibilities, "Structural heading handling"

**Prior state:** Phase 1 provides `WhenEntry` model with operator, trigger, extra_triggers, line_number, section fields.

---
