# Runbook Outline Review: when-recall

**Artifact**: plans/when-recall/runbook-outline.md
**Design**: plans/when-recall/design.md
**Date**: 2026-02-12T17:05:00Z
**Mode**: review + fix-all

## Summary

Outline quality is strong with clear phase structure and comprehensive requirements coverage. All 11 requirements (7 functional, 4 non-functional) are traced to implementation phases. Phase structure is well-balanced with parallelization opportunities identified. Fixed 9 issues spanning phase numbering corrections, dependency clarifications, and execution-readiness improvements.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 0-5, 8 | Fuzzy→Parser→Nav→Resolver→CLI→Skills | Complete | Corrected phase references (was 1-5, now 0-5, 8) |
| FR-2 | 0 | 0.1-0.8 (fuzzy engine) | Complete | Foundation phase |
| FR-3 | 2 | 2.1-2.6 (navigation) | Complete | Corrected phase ref (was 4, now 2) |
| FR-4 | 6 | 6.1-6.7 (validator update) | Complete | Uses Phase 0 fuzzy |
| FR-5 | 10 | 10.1-10.3 (remember skill) | Complete | Post-migration |
| FR-6 | 9 | 9.1-9.8 (migration) | Complete | ~159 entries, atomic commit |
| FR-7 | 3 | 3.1-3.4 (resolver modes) | Complete | Trigger/.section/..file |
| NFR-1 | 0 | Shared fuzzy.py | Complete | Imported by resolver/validator/compress-key |
| NFR-2 | 0-7, 11 | All TDD phases | Complete | Corrected phase range (was 1-7) |
| NFR-3 | 11 | 11.1-11.3 (recall parser) | Complete | Measurement infrastructure |
| NFR-4 | 9 | 9.6 (consumption header) | Complete | @-loaded preserved |

**Coverage Assessment**: All requirements covered with explicit phase/cycle mappings.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles/Steps | Complexity | Type | Assessment |
|-------|--------------|------------|------|------------|
| 0 | 8 | Medium | TDD | Balanced (foundation) |
| 1 | 5 | Low | TDD | Balanced |
| 2 | 6 | Medium | TDD | Balanced |
| 3 | 9 | High | TDD | Within limits (checkpoint added) |
| 4 | 5 | Low | TDD | Balanced |
| 5 | 2 | Trivial | General | Balanced |
| 6 | 7 | Medium | TDD | Balanced |
| 7 | 4 | Low | TDD | Balanced |
| 8 | 3 | Trivial | General | Balanced |
| 9 | 8 | High | General | Balanced (sonnet model) |
| 10 | 3 | Low | General | Balanced |
| 11 | 3 | Low | TDD | Balanced |

**Balance Assessment**: Well-balanced. No phase exceeds 10 items. Phase 3 (9 cycles) is highest but appropriate for High complexity resolver integration.

### Complexity Distribution

- **Trivial phases**: 2 (Phase 5, 8 — bin script and skills)
- **Low complexity phases**: 4 (Phase 1, 4, 7, 10, 11)
- **Medium complexity phases**: 3 (Phase 0, 2, 6)
- **High complexity phases**: 2 (Phase 3, 9)

**Distribution Assessment**: Appropriate. High-complexity phases (resolver integration, migration) have explicit checkpoints and appropriate model tier (haiku for TDD, sonnet for migration).

## Review Findings

### Critical Issues

**1. Phase numbering inconsistency in requirements mapping**
- Location: Requirements Mapping table
- Problem: Mapping referred to "Phase 1-5" (0-based ignored) and "Phase 4" for navigation (actually Phase 2)
- Fix: Corrected all phase references to match 0-11 numbering (FR-1: 0-5,8; FR-2: Phase 0; FR-3: Phase 2; FR-4: Phase 0 reference)
- **Status**: FIXED

### Major Issues

**2. Navigation dependency unclear**
- Location: Phase 2 dependencies
- Problem: Said "Phase 1 (index parser for sibling computation)" without clarifying that WhenEntry model is the dependency, not file parsing logic
- Fix: Clarified Cycle 2.5 depends on WhenEntry structures from Phase 1, added note that navigation operates on file content strings
- **Status**: FIXED

**3. Missing checkpoint in 9-cycle phase**
- Location: Phase 3 (9 cycles, High complexity)
- Problem: No internal checkpoint guidance for longest TDD phase — risk of drift accumulation
- Fix: Added checkpoint marker after Cycle 3.6 (core resolver logic complete), updated Expansion Guidance section
- **Status**: FIXED

**4. Cycle descriptions lack assertion specificity**
- Location: Phase 3 cycles 3.2-3.9
- Problem: Cycle titles didn't specify test outcomes (e.g., "fuzzy match against index" → what assertion?)
- Fix: Added behavioral outcomes: 3.2 "return matching heading", 3.3 "global unique heading lookup in decision files", 3.5 "heading to next same-level heading", 3.7 "suggest top 3 closest matches via fuzzy"
- **Status**: FIXED

**5. Migration phase lacks validation checkpoint**
- Location: Phase 9 Step 9.5
- Problem: Validator run listed as step but not marked as hard gate before proceeding to documentation updates
- Fix: Added checkpoint marker "validator must pass before proceeding" at Step 9.5
- **Status**: FIXED

**6. Prior state awareness missing**
- Location: Phase 6 and Phase 9
- Problem: No explicit note of what earlier phases established (Phase 6 uses fuzzy engine, Phase 9 uses validator+compress-key)
- Fix: Added "Prior State" sections to Phase 6 (fuzzy engine + WhenEntry model available) and Phase 9 (validator supports new format, compress-key verifies uniqueness)
- **Status**: FIXED

