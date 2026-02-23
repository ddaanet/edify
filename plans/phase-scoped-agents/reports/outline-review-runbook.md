# Runbook Outline Review: phase-scoped-agents

**Artifact**: plans/phase-scoped-agents/runbook-outline.md
**Design**: plans/phase-scoped-agents/outline.md
**Date**: 2026-02-23
**Mode**: review + fix-all

## Summary

The runbook outline is well-structured with clear TDD cycles, proper phase typing, and logical foundation-first ordering. Eight issues found: one major (misplaced cross-file reference in Phase 3), seven minor (inaccurate helper counts, missing dependency declarations, FR-3 mapping gap, implicit RED not noted, Expansion Guidance placement). All fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles | Coverage | Notes |
|-------------|-------|--------|----------|-------|
| FR-1: Per-phase agents with phase-scoped context | 1 | 1.1-1.4 | Complete | Naming, baseline selection, composition, type detection |
| FR-2: Same base type, injected context differentiator | 1 | 1.2, 1.3 | Complete | 1.2 selects baseline per type; 1.3 composes with injected context |
| FR-3: Orchestrate-evolution dispatch compatibility | 2, 3 | 2.1-2.3, Phase 3 | Complete | Mapping table populated, Agent: field per step, skill reads field |

**Coverage Assessment**: All requirements covered. FR-3 mapping corrected to include Phase 3 inline work.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Assessment |
|-------|--------|------------|------------|
| 1 | 4 | Medium | Balanced — all new functions, unit-level |
| 2 | 5 | High | Largest phase but justified — integration + regression |
| 3 | inline | Low | 3 line edits in one skill file |

**Balance Assessment**: Well-balanced. Phase 2 is largest (5 cycles, ~56% of work) but includes both integration testing and regression updates which are logically coupled. Splitting would create cross-phase dependencies without benefit.

### Complexity Distribution

- **Low complexity cycles**: 1.1, 1.2, 2.4, 2.5 (4 cycles)
- **Medium complexity cycles**: 1.4, 2.1, 2.2 (3 cycles)
- **High complexity cycles**: 1.3, 2.3 (2 cycles)

**Distribution Assessment**: Appropriate. High-complexity cycles (1.3 composition, 2.3 integration) are correctly placed after their dependencies.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Phase 3 contained misplaced prepare-runbook.py reference**
   - Location: Phase 3, third bullet
   - Problem: "Line 1014 of `generate_default_orchestrator()`" is a prepare-runbook.py reference, not an orchestrate skill edit. Line 1014 is the header text in `prepare-runbook.py` which is already updated in Cycle 2.1. This verification belongs to Phase 2, not Phase 3.
   - Fix: Removed the misplaced bullet from Phase 3. The header text update is already specified in Cycle 2.1 GREEN description.
   - **Status**: FIXED

### Minor Issues

1. **Inaccurate `_run_validate` count in Expansion Guidance**
   - Location: Expansion Guidance section, line 28
   - Problem: Claimed "`_run_validate()` in 4 test files" but only 2 files have this helper (`test_prepare_runbook_mixed.py`, `test_prepare_runbook_orchestrator.py`). The other 2 files (`test_prepare_runbook_inline.py`, `test_prepare_runbook_phase_context.py`) call `validate_and_create()` directly.
   - Fix: Corrected to specify which files have the helper and which call directly.
   - **Status**: FIXED

2. **Cycle 2.5 repeated the inaccurate count**
   - Location: Cycle 2.5 GREEN description
   - Problem: "Update `_run_validate()` helpers in all 4 test files" — same factual error as above.
   - Fix: Split into two update groups: `_run_validate` helpers (2 files) and direct `validate_and_create` calls (2 files).
   - **Status**: FIXED

3. **Missing dependency declaration on Cycle 1.4**
   - Location: Cycle 1.4
   - Problem: `detect_phase_types()` classifies phases using the same content pattern as `get_phase_baseline_type()` from Cycle 1.2, but no dependency was declared.
   - Fix: Added `Depends on: 1.2 (reuses phase classification logic)` and updated GREEN to specify delegation to `get_phase_baseline_type()`.
   - **Status**: FIXED

4. **Missing dependency declarations on Cycles 2.2 and 2.4**
   - Location: Cycles 2.2 and 2.4
   - Problem: 2.2 needs phase type info from 1.4 for mapping table rows. 2.4 depends on 2.3's implementation to test the inline-skip path.
   - Fix: Added `Depends on: 1.4` to 2.2 and `Depends on: 2.3` to 2.4.
   - **Status**: FIXED

