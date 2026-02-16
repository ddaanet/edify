# Runbook Outline Review: Worktree Merge Data Loss

**Artifact**: plans/worktree-merge-data-loss/runbook-outline.md
**Design**: plans/worktree-merge-data-loss/design.md
**Date**: 2026-02-16T12:00:00Z
**Mode**: review + fix-all

## Summary

Outline is well-structured with clear phase separation (TDD + general), comprehensive requirements mapping, and detailed expansion guidance. All 9 functional requirements are traced to specific cycles. Phase structure balances two independent implementation tracks (removal guard, merge correctness) within a single TDD phase, followed by a minimal prose update phase.

**Overall Assessment**: Ready

---

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1 | 1.1-1.3 | Complete | Helper functions + classification logic |
| FR-2 | 1 | 1.4 | Complete | Guard refusal with exit 1 |
| FR-3 | 1 | 1.3 | Complete | Marker text detection for focused sessions |
| FR-4 | 1 | 1.4 | Complete | Exit codes 0/1/2 in guard logic |
| FR-5 | 1 | 1.5 | Complete | Message cleanup, no destructive suggestions |
| FR-6 | 1 | 1.6-1.8 | Complete | Three-branch MERGE_HEAD checkpoint |
| FR-7 | 1 | 1.9 | Complete | Ancestry validation after merge |
| FR-8 | 1 | 1.5 | Complete | Success message differentiation |
| FR-9 | 2 | 2.1 | Complete | Skill Mode C prose update |

**Coverage Assessment**: All requirements covered with explicit cycle references and clear notes.

---

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles/Steps | Complexity | Percentage | Assessment |
|-------|--------------|------------|------------|------------|
| 1 (TDD) | 11 cycles | Medium-High | 92% | Dominant but appropriate for dual-track behavioral changes |
| 2 (general) | 1 step | Low | 8% | Minimal prose update, correctly isolated |

**Balance Assessment**: Imbalance appropriate given scope. Phase 1 contains two independent tracks (removal guard + merge correctness) with shared dependencies, necessitating combined phase. Phase 2 is minimal by design (single prose addition).

### Complexity Distribution

- **Phase 1**: Medium-High (11 cycles covering guard logic, checkpoint logic, validation, 2 integration tests)
- **Phase 2**: Low (single prose update to skill documentation)

**Distribution Assessment**: Appropriate. Phase 1 complexity reflects defensive programming requirements (guard before destruction, MERGE_HEAD checkpoint, ancestry validation). Phase 2 is correctly minimal.

---

## Review Findings

### Critical Issues

None identified.

### Major Issues

**1. Vague integration test assertion (Cycle 1.10)**
- **Location**: Phase 1, Cycle 1.10
- **Problem**: RED assertion said "check for pipeline-contracts.md, learnings.md, memory-index.md" but these are incident-specific files, not general test pattern. Test should verify ANY parent repo file preservation, not specific incident files.
- **Fix**: Clarified RED assertion to create a test file (`parent-change.md`) and verify its presence after merge. Added Track 2 label for clarity. Expansion Guidance updated to remove incident-specific file references.
- **Status**: FIXED

**2. Missing Track label (Cycle 1.11)**
- **Location**: Phase 1, Cycle 1.11
- **Problem**: Integration test for orphan branch handling didn't indicate it tests Track 1 (rm guard edge case), not Track 2 (merge correctness).
- **Fix**: Added Track 1 label, clarified this tests rm guard with orphan branch scenario, emphasized directory preservation as regression test.
- **Status**: FIXED

**3. Cycle count mismatch**
- **Location**: Phase 1 header, "Estimated complexity" line
- **Problem**: Said "~12 cycles" but actual count is 11 cycles (1.1-1.11).
- **Fix**: Updated to "11 cycles" for accuracy.
- **Status**: FIXED

### Minor Issues

**1. Duplicate Expansion Guidance sections**
- **Location**: Lines 149-180 and 195-224
- **Problem**: Two separate "Expansion Guidance" sections with different content. First section contained generic guidance, second contained specific recommendations. Redundant structure.
- **Fix**: Consolidated into single Expansion Guidance section with organized subsections: cycle granularity, test patterns, RED assertions, GREEN implementation (with Track 1/2 breakdown), file growth monitoring, checkpoint validation, prerequisite validation.
- **Status**: FIXED

**2. File growth projection missing calculation detail**
- **Location**: Expansion Guidance, file growth monitoring subsection
- **Problem**: Mentioned "cli.py projected at 417 lines (borderline)" without showing calculation baseline + additions.
- **Fix**: Added explicit calculations: cli.py (382 baseline + 35 LOC = 417), merge.py (299 + 25 = 324), utils.py (38 + 8 = 46). Provides transparency for growth assessment.
- **Status**: FIXED

**3. Integration test execution order unclear**
- **Location**: Expansion Guidance, GREEN phase implementation
- **Problem**: Generic statement "Integration tests final (Cycles 1.11-1.12)" but there are only 11 cycles total (1.11 is the last).
- **Fix**: Restructured GREEN phase implementation to separate Track 1 and Track 2 cycles explicitly, showing C1.10-C1.11 as integration tests for their respective tracks. Clarified dependency (C1.6 depends on C1.1).
- **Status**: FIXED

---

## Fixes Applied

