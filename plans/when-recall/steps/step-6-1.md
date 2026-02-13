# Cycle 6.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.1: Replace em-dash parsing with `/when` format parsing

**Prerequisite:** Read `src/claudeutils/validation/memory_index.py:35-60` and `src/claudeutils/validation/memory_index_helpers.py:1-50` — understand `extract_index_entries()` current parsing

**RED Phase:**

**Test:** `test_validator_parses_when_format`
**Assertions:**
- `extract_index_entries(index_with_when_format, root)` returns entries keyed by trigger text
- Entry `/when writing mock tests | mock patch` → key `"writing mock tests"`, section from H2
- Old em-dash format `Key — description` → not parsed (returns empty for that line)
- Entry count matches number of `/when` and `/how` lines

**Expected failure:** AssertionError — validator still parsing em-dash format, not `/when` format

**Why it fails:** `extract_index_entries` still uses em-dash parsing logic

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_validator_parses_when_format -v`

**GREEN Phase:**

**Implementation:** Update entry extraction to use `/when` format.

**Behavior:**
- Detect lines starting with `/when ` or `/how `
- Import and reuse `WhenEntry` model from `claudeutils.when.index_parser` for format consistency
- Key by trigger text (lowercase) instead of key text
- Preserve section tracking from H2 headings

**Approach:** Replace em-dash split logic with `/when`/`/how` prefix detection and pipe splitting. Reuse WhenEntry format spec.

**Changes:**
- File: `src/claudeutils/validation/memory_index.py`
  Action: Update `extract_index_entries()` to parse `/when` format
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Update parallel extraction function if one exists there

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_validator_parses_when_format -v`
**Verify no regression:** `pytest tests/ -q`

---
