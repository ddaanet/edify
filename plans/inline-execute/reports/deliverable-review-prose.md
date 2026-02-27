# Deliverable Review: Inline Execute Prose Artifacts

**Scope**: 9 files — 7 modified decision/pipeline/skill files + 2 new /inline skill files. Agentic prose review against outline.md design spec and requirements.md.
**Date**: 2026-02-27
**Mode**: review + fix
**Design reference**: plans/inline-execute/outline.md
**Requirements**: plans/inline-execute/requirements.md

## Summary

The deliverables implement all 10 FRs and 3 NFRs with high fidelity to the design outline. The /inline SKILL.md is well-structured with clear D+B anchors, the corrector template consolidates ad-hoc patterns correctly, and pipeline integration edits are consistent across continuation-passing, pipeline-contracts, and memory-index. One major functional completeness gap: /runbook Tier 2 lost its lightweight cycle planning guidance when execution was delegated to /inline, violating FR-10's explicit retention requirement.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Tier 2 lightweight cycle planning removed from /runbook**
   - Location: agent-core/skills/runbook/SKILL.md:138
   - Problem: FR-10 requires "/runbook retains tier assessment criteria and Tier 2 lightweight cycle planning." The diff removed the Tier 2 TDD and general work planning guidance ("Plan cycle descriptions (lightweight)", "Single agent for cohesive work; break into 2-4 components only if logically distinct"). /inline Phase 3 says "execution approach comes from caller's design/plan" but /runbook no longer tells the agent what to plan before invoking /inline. The criteria are retained; the planning instructions are not.
   - Axis: functional completeness (FR-10 retention requirement)
   - Suggestion: Add Tier 2 planning guidance before the `/inline` invocation line. The planning step should remain in /runbook; only execution mechanics moved to /inline.
   - **Status**: FIXED

### Minor Issues

1. **Corrector template heading level inconsistency with memory-index entry key**
   - Location: agents/decisions/pipeline-contracts.md:352
   - Problem: The heading "How To Dispatch Corrector From Inline Skill" uses H3 (`###`) under the H2 "When Using Inline Execution Lifecycle". The memory-index entry key is `/how dispatch corrector from inline skill` which resolves via `when-resolve.py` section matching. The entry key uses "dispatch" but the heading uses "How To Dispatch" — the `when-resolve.py` resolver handles this mapping, but the H3 nesting means the section is a subsection, not a standalone entry point. If a consumer resolves `/how dispatch corrector from inline skill` they get the parent H2 context too, which is correct behavior for subsection resolution. No action needed — noting for completeness.
   - Axis: constraint precision
   - **Status**: OUT-OF-SCOPE — memory-index resolution mechanics, not inline-execute deliverable content

2. **execution-strategy.md "Separate task" sentence removed**
   - Location: agents/decisions/execution-strategy.md:28
   - Problem: The original text ended with "Separate task: calibrate against execution history." The diff replaced this with the expanded calibration data source paragraph. The removal of the action item is intentional — the calibration data source now names the specific mechanism (triage-feedback-log.md) rather than a vague task reference. This is an improvement.
   - Axis: n/a (positive observation, not issue)
   - **Status**: OUT-OF-SCOPE

3. **Phase 2.4 Reference Loading not in design outline**
   - Location: agent-core/skills/inline/SKILL.md:82-84
   - Problem: The outline's Phase 2 covers task-context, brief, recall-artifact, and lightweight recall. SKILL.md adds "2.4 Reference Loading" for domain-relevant skills and reference files. This is additive guidance consistent with the pre-work intent but not traced to a specific design decision.
   - Axis: excess (minor — guidance is useful but unspecified)
   - **Status**: DEFERRED — useful enhancement, no design violation. Could be traced to a future design update.

## Fixes Applied

