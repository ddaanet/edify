# Cycle 1.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.4: Validate format (operator prefix, pipe separator)

**RED Phase:**

**Test:** `test_format_validation`
**Assertions:**
- `/when` alone (no trigger text) → skipped with warning logged
- `/when | extras` (empty trigger) → skipped with warning logged
- `/when   | extras` (whitespace-only trigger) → skipped with warning logged
- `/when valid trigger | ,,,` (all-empty extras) → accepted, extras `[]`
- parse_index returns only valid entries (malformed ones excluded from list)

**Expected failure:** AssertionError — empty triggers accepted or malformed entries included

**Why it fails:** Format validation not yet enforcing trigger non-empty requirement

**Verify RED:** `pytest tests/test_when_index_parser.py::test_format_validation -v`

**GREEN Phase:**

**Implementation:** Add format validation rules.

**Behavior:**
- Trigger must be non-empty after stripping
- Empty trigger → skip entry, log warning with line number
- Extra triggers: empty segments after splitting silently dropped (not a warning)
- Return only entries passing validation

**Approach:** Validation checks after parsing, before appending to entry list. Use `logging.warning()` for skipped entries.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Add trigger non-empty validation, log warnings for malformed entries
  Location hint: After trigger extraction, before WhenEntry construction

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_format_validation -v`
**Verify no regression:** `pytest tests/ -q`

---
