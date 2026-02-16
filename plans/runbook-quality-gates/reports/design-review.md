# Design Review: Runbook Quality Gates

**Design Document**: `plans/runbook-quality-gates/design.md`
**Review Date**: 2026-02-16
**Reviewer**: design-vet-agent (opus)

## Summary

The design specifies two-phase delivery of runbook quality gates: Phase A (prose edits to 6 architectural artifacts, opus-required) and Phase B (TDD script development for `validate-runbook.py` with 4 subcommands). The architecture is well-structured with clear pipeline positions (Phase 0.86 for simplification, Phase 3.5 for pre-execution validation), concrete agent and script specifications, and explicit delivery sequencing with graceful degradation bridging the gap.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **FR-6 Scaling had no architecture section**
   - Problem: FR-6 (Scaling by runbook size) was mentioned only in the Requirements summary line ("addressed by mandatory-for-all design") with no dedicated Architecture subsection explaining the mechanism.
   - Impact: A planner would not understand why separate scaling code paths are unnecessary, or how FR-6 acceptance criteria are satisfied.
   - Fix Applied: Added "Scaling (FR-6) -- Addressed by Design" section before Pipeline Contracts, explaining that scripts are O(n) text parsing, the simplification agent operates on bounded outline input, and plan-reviewer already runs per-phase. FR-6 acceptance criteria satisfied by uniform mandatory execution.

2. **Missing Requirements Traceability Table**
   - Problem: No formal mapping from each FR/NFR to its corresponding design element and delivery phase. Traceability was implicit from section headers but not consolidated.
   - Impact: Planner must reconstruct traceability by reading full design. Gaps harder to detect.
   - Fix Applied: Added Requirements Traceability section with table mapping all 10 requirement items (FR-1 through FR-6, NFR-1, NFR-2, including FR-2/FR-4 splits) to design elements and delivery phases.

3. **FR-1 requirements.md text not updated for D-1 decision**
   - Problem: `requirements.md` FR-1 says "After Phase 1 expansion completes (all phase files written)" but design decision D-1 moved consolidation to outline level (Phase 0.86, before expansion). The design correctly implements the outline discussion decision but the source requirements text is stale.
   - Impact: Planner reading requirements.md first gets conflicting guidance about when simplification runs.
   - Fix Applied: Added explicit note to D-1 documenting that requirements.md text was superseded and should be updated. (Requirements.md itself not modified -- that is the designer's responsibility, not a design document fix.)

### Minor Issues

1. **Phase 0.86 "When to skip" contradicted D-4 mandatory-for-all**
   - Problem: SKILL.md Phase 0.86 section said "When to skip: Outline has <=10 items" but D-4 says "mandatory for all Tier 3 runbooks." The skip condition contradicts the mandatory gate.
   - Fix Applied: Clarified that the agent still runs on small outlines but reports "no consolidation candidates" rather than skipping -- maintains mandatory gate while avoiding wasted effort.

2. **Problem statement only covered Phase 3-4 gap**
   - Problem: Problem section described gaps "between Phase 3 and Phase 4" but omitted the outline-level gap where redundant patterns inflate expansion cost. Design addresses two gaps (0.85-0.9 and 3-4) but problem statement only described one.
   - Fix Applied: Expanded problem statement to cover both pipeline positions: outline-to-expansion (redundant patterns) and Phase 3-to-4 (structural defects).

3. **NFR-2 incremental adoption mechanism unclear for subcommand architecture**
   - Problem: The outline referenced `--skip-*` flags but the design architecture uses individual subcommand invocations (orchestrator calls each subcommand separately). These are different mechanisms -- one is a flag on a combined invocation, the other is selective invocation.
   - Fix Applied: Added clarifying text to validate-runbook.py section: "Incremental adoption (NFR-2) achieved via subcommand granularity -- orchestrator invokes each check independently and can omit any subset."

## Requirements Alignment

**Requirements Source:** `plans/runbook-quality-gates/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes (with caveat) | Simplification Agent, Phase 0.86. Caveat: requirements.md text says post-expansion, design implements at outline level per D-1. |
| FR-2 (mechanical) | Yes | validate-runbook.py `model-tags` subcommand |
| FR-2 (semantic) | Yes | Review-Plan Skill Section 12 + plan-reviewer one-line addition |
| FR-3 | Yes | validate-runbook.py `lifecycle` subcommand |
| FR-4 (structural) | Yes | validate-runbook.py `red-plausibility` subcommand |
| FR-4 (semantic) | Yes | Optional agent delegation on exit code 2 |
| FR-5 | Yes | validate-runbook.py `test-counts` subcommand |
| FR-6 | Yes | Scaling section (added) -- mandatory uniform execution, no separate code paths |
| NFR-1 | Yes | SKILL.md Phase 0.86 + Phase 3.5, pipeline-contracts T2.5/T4.5 |
| NFR-2 | Yes | Graceful degradation (existence checks in skill), subcommand granularity (script) |
| C-1 | Yes | validate-runbook.py is read-only text analysis |
| C-2 | Yes | FR-1/FR-2 via agent/reviewer enrichment; FR-3-5 via Python script |

**Gaps:**
- FR-1 acceptance criteria reference "55 items pre-optimization" from workwoods -- this is an expanded-runbook metric, but design operates on outline items. Acceptance criteria should be restated in outline terms. Not fixed here (requires designer judgment on acceptance thresholds).

## Positive Observations

- **Clean delivery phase separation.** Phase A (prose, opus) vs Phase B (TDD, script) with explicit dependency analysis and graceful degradation bridging. This is a mature pattern that supports incremental deployment.
- **Concrete agent specification.** Simplification agent has YAML frontmatter, process steps, pattern detection categories, output format -- all actionable by the planner.
- **Precise review-plan integration.** Section 12 criteria with advisory severity and explicit "Do NOT mark as UNFIXABLE" constraint prevents the known over-escalation pattern.
- **D-7 verified.** All 5 functions referenced from prepare-runbook.py (`extract_cycles`, `extract_sections`, `extract_file_references`, `extract_step_metadata`, `assemble_phase_files`) confirmed to exist on disk.
- **Pipeline position diagram.** Single-line ASCII showing both new gates relative to existing phases -- clear at a glance.
- **Documentation Perimeter well-scoped.** Required reading is specific (6 files for Phase A, 2 additional for Phase B), not broad.

## Recommendations

- Update `requirements.md` FR-1 text to match D-1 decision (outline-level, not post-expansion). The design documents the discrepancy but the source requirements should be authoritative.
- Consider restating FR-1 acceptance criteria in outline-item terms (e.g., "given workwoods outline with N items, simplification produces M items") rather than expanded-runbook metrics.
- The outline's `--skip-*` flags (Incremental Adoption section) should be reconciled or removed since the design uses subcommand granularity instead. This is an outline cleanup, not a design issue.

## Next Steps

1. Update `requirements.md` FR-1 to reflect outline-level consolidation (designer action)
2. Proceed to `/runbook plans/runbook-quality-gates/design.md` for Phase A planning