- agent-core/skills/runbook/SKILL.md:138 — Restored Tier 2 planning guidance (TDD cycle planning and general work component planning) before the `/inline` invocation, preserving FR-10's retention requirement.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 | Satisfied | agent-core/skills/design/SKILL.md:114 — Write step added to Phase 0 after classification block |
| FR-2 | Satisfied | agent-core/skills/inline/SKILL.md:54-84 — Phase 2 with task-context, brief, recall, reference loading |
| FR-3 | Satisfied | agent-core/skills/inline/SKILL.md:86-119 — Phase 3 with Tier 1/2 execution |
| FR-4 | Satisfied | agent-core/skills/inline/SKILL.md:123-137, references/corrector-template.md — standardized corrector dispatch |
| FR-5 | Satisfied | agent-core/skills/inline/SKILL.md:141-143 — triage-feedback.sh invocation with baseline |
| FR-6 | Satisfied | triage-feedback.sh performs comparison (script-level, not reviewed here) |
| FR-7 | Satisfied | triage-feedback.sh appends to log (script-level, not reviewed here) |
| FR-8 | Satisfied | agent-core/skills/inline/SKILL.md:148-153 — deliverable-review chain via handoff continuation |
| FR-9 | Satisfied | agent-core/skills/design/SKILL.md:331,424 — Phase B and C.5 route to `/inline plans/<job> execute` |
| FR-10 | Satisfied (after fix) | agent-core/skills/runbook/SKILL.md:122,138 — Tier 1 and Tier 2 route to `/inline`; Tier 2 planning guidance restored |
| NFR-1 | Satisfied | Chained path overhead: ~3-4 tool calls per outline budget |
| NFR-2 | Satisfied | Detection is script-based; no automatic correction |
| NFR-3 | Satisfied | Single corrector template in references/corrector-template.md |
| C-1 | Satisfied | /design writes classification.md; /inline only reads it |
| C-2 | Satisfied | Classification block written verbatim (SKILL.md:114 says "verbatim") |
| C-3 | Satisfied | execution-strategy.md:32, pipeline-contracts.md:358 both note initial estimates |
| C-4 | Satisfied | /inline covers Tier 1/2 only; Tier 3 explicitly excluded |

## Design Decision Verification

| Decision | Status | Evidence |
|----------|--------|----------|
| D-1: Named entry points | Correct | SKILL.md:22-28 — `execute` entry point, no flags |
| D-2: Evidence + triage as script | Correct | SKILL.md:141-143 — invokes triage-feedback.sh |
| D-3: Classification persistence in /design | Correct | design/SKILL.md:114 — Write step in Phase 0 |
| D-4: Single corrector template | Correct | references/corrector-template.md — one template, one place |
| D-5: Deliverable-review via handoff | Correct | SKILL.md:148-153 — states pending task, continuation invokes handoff |
| D-6: Skill structure with continuation | Correct | Frontmatter, allowed-tools, continuation section all match spec |
| T6.5: Pipeline contracts entry | Correct | pipeline-contracts.md:17 — transformation table row |

## Integration Consistency

| Integration point | Status | Notes |
|-------------------|--------|-------|
| continuation-passing.md | Consistent | /inline row added, "Six cooperative skills" count updated |
| pipeline-contracts.md | Consistent | T6.5 row + 3 new decision sections |
| memory-index.md | Consistent | 3 new entries, T1-T6 updated to T1-T6.5 |
| memory-index SKILL.md copy | Consistent | Identical 3 new entries, identical T6.5 update |
| execution-strategy.md | Consistent | Checkpoint frequency noted as ungrounded, calibration source named |

---

## Positive Observations

- The corrector-template.md lightweight recall fallback (lines 52-65) is well-designed — provides specific `when-resolve.py` keys that resolve to review-relevant entries, preventing cold-start corrector from operating without context.
- Phase 4c's mechanism (state pending task in conversation, let handoff capture it) is a clean use of existing continuation infrastructure without new machinery.
- The delegation protocol summary table (SKILL.md:157-165) provides a scannable reference for the 7 delegation rules, complementing the prose descriptions.
- D+B anchors throughout the SKILL.md (git status, just precommit, when-resolve.py, git rev-parse HEAD) are concrete and non-skippable.

## Recommendations

- The pre-existing divergence between memory-index.md (source) and memory-index SKILL.md (copy) entry keys is significant — e.g., `/when choosing review gate` vs `/when transformation table`, `/when declaring phase type` vs `/when phase type model`. The 3 new entries are identical, but older entries differ. This is a known sync issue (SKILL.md comment says "Synced from agents/memory-index.md") that should be addressed separately.