5. **FR-3 mapping incomplete**
   - Location: Requirements Mapping table
   - Problem: FR-3 mapped only to Phase 2 (2.1-2.3), but Phase 3 (orchestrate skill reading Agent: field) is also part of dispatch compatibility. The original had a separate non-FR row instead.
   - Fix: Merged into FR-3 row: `2, 3 | 2.1-2.3, Phase 3 inline`.
   - **Status**: FIXED

6. **Cycle 2.5 REGRESSION implicit RED not documented**
   - Location: Cycle 2.5
   - Problem: Marked `[REGRESSION]` with only GREEN, but TDD protocol expects RED. The RED is implicit (existing tests break after 2.3 API change) but this wasn't stated.
   - Fix: Added note: "RED is implicit: existing tests fail after 2.3 changes the `validate_and_create` signature."
   - **Status**: FIXED

7. **Expansion Guidance placed before phases**
   - Location: Between Key Decisions and Phase 1
   - Problem: Expansion Guidance should be appended at the end of the outline per review protocol, not interleaved before the phase structure.
   - Fix: Moved to end of file and enhanced with review-driven recommendations.
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping: merged FR-3 + orchestrate skill row into single FR-3 row spanning Phases 2 and 3
- Cycle 1.4: added `Depends on: 1.2`, updated GREEN to delegate to `get_phase_baseline_type()`
- Cycle 2.2: added `Depends on: 1.4`
- Cycle 2.4: added `Depends on: 2.3`, clarified GREEN as verify-then-add
- Cycle 2.5: added `Depends on: 2.3`, documented implicit RED, split file list by update mechanism
- Phase 3: removed misplaced `generate_default_orchestrator()` line 1014 reference
- Expansion Guidance: moved from mid-file to end, enhanced with test placement, API migration, consolidation candidates, cycle expansion notes, checkpoint guidance, and design references

## Design Alignment

- **Architecture**: Aligned. Outline follows the 5-layer composition model from design Key Decision 3.
- **Module structure**: Aligned. New functions (`get_phase_baseline_type`, `detect_phase_types`, `generate_phase_agent`) are placed in `prepare-runbook.py` as specified. No unnecessary module splits.
- **Key decisions**: All 8 design decisions reflected. Naming convention (D-1), baseline per type (D-2), context layering (D-3), common context (D-4), phase context source (D-5), orchestrator format (D-6), backward compatibility (D-7), orchestrate-evolution compatibility (D-8).
- **Scope boundaries**: Outline stays within design IN scope. No scope creep into orchestrate-evolution territory (D-2, D-3, D-5 out of scope).

## Vacuity Analysis

All cycles produce behavioral outcomes:

- **1.1**: Tests naming branch point (multi-phase vs single-phase)
- **1.2**: Tests content classification branch (Cycle headers vs Step headers)
- **1.3**: Tests composition ordering (5 layers in correct sequence)
- **1.4**: Tests per-phase classification across a mixed runbook (3-way branch: tdd/general/inline)
- **2.1**: Tests Agent: field emission in orchestrator output
- **2.2**: Tests mapping table generation with all phase types
- **2.3**: Integration test through full pipeline (6 distinct assertions)
- **2.4**: Tests negative case (inline phase skipped) — legitimate edge case test
- **2.5**: Regression updates — implicit RED from API breakage

No vacuous cycles detected.

## Intra-Phase Ordering

- Phase 1: naming (1.1) → baseline selection (1.2) → composition using both (1.3) → type detection reusing 1.2 (1.4). Foundation-first ordering correct.
- Phase 2: orchestrator field (2.1) → mapping table (2.2) → integration combining all (2.3) → edge case (2.4) → regression (2.5). Foundation-first ordering correct. 2.1 and 2.2 are independent and could be parallel, but sequential is fine for a 2-cycle span.

## Positive Observations

- Clean separation: Phase 1 (pure functions, unit tests) vs Phase 2 (integration, regressions) vs Phase 3 (prose edit)
- Cycle 2.3 RED specifies 6 distinct assertions covering all requirement facets — thorough integration coverage
- Affected files sections per phase aid expansion agents in scoping reads
- Cycle 2.4 correctly tests the negative case (inline produces no agent) as a separate cycle
- REGRESSION tag on Cycle 2.5 correctly signals non-standard RED semantics

## Recommendations

- Cycles 2.1 and 2.2 both modify `generate_default_orchestrator()` — if individual complexity is low during expansion, consider merging
- Cycle 2.3 is the densest cycle (6 assertions, multiple function modifications). Monitor size during expansion; split if GREEN exceeds comfortable single-cycle scope
- Phase boundary checkpoint between 1 and 2: run unit tests for all 4 new functions before starting integration

---

**Ready for full expansion**: Yes
