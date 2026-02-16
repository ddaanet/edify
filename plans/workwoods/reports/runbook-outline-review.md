# Runbook Outline Review: workwoods

**Artifact**: plans/workwoods/runbook-outline.md
**Design**: plans/workwoods/design.md
**Requirements**: plans/workwoods/requirements.md
**Date**: 2026-02-16
**Mode**: review + fix-all

## Summary

The outline is well-structured with complete requirements coverage, correct phase types (4 TDD, 2 mixed), and all 8 design decisions referenced. Issues were concentrated in cycle density (Phase 2 had 4 near-identical mapping cycles), missing deliverables (focus_session() update, jobs.md deletion step), and Phase 5 checkpoint spacing. All issues fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles/Steps | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 3, 4 | 3.1-3.8, 4.1-4.6 | Complete | Aggregation + CLI output |
| FR-2 | 2 | 2.1-2.5 | Complete | Mtime-based detection |
| FR-3 | 1 | 1.1-1.8 | Complete | Planstate module core |
| FR-4 | 5 | 5.11 | Complete | Skill update only (D-4) |
| FR-5 | 5 | 5.1-5.10 | Complete | Per-section merge strategies |
| FR-6 | 6 | 6.1-6.15 | Complete | Planstate adoption + archive + removal |
| NFR-1 | All | -- | Complete | Read-only aggregation pattern |
| NFR-2 | All | -- | Complete | Each tree owns session.md |
| NFR-3 | All | -- | Complete | All state versioned or computed |
| C-1 | 2 | 2.3-2.4 | Complete | Filesystem mtime for staleness |
| C-2 | 3 | 3.3 | Complete | Git commit hash anchor |
| C-3 | All | -- | Complete | No new config needed |

**Coverage Assessment**: All requirements covered.

## Phase Structure Analysis

### Phase Balance

| Phase | Items | Type | Percentage | Assessment |
|-------|-------|------|------------|------------|
| 1 | 8 | TDD | 14.5% | Balanced |
| 2 | 5 | TDD | 9.1% | Balanced (consolidated from 7) |
| 3 | 8 | TDD | 14.5% | Balanced |
| 4 | 6 | TDD | 10.9% | Balanced |
| 5 | 13 | Mixed | 23.6% | Acceptable (mid-phase checkpoint added) |
| 6 | 15 | Mixed | 27.3% | Acceptable (mechanical removals dominate) |

**Balance Assessment**: Well-balanced. Phases 5-6 are largest but Phase 5 has mid-phase checkpoint and Phase 6 is dominated by mechanical removal steps.

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 4)
- **Medium complexity phases**: 3 (Phases 1, 2, 6)
- **High complexity phases**: 2 (Phases 3, 5)

**Distribution Assessment**: Appropriate. High complexity concentrated in git interaction (Phase 3) and merge refactor (Phase 5) — both are genuinely complex.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Cycle 1.7 depends on unbuilt Phase 2**
   - Location: Phase 1, Cycle 1.7
   - Problem: "Gate attachment from vet status (integration with Phase 2)" implies calling vet.py which doesn't exist during Phase 1 execution
   - Fix: Clarified as "Gate attachment interface (stub vet call -- actual vet.py built in Phase 2; test gate wiring with mock VetStatus)"
   - **Status**: FIXED

2. **Missing focus_session() update**
   - Location: Phase 6
   - Problem: Design notes "Update focus_session() if it references jobs.md" but no outline step covered this
   - Fix: Added Step 6.13 for focus_session() jobs.md reference update
   - **Status**: FIXED

3. **Missing jobs.md deletion step**
   - Location: Phase 6
   - Problem: Design specifies deleting agents/jobs.md. Affected Files Summary listed it as deleted, but no step performed the deletion.
   - Fix: Added Step 6.14 to delete agents/jobs.md
   - **Status**: FIXED

4. **Phase 5 checkpoint spacing**
   - Location: Phase 5 (13 items, no internal checkpoint)
   - Problem: Phase 5 has 13 items total (10 TDD cycles + 3 general steps) with no internal checkpoint. Exceeds 8-item threshold.
   - Fix: Added Checkpoint 5.mid after Cycle 5.10 (TDD portion complete before skill edits)
   - **Status**: FIXED

### Minor Issues