- Line 31: Updated cycle count from "~12 cycles" to "11 cycles"
- Lines 86-88: Enhanced Cycle 1.10 RED assertion with Track 2 label, clarified test pattern (create test file, verify presence), added regression test note
- Lines 91-93: Enhanced Cycle 1.11 RED assertion with Track 1 label, detailed orphan branch setup, emphasized directory preservation as regression test
- Lines 149-224: Consolidated duplicate Expansion Guidance sections, reorganized into clear subsections (cycle granularity, test patterns, RED assertions, GREEN implementation with Track 1/2 breakdown, file growth with calculations, checkpoint validation, prerequisite validation)

---

## Phase Structure Analysis

### Phase 1: Safety Guards and Merge Correctness (TDD)

**Cycle organization:**
- Foundation (C1.1): Shared helper `_is_branch_merged` in utils.py
- Track 1 — Removal guard (C1.2-C1.5): Classification helper → focused-session detection → refusal logic → messaging
- Track 2 — Merge correctness (C1.6-C1.9): MERGE_HEAD checkpoint → idempotency → no-op case → ancestry validation
- Integration (C1.10-C1.11): Track 2 regression test (parent file preservation), Track 1 edge case (orphan branch)

**Dependencies:**
- C1.2 depends on C1.1 (uses `_is_branch_merged`)
- C1.3-C1.5 depend on C1.2 (use `_classify_branch`)
- C1.6 depends on C1.1 (uses `_is_branch_merged`)
- C1.7-C1.8 extend C1.6 (build on checkpoint logic)
- C1.9 depends on C1.1 (ancestry validation uses merge-base)
- C1.10-C1.11 are independent integration tests (can run in any order after C1.9)

**Intra-phase ordering**: Foundation-first (C1.1), then two parallel tracks (C1.2-C1.5 for Track 1, C1.6-C1.9 for Track 2), finally integration tests (C1.10-C1.11). No forward dependencies detected. Ordering is correct.

### Phase 2: Skill Update (general)

Single step: prose addition to SKILL.md Mode C. Minimal scope, correctly isolated from Phase 1 implementation.

---

## Design Alignment

**Architecture**: Outline follows design's three-track structure (Track 1 cli.py rm, Track 2 merge.py Phase 4, Track 3 SKILL.md). Phase 1 combines Track 1 + Track 2 into single TDD phase due to shared helper dependency (_is_branch_merged). Phase 2 isolates Track 3 as general phase.

**Module structure**: Shared helper in utils.py (D-7), rm-specific logic in cli.py, merge logic in merge.py, skill prose in SKILL.md. Matches design partitioning.

**Key decisions**: All 7 design decisions (D-1 through D-7) referenced in Phase 1 scope section. Cycles implement decisions correctly:
- D-1 (marker text): C1.3
- D-2 (exit codes): C1.4
- D-3 (no destructive output): C1.5
- D-4 (MERGE_HEAD checkpoint): C1.6-C1.8
- D-5 (ancestry validation): C1.9
- D-6 (guard before destruction): C1.3-C1.4
- D-7 (shared helper): C1.1

**Testing strategy**: All tests use real git repos per design requirement. Integration tests (C1.10-C1.11) cover regression scenarios from incident.

---

## Positive Observations

**Requirements traceability**: Excellent requirements mapping table with explicit cycle references. Every FR maps to specific implementation cycles, not just phases.

**Phase type tagging**: Correct TDD/general tagging. Phase 1 properly tagged TDD (behavioral changes), Phase 2 general (prose).

**Cycle granularity**: Each cycle tests single branch point or error condition. No bloated cycles combining multiple behavioral changes. C1.10-C1.11 are properly scoped integration tests.

**Expansion Guidance quality**: Detailed guidance with test patterns, fixture references, RED assertion criteria, GREEN implementation order, file growth projections, checkpoint validation details. Planner has clear execution roadmap.

**Foundation-first ordering**: C1.1 (shared helper) precedes all dependent cycles. Guard logic builds incrementally (C1.2 → C1.3 → C1.4 → C1.5). Checkpoint logic builds incrementally (C1.6 → C1.7 → C1.8).

**Integration test placement**: Integration tests last (C1.10-C1.11) after all unit cycles. Correct ordering — unit tests establish behavior, integration tests verify composition.

**Design decision references**: All 7 design decisions explicitly listed in Phase 1 scope. Cycles reference decisions in descriptions. Strong traceability from design to implementation.

**Checkpoint specification**: Full checkpoint after Phase 1 with fix (commit), vet (execution context), and functional validation (reproduction scenario). Defense-in-depth verification.

---

## Recommendations

**During expansion:**

1. **Parallel execution opportunity**: Track 1 cycles (C1.2-C1.5) and Track 2 cycles (C1.6-C1.9) are independent after C1.1 completes. If orchestrator supports parallel cycle execution, these tracks can run concurrently.

2. **File growth monitoring**: cli.py projected at 417 lines (borderline). If implementation grows during GREEN phase, consider extracting guard logic to `cli_guards.py` before crossing 420-line threshold. Expansion Guidance documents split point.

3. **Integration test value**: C1.10 (parent file preservation) may pass without code changes if incident was environment-specific. If so, test still valuable as regression guard (prevents future introduction of single-parent commit bug).

4. **Orphan branch test setup**: C1.11 requires creating orphan branch with `git checkout --orphan`. Ensure test setup includes commits on orphan branch (zero commits makes it indistinguishable from non-existent branch).

---

**Ready for full expansion**: Yes
