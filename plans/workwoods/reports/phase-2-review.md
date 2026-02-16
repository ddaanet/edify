# Runbook Review: Phase 2 - Vet Staleness Detection

**Artifact**: plans/workwoods/runbook-phase-2.md
**Date**: 2026-02-16T18:30:00Z
**Mode**: review + fix-all
**Phase types**: TDD

## Summary

Phase 2 runbook reviewed for TDD discipline, step quality, and LLM failure modes. Phase implements vet staleness detection via mtime comparison using established naming conventions.

**Total items:** 5 cycles
**Issues found:** 1 minor
**Issues fixed:** 1
**Unfixable (escalation required):** 0

**Overall Assessment:** Ready

Phase demonstrates strong TDD discipline with clear RED/GREEN sequencing, behavioral test descriptions, and no prescriptive code in GREEN phases. All cycles test meaningful behavior with specific assertions. Foundation-first ordering maintained throughout.

## Critical Issues

None found.

## Major Issues

None found.

## Minor Issues

### Issue 1: Missing Weak Orchestrator Metadata

**Location:** Phase header (lines 1-15)
**Problem:** Phase lacks standard "Weak Orchestrator Metadata" section required for execution routing. Orchestrator needs model tier, cycle count, and restart flag.
**Fix:** Added metadata section after Estimated Complexity field:
```markdown
**Weak Orchestrator Metadata:**
- Model: sonnet
- Total Cycles: 5
- Restart required: No
```
**Status:** FIXED

## TDD Quality Assessment

### GREEN Phase Code Review
All 5 GREEN phases reviewed for prescriptive implementation code.

**Result:** ✓ Clean — No code blocks found in GREEN phases. All GREEN phases use behavior descriptions with hints, not exact code.

**Examples of correct patterns:**
- Cycle 2.1: "Create vet.py with get_vet_status() that scans source artifacts and maps to report paths" — describes behavior, not implementation
- Cycle 2.3: "Use Path.stat().st_mtime to get filesystem mtimes and compare" — provides approach hint, not code
- Cycle 2.5: "Regex to extract numbers, sort by (number, mtime) tuple" — suggests technique, not prescription

### RED Phase Test Quality
All 5 RED phases reviewed for prose test quality and behavioral specificity.

**Result:** ✓ Strong — All RED phases use prose test descriptions with specific assertions. No full test code in RED phases.

**Assertion quality examples:**
- Cycle 2.1: Parametrized assertions for 4 specific naming conventions (outline.md → outline-review.md, etc.)
- Cycle 2.3: Specific comparisons: "stale == False when report_mtime > source_mtime", "stale == True when source_mtime > report_mtime"
- Cycle 2.4: Exact None handling: "report == None", "report_mtime == None", "stale == True"
- Cycle 2.5: Highest-wins logic with fallback: "Use highest number" then "use highest mtime"

All assertions are behaviorally specific — an executor could not write different tests that all satisfy these descriptions.

### RED/GREEN Sequencing
Verified RED can fail before GREEN implementation for all cycles.

**Result:** ✓ Valid sequencing

- Cycle 2.1: ImportError/NameError (module doesn't exist)
- Cycle 2.2: Only primary pattern works (fallback not implemented)
- Cycle 2.3: stale field always False or not computed
- Cycle 2.4: Exception or wrong stale value (missing report case not handled)
- Cycle 2.5: Uses first or alphabetically first (no number extraction)

Each RED phase will genuinely fail, requiring GREEN implementation to pass.

## LLM Failure Mode Analysis

### 11.1 Vacuity
**Check:** Cycles testing only structure/imports vs meaningful behavior

**Result:** ✓ No vacuity detected

All 5 cycles test concrete behavior:
- 2.1: Source→report mapping detection (4 naming conventions)
- 2.2: Fallback glob with mtime selection (naming variance handling)
- 2.3: Mtime extraction and staleness comparison
- 2.4: Missing report edge case (None propagation)
- 2.5: Iterative review selection (number extraction + mtime fallback)

No scaffolding-only cycles. Each cycle delivers testable functional outcome.

### 11.2 Dependency Ordering
**Check:** Foundation-first within phase

**Result:** ✓ Correct ordering

Progression:
1. Cycle 2.1: Basic mapping (existence)
2. Cycle 2.2: Fallback glob (structure extension)
3. Cycle 2.3: Mtime comparison (core behavior)
4. Cycle 2.4: Edge case handling (refinement)
5. Cycle 2.5: Multi-match resolution (refinement)

No forward references. Each cycle builds on prior cycles' foundations.

### 11.3 Density
**Check:** Adjacent cycles with <1 branch point difference

**Result:** ✓ Appropriate granularity

Cycle boundaries justified:
- 2.1→2.2: Direct mapping vs glob-based fallback (different code paths)
- 2.2→2.3: Report existence vs staleness computation (distinct concerns)
- 2.3→2.4: Normal case vs missing report edge case (separate validation)
- 2.4→2.5: Single match vs multi-match resolution (different algorithms)

No over-granular decomposition detected.

### 11.4 Checkpoint Spacing
**Check:** Gaps >10 items or >2 phases without checkpoint

**Result:** ✓ Adequate spacing

Checkpoint appears after Cycle 2.5 (5 cycles total). Well within acceptable range.

### 11.5 File Growth
**Check:** Projected LOC vs 400-line threshold

**Result:** ✓ No growth concerns

New module with narrow scope (vet staleness detection). Expected file size <200 LOC based on:
- Single core function (get_vet_status)
- Mapping table (static data)
- Glob logic + mtime comparison
- No complex algorithms or state management

No file split needed.

## File Reference Validation

All referenced files checked for existence:

**Non-existent (expected — to be created):**
- `src/claudeutils/planstate/vet.py` — module to be created in Cycle 2.1
- `src/claudeutils/planstate/models.py` — may exist from Phase 1, will be extended if needed
- `tests/test_planstate_vet.py` — test file to be created in Cycle 2.1

**Design reference:**
- `plans/workwoods/design.md` — exists ✓

**Result:** ✓ All file references valid for Phase 2 execution context

## Consolidation Quality

**Check:** Trivial work placement and phase preamble usage

**Result:** ✓ Appropriate structure

- No phase preamble content (all work in cycles)
- No trivial items left isolated
- No testable behavior hidden outside cycles
- No forced grouping of unrelated domains

Phase is correctly focused on single responsibility (vet staleness detection).

## Fixes Applied

1. Added Weak Orchestrator Metadata section (lines 15-18) — model tier (sonnet), cycle count (5), restart flag (No)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes

Phase 2 runbook demonstrates strong TDD discipline and is ready for execution. All RED phases have specific behavioral assertions, all GREEN phases provide guidance without prescriptive code, and dependency ordering is foundation-first throughout. No LLM failure modes detected.
