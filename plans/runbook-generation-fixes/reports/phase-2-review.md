# Runbook Review: Phase 2 — Model Propagation

**Artifact**: `plans/runbook-generation-fixes/runbook-phase-2.md`
**Date**: 2026-02-22T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (5 cycles)

## Summary

Phase 2 implements D-1 (model priority chain) across 5 cycles covering extraction, propagation, step-level override, frontmatter correction, and error-on-missing-model. The structure and file references are sound. Three issues found: Cycle 2.3 had a self-contradictory RED phase (explicitly stated the test "actually passes" before implementation), Cycle 2.5 had disjunctive assertions (OR logic), and Cycle 2.4's GREEN behavior used ambiguous algorithm language ("first phase or most common"). All fixed.

**Overall Assessment**: Ready

---

## Findings

### Critical Issues

1. **Cycle 2.3 RED phase contradicts TDD discipline**
   - Location: Cycle 2.3, `**Expected failure**` section
   - Problem: The expected failure text stated "this actually passes" with pre-2.2 code, and "the RED failure depends on 2.2's implementation quality." A RED phase that explicitly may not fail violates RED/GREEN sequencing. An executor following this would not know when to run RED or what failure to expect.
   - Fix: Replaced with `[REGRESSION]` framing. Test is correctly labeled as a regression guard written before 2.2 is implemented. Expected failure now specifies the concrete regression case (`AssertionError: 'sonnet' != 'opus'`) and execution note clarifies when to run the verification (after 2.2 GREEN, not before implementation).
   - **Status**: FIXED

### Major Issues

1. **Cycle 2.5 disjunctive assertions (OR logic)**
   - Location: Cycle 2.5, `**Assertions**` section
   - Problem: "returns `False` (error condition) OR the pipeline produces a stderr error message" — two different acceptable behaviors. An executor could write a test asserting only the return value while the error message was missing, or vice versa. The OR logic means both branches are valid independently, making the test under-specified.
   - Fix: Changed to conjunctive assertions: `validate_and_create()` returns `False` AND stderr contains "model" AND no step files written. Added concrete stderr example ("ERROR: No model specified for step 1.1"). All three must hold together.
   - **Status**: FIXED

2. **Cycle 2.4 GREEN behavior ambiguous algorithm**
   - Location: Cycle 2.4, `**Behavior**` section, line "Use first phase's model (or most common)"
   - Problem: Two different algorithms in the same sentence — "first" picks the lowest-numbered phase from the dict; "most common" requires counting and produces different results when phases use different models. An executor could implement either.
   - Fix: Replaced with "Use first phase's model (lowest phase number)." This is unambiguous and consistent with D-1's intent (phase header format uses sequential numbering; the primary phase model drives the frontmatter).
   - **Status**: FIXED

### Minor Issues

None identified beyond the above.

---

## Fixes Applied

- Cycle 2.3: Replaced contradictory expected failure text with `[REGRESSION]` label and concrete regression failure specification; updated verification instruction from "Verify RED" to "Verify after 2.2 GREEN"
- Cycle 2.5: Replaced disjunctive OR assertion with three conjunctive assertions (returns False + stderr contains "model" + no step files written); added concrete stderr example
- Cycle 2.4: Replaced ambiguous "first phase's model (or most common)" with "first phase's model (lowest phase number)"

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