### Minor Issues

**7. Validator cycle descriptions generic**
- Location: Phase 6 cycles 6.2-6.4
- Problem: "Format validation" and "collision detection" didn't specify what constitutes valid/invalid
- Fix: Added specifics: 6.2 "operator prefix required, trigger non-empty, extras comma-separated", 6.3 "each entry fuzzy-expands to exactly one heading", 6.4 "no two triggers resolve to same heading via fuzzy"
- **Status**: FIXED

**8. Migration step scope vague**
- Location: Phase 9 Step 9.2, 9.8
- Problem: Didn't specify which headings get renamed (semantic vs structural) or what "redistribute" means
- Fix: 9.2 "~131 semantic headings, preserve structural `.` headings", 9.8 "create new sections for files without entries"
- **Status**: FIXED

**9. Checkpoint guidance incomplete**
- Location: Expansion Guidance section
- Problem: Listed full checkpoints only, no mid-phase guidance
- Fix: Added mid-phase checkpoint after Cycle 3.6, clarified Phase 9 checkpoint requires validator pass before docs
- **Status**: FIXED

## Fixes Applied

All fixes applied to `plans/when-recall/runbook-outline.md`:

- Requirements Mapping table — corrected phase references (0-5,8 for FR-1, Phase 0 for FR-2/NFR-1, Phase 2 for FR-3, Phases 0-7,11 for NFR-2)
- Phase 2 dependencies — clarified WhenEntry dependency, added note on no resolver dependency
- Phase 2 Cycle 2.5 — explicit note "requires WhenEntry structures from Phase 1"
- Phase 3 cycles 3.2-3.9 — added behavioral outcome descriptions
- Phase 3 Cycle 3.6 — added checkpoint marker
- Phase 3 rationale — added checkpoint recommendation
- Phase 6 — added "Prior State" section (fuzzy engine, WhenEntry model)
- Phase 6 cycles 6.2-6.4 — added validation specifics
- Phase 9 — added "Prior State" section (validator format support, compress-key)
- Phase 9 Step 9.2 — clarified semantic vs structural heading scope
- Phase 9 Step 9.5 — added checkpoint marker "validator must pass before proceeding"
- Phase 9 Step 9.8 — clarified redistribution includes creating new sections
- Expansion Guidance checkpoints — added mid-phase checkpoint after 3.6, clarified Phase 9 validator gate

## Design Alignment

**Architecture**: Outline follows design's component architecture exactly (fuzzy → parser → navigation → resolver → CLI → validator → migration sequence).

**Module structure**: Each phase maps to design module responsibilities (fuzzy.py ~80 lines Phase 0, resolver.py ~150 lines Phase 3, etc.).

**Key decisions**: All 9 design decisions (D-1 through D-9) referenced in Key Decisions Reference section. Phase implementations align with decisions:
- D-4 (custom fuzzy): Phase 0 implements ~80 line engine
- D-7 (validator uses fuzzy): Phase 6 imports Phase 0 engine
- D-8 (atomic migration): Phase 9 single commit with validator checkpoint

**Testing strategy**: Phases 0-7, 11 all TDD as required by NFR-2. Non-code phases (5, 8, 9, 10) appropriately marked as general.

## Positive Observations

**Foundation-first ordering**: Phase 0 (fuzzy) built first, consumed by Phases 3, 6, 7. No circular dependencies.

**Parallelization identified**: Outline explicitly notes Phases 0+1+2 can run in parallel (no dependencies), and Phases 6+7 can parallelize (both depend only on Phase 0).

**Model tier matching**: Haiku for TDD execution (Phases 0-7, 11), sonnet for migration complexity (Phase 9). Matches design's testing strategy and complexity assessment.

**Complexity assessment realistic**: Phase 3 marked High (integrates 3 prior phases), Phase 9 marked High (large-scope migration with ~159 entries + ~131 heading renames). Trivial phases appropriately minimized (bin script, skills).

**Checkpoint placement**: Three full checkpoints identified (after Phase 3, 6, 9) at critical integration and validation boundaries. Added mid-phase checkpoint for 9-cycle Phase 3.

**Migration safety**: Phase 9 includes validator run (Step 9.5) with explicit checkpoint before documentation updates. Atomic commit approach (D-8) enforced by step sequencing.

**Dependency clarity**: Each phase lists explicit dependencies by phase number and component. Prior state sections added for Phases 6 and 9 to document what earlier work established.

## Recommendations

**Expansion phase-by-phase**: Follow design's outline-first approach — expand each phase individually with vet review before proceeding. Phases 0-2 can expand in parallel.

**Mid-phase checkpoints**: For Phase 3, consider committing after Cycle 3.6 (core resolver logic) before error handling cycles. 9 cycles is manageable but checkpoint provides safety.

**Migration validation**: Phase 9 Step 9.5 validator run is critical gate. Do not proceed to documentation updates (9.6-9.8) until validator passes with zero errors.

**Fuzzy engine spike**: Design notes fuzzy engine may need scoring constant tuning (boundary bonuses, gap penalties). Consider spike before formal TDD if scoring behavior unclear.

**Test corpus reuse**: Existing recall tool tests (`tests/test_recall_*.py`) provide patterns for WhenEntry parsing and validation. Refer during Phase 1 and 6 expansion.

**Skills require restart**: Phase 8 skills need session restart for discovery. Note in expansion that manual verification (Step 8.3) requires restart after skill creation.

---

**Ready for full expansion**: Yes

All requirements traced, all issues fixed, phase structure sound, complexity distribution appropriate, checkpoints identified, execution-readiness validated.
