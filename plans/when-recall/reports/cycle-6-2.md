# Cycle 6.2: Format Validation (Operator Prefix, Trigger Non-empty, Extras)

**Date:** 2026-02-13
**Status:** GREEN_VERIFIED
**Execution Model:** Haiku

---

## RED Phase

**Test:** `test_format_validation_rules`

**RED Result:** FAIL as expected

The test failed because the validation code was still checking em-dash format and word count, not the new `/when`/`/how` format with trigger validation.

**Failure message:** AssertionError on assertions checking for invalid operator, empty trigger, and missing operator prefix errors.

---

## GREEN Phase

**Implementation:** Replaced `check_em_dash_and_word_count()` with `check_trigger_format()`

**Changes:**
1. **File:** `src/claudeutils/validation/memory_index_checks.py`
   - Replaced `check_em_dash_and_word_count()` with new `check_trigger_format()`
   - New function checks:
     - Operator prefix (`/when` or `/how` required)
     - Trigger non-empty after stripping
     - Extras format (comma-separated, validated elsewhere)
   - Skips entries in EXEMPT_SECTIONS (preserved as-is)

2. **File:** `src/claudeutils/validation/memory_index.py`
   - Updated import to use `check_trigger_format` from memory_index_checks
   - Moved `check_entry_sorting` import from memory_index_helpers to memory_index_checks
   - Removed duplicate `check_entry_sorting` definition from memory_index_helpers

3. **File:** `src/claudeutils/validation/memory_index_helpers.py`
   - Updated `_build_file_entries_map()` to use new format key extraction logic
   - Supports `/when`/`/how` format alongside old em-dash format

**Test Results:**
- `test_format_validation_rules` — PASS
- All validation tests (19/19) — PASS
- Full test suite (778/794) — PASS, 16 skipped

**Regression Check:** No regressions introduced. Updated all validation test fixtures to use new format.

---

## Refactor Phase

**Linting:** PASS after formatting
- Fixed line-length issues in check_trigger_format()
- Fixed docstring formatting in test file

**Precommit Validation:** WARNINGS ONLY

The precommit validator reports format errors for entries in the project's actual `agents/memory-index.md` that still use em-dash format. These are expected:
- These entries will be migrated to new format in Step 9 (Index migration)
- The validator correctly enforces new format going forward
- No changes needed now; production migration is out-of-scope for this cycle

**Commit:** WIP commit created at 67336ba

---

## Files Modified

1. `src/claudeutils/validation/memory_index_checks.py` — new format validation
2. `src/claudeutils/validation/memory_index.py` — import updates
3. `src/claudeutils/validation/memory_index_helpers.py` — key extraction logic
4. `tests/test_validation_memory_index.py` — updated fixtures to new format
5. `tests/test_validation_memory_index_autofix.py` — updated fixtures to new format

---

## Design Decisions

**D-9 applied:** Word count validation removed entirely. Triggers are intentionally short (2-5 words); validation quality comes from fuzzy uniqueness, not word count.

**Exempt sections preserved:** Entries in EXEMPT_SECTIONS bypass format validation to allow legacy format in sections like "Behavioral Rules (fragments — already loaded)".

**Format-independent autofix:** Fixed `_build_file_entries_map()` to extract keys correctly from both `/when` and em-dash formats, enabling seamless coexistence during migration period.

---

## Stop Condition

None. Cycle completed successfully.

---

## Next Steps

1. Proceed to Cycle 6.3 if assigned
2. Step 9 includes production migration of memory-index.md to new format