1. **Cycle density: Phase 2 source→report mappings**
   - Location: Phase 2, Cycles 2.1-2.4
   - Problem: Four cycles each testing a single source→report mapping with <1 branch point difference. Parametrizable as a single test.
   - Fix: Consolidated into Cycle 2.1 (parametrized standard mappings) + Cycle 2.2 (phase-level fallback glob). Phase 2 reduced from 7 to 5 cycles.
   - **Status**: FIXED

2. **Steps 5.12 + 5.13 same-file collapse**
   - Location: Phase 5, Steps 5.12-5.13
   - Problem: Both steps modified execute-rule.md with related changes (STATUS transition + Unscheduled Plans transition)
   - Fix: Collapsed into single Step 5.12 covering full planstate transition in execute-rule.md
   - **Status**: FIXED

3. **Steps 6.12 + 6.13 same-file collapse**
   - Location: Phase 6, Steps 6.12-6.13
   - Problem: Both steps modified merge.py (removing conflict function + removing exempt_paths entry)
   - Fix: Collapsed into single Step 6.12 covering all jobs.md reference removal from merge.py
   - **Status**: FIXED

4. **New files count mismatch**
   - Location: Affected Files Summary
   - Problem: Header says "New files (6)" but lists 7 items (including agents/plan-archive.md)
   - Fix: Changed to "New files (7)"
   - **Status**: FIXED

5. **Post-phase state awareness for Step 5.12**
   - Location: Phase 5, Step 5.12
   - Problem: References list_plans() and PlanState without noting they come from Phase 1
   - Fix: Added "Depends on: Phase 1 (list_plans(), PlanState model)" declaration
   - **Status**: FIXED

## Fixes Applied

- Phase 1, Cycle 1.7 -- clarified as stub/mock interface for gate wiring (actual vet.py in Phase 2)
- Phase 2 -- consolidated cycles 2.1-2.4 into 2.1 (parametrized mappings) + 2.2 (fallback glob); updated cycle count 7->5
- Phase 5 -- collapsed Steps 5.12+5.13 into single Step 5.12; added Checkpoint 5.mid after TDD portion
- Phase 5, Step 5.12 -- added "Depends on: Phase 1" declaration
- Phase 6 -- collapsed Steps 6.12+6.13 into single Step 6.12; added Step 6.13 (focus_session), Step 6.14 (delete jobs.md), renumbered Step 6.15 (worktree skill Mode B)
- Phase 6 complexity -- updated 8->9 general steps
- Complexity Distribution table -- updated Phase 2 (7->5), Phase 5 (4->3 steps), Phase 6 (8->9 steps), total (57->55)
- Affected Files Summary -- fixed new files count 6->7
- Expansion Guidance -- added vacuity notes (Phase 5 keep-ours strategies), growth projection (cli.py exceeds threshold, merge.py monitor), Phase 2 consolidation note

## Design Alignment

- **Architecture**: Aligned. New planstate module separate from worktree (D-1). Module structure matches design exactly.
- **Phase types**: Aligned. 4 TDD (1-4), 2 mixed (5-6) per design Phase Type Classification table.
- **Key decisions**: All 8 decisions (D-1 through D-8) referenced in outline and reflected in phase structure.
- **Execution model**: Aligned. Sonnet for TDD, opus for skill edits per design directive.
- **Affected files**: Complete match against design Affected Files Summary table. All 18 design entries covered.
- **External dependency**: Correctly gated at Phase 5 with verification steps.

## Positive Observations

- Requirements mapping table includes NFRs and constraints, not just FRs -- thorough traceability
- External dependency handling is well-structured with concrete verification steps before Phase 5
- Phase types correctly distinguish TDD vs mixed portions with per-step model annotations
- Affected files inventory is complete and includes test files (both new and deleted)
- Classification table binding note in Expansion Guidance prevents strategy drift during expansion
- Investigation prerequisites section ensures expanding agents load the right context per phase

## Recommendations

- Phase 5 Cycles 5.2-5.7 (keep-ours strategies) should be consolidated into a parametrized cycle during expansion -- noted in Expansion Guidance vacuity section
- Phase 4 expansion should monitor cli.py growth and extract formatting if it exceeds 400 lines -- noted in Growth Projection
- Phase 6 Step 6.13 (focus_session) is conditional ("if it references jobs.md") -- expansion agent should grep first, skip if no reference found

---

**Ready for full expansion**: Yes
