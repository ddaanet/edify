# Review: Phase 1 Checkpoint — learnings.py validation

**Scope**: `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
**Date**: 2026-02-23
**Mode**: review + fix

## Summary

Phase 1 implements When/How prefix validation and min-2-content-words checks in `validate()`, with full TDD cycle coverage. Implementation is clean and correct. Five existing fixtures were migrated to prefixed titles. All 12 tests pass and precommit is green.

One minor issue found: a redundant variable recalculation for `words` inside the word-count check. One test coverage gap: the `test_multiple_errors_reported` fixture does not exercise a combined word-count + prefix scenario — the max-word-count error fires on "When" titles, which means the fixture tests the right thing, but the second assertion `assert any("title has 8 words" in e for e in errors)` is duplicated verbatim (both lines identical), which tests nothing extra.

**Overall Assessment**: Ready

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Redundant `words` recalculation inside word-count block**
   - Location: `src/claudeutils/validation/learnings.py:79`
   - Note: `words = title.split()` at line 70 and again at line 79. The first assignment is inside the `else` branch (prefix valid). The second assignment at line 79 is unconditional and recalculates `words` even though it was just calculated at line 70 in the `else` branch, and the prefix-error branch also needs it for the word-count check. The logic is correct but the variable is assigned twice when the prefix is valid.
   - Fix: Hoist `words = title.split()` before the prefix check so it is computed once and used in both branches.
   - **Status**: FIXED

2. **Duplicate assertion line in `test_multiple_errors_reported`**
   - Location: `tests/test_validation_learnings.py:283-284`
   - Note: Lines 283 and 284 are identical: `assert any("title has 8 words" in e for e in errors)`. The second line adds no coverage — it asserts the same predicate twice. The intent (presumably) was to assert both word-count errors are present, but the current predicate `any(...)` is satisfied by a single match.
   - Fix: Change the second assertion to verify two word-count errors are present, e.g., `assert sum(1 for e in errors if "title has 8 words" in e) == 2`.
   - **Status**: FIXED

---

## Fixes Applied

- `src/claudeutils/validation/learnings.py:70-80` — Hoisted `words = title.split()` before the prefix check; removed duplicate recalculation inside word-count block. Content-word slice logic updated to use the hoisted variable.
- `tests/test_validation_learnings.py:284` — Replaced duplicate `any(...)` assertion with `sum(...) == 2` to verify both word-count errors are reported.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: When/How prefix check | Satisfied | `learnings.py:63` — `startswith(("When ", "How to "))` |
| FR-2: Min 2 content words after prefix | Satisfied | `learnings.py:71-76` — strips prefix words, checks `len < 2` |
| FR-3: Precommit enforcement | Satisfied | `cli.py:52` — `validate_learnings` called in `_run_all_validators`; `just dev` passes |

---

## Positive Observations

- Prefix check uses `startswith` tuple — avoids a separate `or` condition, idiomatic Python.
- Content-word stripping correctly distinguishes 2-word prefix ("How to", strips `words[2:]`) from 1-word prefix ("When", strips `words[1:]`).
- Test for `test_how_without_to_rejected` specifically validates that "How" alone does not satisfy the prefix — closes the most likely off-by-one in the prefix check.
- `test_combined_errors_reported` exercises two distinct error types from two distinct titles in a single file — good behavioral test.
- Existing preamble-skip logic (first 10 lines) preserved without modification.
- `validate()` returns empty list for missing file — graceful degradation unchanged.
