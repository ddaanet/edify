# Vet Review: Phase 4 Checkpoint — red-plausibility subcommand

**Scope**: `check_red_plausibility`, `write_report` AMBIGUOUS support, `cmd_red_plausibility`, 3 new tests, 2 new fixtures
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix

## Summary

Phase 4 implements the `red-plausibility` subcommand: cycles are processed in order, `created_names` accumulates after each cycle's RED check (D-7 correct), RED `**Expected failure:**` lines are parsed for ImportError/ModuleNotFoundError on already-created modules (exit 1), non-import errors when created names exist are classified AMBIGUOUS (exit 2), plausible REDs pass (exit 0). The `write_report` function correctly inserts the `Ambiguous:` summary line only for red-plausibility. The ambiguous detection condition (`"." not in name or name in failure_text`) is correct for the fixture format: since `failure_text` only captures content inside backticks (e.g., `"ValueError"`), created module names won't appear there, so the `"." not in name` arm (stems) does the work of triggering on first created stem. No issues requiring fixes found.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-5: RED expects ImportError on prior-GREEN module → exit 1 | Satisfied | `test_red_plausibility_violation`: VIOLATION_RED_IMPLAUSIBLE, exit 1, "Ambiguous: 0" in report |
| FR-5: Non-import error when created name exists → exit 2 | Satisfied | `test_red_plausibility_ambiguous`: AMBIGUOUS_RED_PLAUSIBILITY, exit 2, "## Ambiguous" in report |
| FR-5: No conflicts → exit 0 | Satisfied | `test_red_plausibility_happy_path`: VALID_TDD, exit 0, "Ambiguous: 0" in report |
| D-7: created_names tracks only cycles 1..N-1 | Satisfied | `validate-runbook.py:275-283` — accumulation block follows RED check within same loop iteration |
| Exit codes: 0=pass, 1=violations, 2=ambiguous | Satisfied | `cmd_red_plausibility:298-303` |

---

## Positive Observations

- D-7 ordering correct: `created_names` populated after the RED check for each cycle iteration; current cycle's own GREEN is invisible to that cycle's RED check.
- `write_report` cleanly separates AMBIGUOUS from PASS/FAIL using `ambiguous is not None` guard — callers that don't pass `ambiguous` get no Ambiguous line; red-plausibility always passes it.
- VIOLATION_RED_IMPLAUSIBLE fixture demonstrates the violation path precisely: Cycle 1.1 creates `src/widget.py`, Cycle 1.2 RED expects `ImportError on 'widget' not importable`. Both the stem (`widget`) and dotted path (`src.widget`) are added to `created_names`; the stem match in `created_names.get(stem)` fires.
- Violation message format includes both the failure text and the creating cycle ID, satisfying test assertions `"1.1" in content` and `"1.2" in content`.
- `setdefault` used for `created_names` accumulation — prevents overwriting when both stem and dotted path map to the same cycle.
- Tests assert `"Ambiguous: 0"` in violation report and `"Failed: 0"` in ambiguous report — covers mixed-state report content correctness.
- `just dev` passes: 989/990 tests (1 xfail pre-existing, unrelated to Phase 4).
