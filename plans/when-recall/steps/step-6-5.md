# Cycle 6.5

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.5: Remove word count check

**RED Phase:**

**Test:** `test_word_count_removed`
**Assertions:**
- `/when a b` (2 words) → passes validation (previously would fail 8-word minimum)
- `/when very long trigger with many many many words in it` (11 words) → passes (no upper limit)
- `check_em_dash_and_word_count` function no longer called in validation pipeline
- No word count errors in validation output for valid `/when` entries

**Expected failure:** AssertionError — word count check still rejecting short triggers

**Why it fails:** Old word count validation still active

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_word_count_removed -v`

**GREEN Phase:**

**Implementation:** Remove word count validation.

**Behavior:**
- Remove `check_em_dash_and_word_count` from validation pipeline
- No word count constraint on triggers (D-9: triggers are intentionally short)
- Function may remain for backward compatibility but must not be called

**Approach:** Remove call from main validation flow. Delete function if no other callers.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Remove or deprecate `check_em_dash_and_word_count`
- File: `src/claudeutils/validation/memory_index.py`
  Action: Remove call to word count check in validation flow

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_word_count_removed -v`
**Verify no regression:** `pytest tests/ -q`

---
