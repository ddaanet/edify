# Runbook Outline Review: skills-quality-pass

**Artifact**: plans/skills-quality-pass/runbook-outline.md
**Design**: plans/skills-quality-pass/design.md
**Date**: 2026-02-25
**Mode**: review + fix-all

## Summary

Well-structured outline with strong prose atomicity enforcement and correct bootstrapping order. All 10 FRs and 7 NFRs traced to specific steps. Primary issues were missing step-level traceability in mapping tables and underspecified checkpoint review mechanisms -- both fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 | 2, 3, 4, 5 | 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 5.1, 5.2 | Complete | 18 skills across 8 steps |
| FR-2 | 2, 3, 4, 5 | 2.3, 3.1, 3.2, 3.4, 3.5, 4.2, 4.4, 5.1, 5.2 | Complete | 13 skills across 9 steps |
| FR-3 | 3 | 3.1, 3.2, 3.3, 3.4, 3.5 | Complete | ~14 new reference files |
| FR-4 | 4 | 4.1, 4.2, 4.3, 4.4, 4.5 | Complete | ~7 new reference files |
| FR-5 | 1, 2, 3, 4 | 1.1, 2.1, 2.2, 2.3, 3.1, 4.5 | Complete | 12 gates across 6 steps |
| FR-6 | 3, 4, 5 | 3.4, 4.5, 5.2 | Complete | 3 targeted correctness fixes |
| FR-7 | -- | -- | Out of scope | Deferred to /codify per task constraint |
| FR-8 | 2, 3, 4, 5 | 2.1, 3.3, 3.4, 4.2, 5.1, 5.2 | Complete | 6 skills with fragment duplication |
| FR-9 | 2, 3, 4, 5 | 2.2, 2.3, 3.3, 3.4, 3.5, 4.2, 4.5, 5.1, 5.2 | Complete | 12 skills across 9 steps |
| FR-10 | 3 | 3.1, 3.2, 3.3, 3.4, 3.5 | Complete | Absorbed into FR-3 per design |
| NFR-1 | 2, 3, 4 | 2.1, 2.2, 2.3, 3.1, 3.4, 4.5 | Complete | Path enumeration for conditional-branch skills |
| NFR-2 | 2, 3, 4 | 2.1, 2.2, 3.1, 3.4, 4.5 | Complete | User-visible output verification |
| NFR-3 | 1-5 | All | Complete | Opus execution model throughout |
| NFR-4 | 1 | 1.1 | Complete | Phase 1 bootstrap + restart before all others |
| NFR-5 | 3, 4 | 3.1-3.5, 4.1, 4.2, 4.3 | Complete | Trigger + Read verification for each extraction |
| NFR-6 | 2-5 | All FR-1 steps | Complete | "This skill should be used when..." format preserved |
| NFR-7 | 1, 2, 3, 4 | 1.1, 2.1, 2.2, 2.3, 3.1, 4.5 | Complete | Gate steps verify no outcome change |

**Coverage Assessment**: All requirements covered. FR-7 explicitly deferred per task constraint.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 1 | Low | 6% | Appropriate (bootstrap) |
| 2 | 3 | Medium | 19% | Balanced |
| 3 | 5 | High | 31% | Balanced (largest compression scope justifies) |
| 4 | 5 | Medium | 31% | Balanced |
| 5 | 2 | Low | 13% | Balanced (batched mechanical edits) |

**Balance Assessment**: Well-balanced. No phase exceeds 40%. Phases 2-5 execute in parallel, so balance is per-agent rather than sequential.

### Complexity Distribution

- Low complexity phases: 2 (Phase 1, Phase 5)
- Medium complexity phases: 2 (Phase 2, Phase 4)
- High complexity phases: 1 (Phase 3)

**Distribution Assessment**: Appropriate. High complexity concentrated in Phase 3 (C/C+ body surgery) where extraction scope genuinely warrants it.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Requirements mapping table lacked step-level traceability**
   - Location: Requirements Mapping section
   - Problem: FR table had only Phase column, no Steps column. NFR table had no Phase or Steps columns. Protocol requires step-level traceability for expansion agents to verify coverage.
   - Fix: Added Steps and Notes columns to FR table with specific step references. Added Phases and Steps columns to NFR table.
   - **Status**: FIXED

