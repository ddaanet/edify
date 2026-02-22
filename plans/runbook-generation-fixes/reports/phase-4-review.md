# Runbook Review: Phase 4 — Orchestrator plan improvements

**Artifact**: `plans/runbook-generation-fixes/runbook-phase-4.md`
**Date**: 2026-02-22T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (2 cycles)

## Summary

Phase 4 is well-structured with specific behavioral RED assertions, no prescriptive code in GREEN phases, and sound dependency ordering (4.1 adds phase file path infrastructure, 4.2 extends with model table). One minor assertion specificity issue in Cycle 4.2 RED (format left ambiguous as "table or list") was fixed to match the GREEN phase's prescribed `- Phase N: model_name` format.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Ambiguous format specification in Cycle 4.2 RED assertions**
   - Location: Cycle 4.2, RED Phase Assertions
   - Problem: "Table or list maps Phase 1 → sonnet..." leaves the expected output format unspecified. The GREEN phase prescribes `- Phase N: model_name` per line, but the RED assertion doesn't reflect this — an executor could write assertions checking any format.
   - Fix: Replaced "Table or list maps Phase 1 → sonnet, Phase 2 → opus, Phase 3 → haiku" with specific expected strings: `- Phase 1: sonnet`, `- Phase 2: opus`, `- Phase 3: haiku`
   - **Status**: FIXED

## Fixes Applied

- Cycle 4.2, RED Phase Assertions — tightened "Table or list" to exact `- Phase N: model_name` format strings matching GREEN phase specification

## Validation Notes

- File references: `agent-core/bin/prepare-runbook.py` (exists), `tests/test_prepare_runbook_inline.py` (exists), `tests/test_prepare_runbook_mixed.py` (new — being created by this runbook, not a false reference)
- Line number hints (743, 798-800, 808, 904-908, 955-967) verified accurate against current file
- Function names `generate_default_orchestrator()`, `validate_and_create()`, `assemble_phase_files()` all exist at stated locations
- Metadata: "All 2 cycles" matches actual cycle count (4.1, 4.2) — accurate
- No prescriptive code blocks in GREEN phases
- RED expected failures are specific (AssertionError with stated reason) and would genuinely fail against current implementation
- Cycle ordering is foundation-first: 4.1 adds `phase_dir` parameter chain, 4.2 adds `phase_models`/`default_model` on top — additive and non-conflicting

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
