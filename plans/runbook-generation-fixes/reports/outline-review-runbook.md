# Runbook Outline Review: runbook-generation-fixes

**Artifact**: plans/runbook-generation-fixes/runbook-outline.md
**Design**: plans/runbook-generation-fixes/outline.md
**Date**: 2026-02-22
**Mode**: review + fix-all

## Summary

The runbook outline correctly maps all 10 evidence issues to 14 TDD cycles across 4 phases plus 1 inline phase. Phase ordering respects dependency chains. Six issues found (0 critical, 3 major, 3 minor) — all fixed. Primary gaps were under-specified `validate_and_create()` threading, missing post-phase state declarations, and decision language in verification-only cycles.

**Overall Assessment**: Ready

## Requirements Coverage

Requirements source: outline.md (Root Cause Analysis, Key Design Decisions, Evidence Mapping).

| Requirement | Phase | Cycles | Coverage | Notes |
|-------------|-------|--------|----------|-------|
| RC-3/C2: Phase numbering off-by-one | Phase 1 | 1.1, 1.3 | Complete | Header injection fixes root cause |
| RC-3/M1: PHASE_BOUNDARY misnumbered | Phase 1 | 1.4 | Complete | Cascades from C2 |
| RC-3/M2: Unjustified interleaving | Phase 1 | 1.4 | Complete | Correct phase numbers eliminate sort-based interleaving |
| Phase header preservation | Phase 1 | 1.2 | Complete | Guard against re-injection |
| RC-1/C1: Wrong execution models | Phase 2 | 2.1, 2.2, 2.4 | Complete | Phase model parsed from header metadata |
| RC-1/M3: Model header/body contradiction | Phase 2 | 2.2 | Complete | Phase model overrides frontmatter default |
| RC-1/m3: Agent model conflict | Phase 2 | 2.4 | Complete | Agent frontmatter uses detected model |
| D-1: Step-level model overrides phase model | Phase 2 | 2.3 | Complete | Priority chain verification |
| RC-2/C3: Phase 2 content loss | Phase 3 | 3.1, 3.2, 3.3 | Complete | Phase preamble extraction and injection |
| RC-2/M4: Agent embeds Phase 1 only | Phase 3 | 3.2, 3.3 | Complete | Step/cycle files get phase context |
| RC-2/M5: Completion validation lost | Phase 3, 4 | 3.2, 4.1 | Complete | Phase context + orchestrator phase file refs |
| D-5: PHASE_BOUNDARY phase file references | Phase 4 | 4.1 | Complete | Orchestrator can read phase-level constraints |
| Phase-agent model mapping table | Phase 4 | 4.2 | Complete | Correct models from Phase 2 |
| Skill prose: enforce phase header format | Phase 5 | inline | Complete | Preventive — expansion agent guidance |

**Coverage Assessment**: All requirements covered. All 10 evidence issues from pre-execution review are mapped. OUT-of-scope items (m1, m2) correctly excluded from runbook scope (they are hook-batch content issues per design source).

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Percentage | Assessment |
|-------|--------|------------|------------|------------|
| 1 | 4 | Medium | 29% | Balanced |
| 2 | 4 | Medium | 29% | Balanced |
| 3 | 4 | Medium | 29% | Balanced |
| 4 | 2 | Low | 13% | Acceptable — small but justified by separate concern |
| 5 | 3 items (inline) | Low | N/A | Inline — orchestrator executes |

**Balance Assessment**: Well-balanced. Phases 1-3 are equal. Phase 4 is small but has distinct scope (orchestrator plan improvements) that doesn't belong in Phase 2.

### Complexity Distribution

- Low complexity phases: 2 (Phase 4, Phase 5)
- Medium complexity phases: 3 (Phase 1, Phase 2, Phase 3)
- High complexity phases: 0

**Distribution Assessment**: Appropriate. All code changes are parsing and threading — no algorithmic complexity.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **`validate_and_create()` threading under-specified in Cycles 2.2, 3.2, 3.3, 4.1, 4.2**
   - Location: Phase 2 Cycle 2.2, Phase 3 Cycles 3.2/3.3, Phase 4 Cycles 4.1/4.2
   - Problem: GREEN descriptions said "thread through pipeline" or "thread parameter" without specifying the concrete changes to `validate_and_create()`. This function is the central wiring point — Phases 2, 3, and 4 all add parameters and call sites to it. An implementing agent needs to know exactly what to add and where.
   - Fix: Added numbered implementation steps for 2.2 (3 changes), specific `validate_and_create()` call patterns for 3.2/3.3 (extraction + threading), and concrete parameter additions for 4.1/4.2.
   - **Status**: FIXED

2. **Missing post-phase state declarations on Phases 2, 3, and 4**
   - Location: Phase preambles for Phases 2, 3, 4
   - Problem: Phases declared dependencies ("Depends on: Phase 1") but didn't describe the post-phase state they rely on. An implementing agent in Phase 2 needs to know that assembled content now contains `### Phase N:` headers; Phase 4 needs to know that `phase_models` dict exists in `validate_and_create()`.
   - Fix: Added `Post-Phase-N state:` declarations to each dependent phase preamble, specifying the concrete state changes from the prior phase.
   - **Status**: FIXED