2. **Checkpoint review mechanism underspecified**
   - Location: Phase 3 checkpoint, Phase 5 checkpoint, Expansion Guidance aggregate checkpoint
   - Problem: Checkpoints said "opus review of accumulated changes" without specifying the review mechanism (which skill/agent, what criteria). This is implicit "decide during execution" language.
   - Fix: Phase 3 checkpoint now specifies `/deliverable-review` against design compression targets and NFR-5. Phase 5 checkpoint specifies spot-check of representative skills for NFR-6 and content loss. Aggregate checkpoint specifies `/deliverable-review` sampling with specific NFR verification targets.
   - **Status**: FIXED

3. **Missing NFR-5 verification on 3 extraction steps**
   - Location: Steps 3.5, 4.1, 4.3
   - Problem: These steps extract content to references/ files but lacked explicit NFR-5 verification notes (trigger + Read load point check). Steps 3.1-3.4 and 4.2 had them; these 3 were inconsistent.
   - Fix: Added `**NFR-5:** Verify each references/ file has a load point` to all 3 steps.
   - **Status**: FIXED

### Minor Issues

1. **Missing dependency declarations on Phase 2-5 headers**
   - Location: Phase 2, 3, 4, 5 headers
   - Problem: Phase 1 post-phase note and Expansion Guidance stated the restart dependency, but individual phase headers lacked explicit `Depends on:` declarations. Expanding agents reading a single phase in isolation could miss the prerequisite.
   - Fix: Added `**Depends on:** Phase 1 + session restart` to each of Phases 2-5.
   - **Status**: FIXED

2. **FR-7 notes could be more precise**
   - Location: Requirements Mapping table, FR-7 row
   - Problem: Original note said "content in learnings.md line 87" without stating the deferral was per task constraint.
   - Fix: Updated to "Out of scope -- deferred to `/codify` (content in learnings.md line 87, per task constraint)".
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping FR table: Added Steps and Notes columns with specific step references for all 10 FRs
- Requirements Mapping NFR table: Added Phases and Steps columns for all 7 NFRs
- Phase 2 header: Added `**Depends on:** Phase 1 + session restart`
- Phase 3 header: Added `**Depends on:** Phase 1 + session restart`
- Phase 4 header: Added `**Depends on:** Phase 1 + session restart`
- Phase 5 header: Added `**Depends on:** Phase 1 + session restart`
- Phase 3 checkpoint: Specified `/deliverable-review` with criteria (compression targets, NFR-5)
- Phase 5 checkpoint: Specified spot-check review with criteria (NFR-6, content loss)
- Step 3.5: Added NFR-5 verification note
- Step 4.1: Added NFR-5 verification note
- Step 4.3: Added NFR-5 verification note
- FR-7 mapping notes: Added "per task constraint" provenance
- Weak Orchestrator Metadata checkpoints: Updated to match refined phase checkpoint descriptions
- Expansion Guidance aggregate checkpoint: Specified `/deliverable-review` with NFR sampling criteria

## Design Alignment

- **Architecture**: Aligned. Three workstreams (deslop, D+B anchoring, doc update) correctly mapped to outline phases. Doc update (FR-7) correctly deferred per task constraint.
- **Module structure**: Aligned. All 26 skills from design Implementation Notes appear in outline steps. All 3 agents covered in Phase 1.
- **Key decisions**: All 6 design decisions (D-1 through D-6) referenced in outline and enforced via step-level annotations.
- **Bootstrapping order (D-2/NFR-4)**: Correctly enforced -- Phase 1 fixes agents before Phases 2-5 modify skills those agents review.
- **Prose atomicity**: Verified -- no skill file appears in more than one step. All applicable FRs bundled per file.
- **Gate fix pattern (D-6)**: All 12 gates mapped to steps with specific tool-call insertions per full-gate-audit.md fix directions.

## Positive Observations

- Prose atomicity enforcement prevents the "file touched in multiple steps" anti-pattern that caused escalations in prior runbooks (learnings: TDD cycle test file growth)
- Parallel execution model with disjoint file sets is clean -- 4 agents with zero cross-agent file dependencies
- Recall artifact with 10 keys provides comprehensive context for expansion agents
- Variation tables in Phase 5 batch steps are an efficient expansion pattern -- per-skill FR applicability at a glance
- NFR enforcement annotations (NFR-1/2/5/6/7 checks) are co-located with the steps they govern, following the "place DO NOT rules where decisions are made" recall entry
- Agent lifecycle guidance uses quality signals rather than arbitrary token thresholds (correct per no-confabulation rule)

## Recommendations

Incorporated into Expansion Guidance section of the outline (co-located with structure for consumption during expansion). No additional recommendations beyond what is already embedded.

---

**Ready for full expansion**: Yes
