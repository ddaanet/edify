# Cycle 6.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.2: Format validation (operator prefix, trigger non-empty, extras)

**RED Phase:**

**Test:** `test_format_validation_rules`
**Assertions:**
- `/when valid trigger` → passes format check
- `/when valid | extra1, extra2` → passes format check
- `/what invalid operator` → flagged as error (invalid operator)
- `/when` (no trigger) → flagged as error (empty trigger)
- `/when trigger | ,,,` → passes (empty extras silently dropped)
- Old em-dash format → flagged as error (no operator prefix)
- Each error includes line number and descriptive message

**Expected failure:** AssertionError — format validation still checking em-dash format

**Why it fails:** `check_em_dash_and_word_count()` still enforcing old rules

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_format_validation_rules -v`

**GREEN Phase:**

**Implementation:** Replace em-dash check with `/when` format validation.

**Behavior:**
- Check operator prefix (`/when` or `/how` required)
- Check trigger non-empty after stripping
- Check extras format (comma-separated, no empty segments — warning only)
- Remove word count check entirely (D-9: obsolete for trigger format)

**Approach:** Replace `check_em_dash_and_word_count()` with `check_trigger_format()`.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Replace `check_em_dash_and_word_count` with trigger format check
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Update parallel check function if one exists

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_format_validation_rules -v`
**Verify no regression:** `pytest tests/ -q`

---