3. **Decision language in verification-only cycles (1.3, 1.4, 2.3)**
   - Location: Cycles 1.3, 1.4, 2.3 GREEN descriptions
   - Problem: "May need no additional code changes" and "Verify no additional changes needed" is decision language — the implementing agent must decide whether changes are needed. The design source is clear that these cycles verify upstream fixes work end-to-end.
   - Fix: Changed to "No additional code changes expected" with explicit investigation targets if tests fail. Marked targets as "verification only".
   - **Status**: FIXED

### Minor Issues

1. **Cycle 3.4 vacuous RED assertion**
   - Location: Phase 3 Cycle 3.4
   - Problem: RED said "Assert no crash, step file has empty or absent phase context section." The "no crash" part is vacuous — any non-crashing code passes. The assertion needs to test specific behavior.
   - Fix: Changed to assert two specific behaviors: `extract_phase_preambles()` returns empty string for that phase, AND generated step file does NOT contain `## Phase Context` section.
   - **Status**: FIXED

2. **Phase 5 header missing model annotation**
   - Location: Phase 5 header
   - Problem: Phase 5 header said `(type: inline)` but expansion guidance specified `opus` as the model. All other phase headers include model annotation. Inconsistency.
   - Fix: Added `model: opus` to Phase 5 header: `(type: inline, model: opus)`.
   - **Status**: FIXED

3. **Requirements mapping table missing Notes column**
   - Location: Requirements Mapping section
   - Problem: Table had Requirement, Phase, Cycles columns but no Notes. Design source (outline.md) Evidence Mapping table includes notes explaining each fix. Without notes, the mapping is a cross-reference table but doesn't explain *how* each requirement is addressed.
   - Fix: Added Notes column with concise descriptions of how each requirement is addressed by its mapped cycles.
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table: added Notes column with per-requirement descriptions
- Cycle 1.3: added `Depends on: 1.1`, replaced decision language with definitive statement and investigation target, marked target as "verification only"
- Cycle 1.4: replaced decision language with definitive statement, marked target as "verification only"
- Phase 2 preamble: added post-Phase-1 state declaration
- Cycle 2.2: expanded GREEN with 3 numbered implementation steps for `validate_and_create()` threading
- Cycle 2.3: replaced decision language with explanation of how existing logic satisfies the priority chain, marked as "verification only"
- Phase 3 preamble: added post-Phase-1 state declaration
- Cycle 3.2: added specific `validate_and_create()` extraction and threading pattern
- Cycle 3.3: added specific `validate_and_create()` threading pattern
- Cycle 3.4: replaced vacuous "no crash" assertion with specific behavioral assertions
- Phase 4 preamble: added post-Phase-2 state declaration
- Cycle 4.1: expanded GREEN with concrete parameter addition and call site changes
- Cycle 4.2: expanded GREEN with concrete parameter addition and call site changes
- Phase 5 header: added `model: opus` annotation
- Expansion Guidance: added checkpoint guidance, collapsible candidates, `validate_and_create()` threading notes

## Design Alignment

- **Architecture**: Aligned. All 5 design decisions (D-1 through D-5) map to specific phases with correct implementation approach.
- **Module structure**: Aligned. Single target file (`prepare-runbook.py`) with new functions (`extract_phase_models`, `extract_phase_preambles`) and modifications to existing functions (`assemble_phase_files`, `generate_step_file`, `generate_cycle_file`, `generate_default_orchestrator`, `validate_and_create`).
- **Key decisions**: D-1 → Phase 2 (model priority chain), D-2 → Phase 3 (phase context injection), D-3 → Phase 1 (header injection), D-4 → no phase (don't-change decision), D-5 → Phase 4 (orchestrator plan references).
- **Scope boundaries**: IN/OUT scope from design source correctly reflected. OUT items (m1, m2, phase expansion quality, per-phase agents, validate-runbook.py, orchestrate skill) excluded.

## Positive Observations

- Root cause to fix phase mapping is clean — each RC maps to exactly one phase (RC-3 → Phase 1, RC-1 → Phase 2, RC-2 → Phase 3)
- Verification-only cycles (1.3, 1.4, 2.3) are a strength — they confirm that upstream fixes propagate correctly without adding unnecessary code
- Single test module strategy avoids fixture duplication across phases
- Cross-phase dependency diagram is accurate and matches phase ordering
- Phase 5 inline type is correct — skill prose edits by the orchestrator, no TDD needed

## Recommendations

Transmitted to outline via Expansion Guidance section:
- Checkpoint guidance for Phase 1 and Phase 2 boundaries
- Collapsible candidate identification for verification-only cycles
- `validate_and_create()` cumulative threading note for expansion awareness

---

**Ready for full expansion**: Yes
