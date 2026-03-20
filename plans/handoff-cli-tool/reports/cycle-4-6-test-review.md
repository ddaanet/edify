# Review: Cycle 4.6 Test Quality (format_diagnostics)

**Scope**: tests/test_session_handoff.py — new tests: test_diagnostics_precommit_pass, test_diagnostics_precommit_fail, test_diagnostics_learnings_age
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

Three tests cover `format_diagnostics` diagnostic output function. Tests are structurally sound and import from correct module path. One gap: the step spec asserts `test_diagnostics_precommit_fail` includes a learnings age warning when `learnings_age_days >= 7`, but the test uses `learnings_age_days=3` (below threshold) — the conditional case where precommit fails AND learnings are stale is untested. Minor signal issue: `test_diagnostics_precommit_pass` uses `learnings_age_days=None` rather than an explicit below-threshold integer to verify no-warning behavior.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Precommit-fail + stale learnings case not covered**
   - Location: tests/test_session_handoff.py:320-330
   - Problem: The step spec asserts "Contains learnings age summary if any ≥ 7 days" under the precommit-failed case. `test_diagnostics_precommit_fail` passes `learnings_age_days=3`, which is below the threshold — it only verifies the no-warning path. The interaction of precommit failure with stale learnings (the case the spec explicitly names) is untested.
   - Suggestion: Add assertion `"Learnings" in result` to a variant that passes `learnings_age_days=8` and `passed=False`, OR update the existing test to use `learnings_age_days=8` and assert the warning appears.
   - **Status**: FIXED

### Minor Issues

1. **`test_diagnostics_precommit_pass` uses `None` for learnings_age_days no-warning case**
   - Location: tests/test_session_handoff.py:307-317
   - Note: `None` means "not computed" (caller didn't check), not "young entries". The no-warning path for computed-but-young learnings (e.g., `learnings_age_days=3`) is a different code branch from `None`. If the implementation distinguishes them, only the `None` path is tested here. Low severity since the step spec doesn't separately enumerate this case, but the distinction is real.
   - **Status**: FIXED

## Fixes Applied

- tests/test_session_handoff.py:320-330 — Updated `test_diagnostics_precommit_fail` to use `learnings_age_days=8` and added assertion that learnings warning appears when precommit failed but age ≥ 7 days, per step spec requirement.
- tests/test_session_handoff.py:307-317 — Added a second `assert "Learnings" not in result` anchor via `learnings_age_days=3` check in `test_diagnostics_precommit_pass` to cover the computed-but-young case alongside the None case.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| format_diagnostics includes precommit output when passed | Satisfied | test_diagnostics_precommit_pass:314 |
| format_diagnostics includes git status/diff when passed | Satisfied | test_diagnostics_precommit_pass:315 |
| No learnings age warning when < 7 days | Partial → Satisfied after fix | None path tested; computed-below-threshold added by fix |
| format_diagnostics includes failure output when failed | Satisfied | test_diagnostics_precommit_fail:327 |
| Git output excluded when precommit failed | Satisfied | test_diagnostics_precommit_fail:329 |
| Learnings age warning when ≥ 7 days AND precommit failed | Missing → Satisfied after fix | Step spec: "Contains learnings age summary if any ≥ 7 days" under failed case |
| Learnings age warning text format includes count and /codify | Satisfied | test_diagnostics_learnings_age:341-343 |

---

## Positive Observations

- Import target (`claudeutils.session.handoff.context.format_diagnostics`, `PrecommitResult`) is specific and consistent with the module structure established in prior phases.
- `test_diagnostics_learnings_age` checks both the numeric value (`"10" in result`) and the action text (`"codify"`) — verifies the warning is informative, not just present.
- `test_diagnostics_precommit_fail` verifies the conditional exclusion of git output (negative assertion on git content when failed), correctly testing the conditional-on-pass behavior from the spec.
- Tests are pure function calls with no I/O setup — fast and isolated.
