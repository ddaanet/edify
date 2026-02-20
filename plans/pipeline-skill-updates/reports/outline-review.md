# Outline Review: Pipeline Skill Updates

**Artifact**: plans/pipeline-skill-updates/outline.md
**Date**: 2026-02-20T18:09:06Z
**Mode**: review + fix-all

## Summary

The outline is technically sound and well-structured. All 11 FRs and 2 NFRs are covered in scope and affected files. Five minor issues found: FR-6, FR-7 (D-4), FR-8, FR-9, FR-10, and FR-11 were mentioned in scope/files but had no Key Decision entries explaining what the changes entail, leaving implementers with insufficient specification for the smaller edits. All fixed by adding D-6 through D-9.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Orchestrate deliverable-review pending task | Scope IN, Affected Files, D-2 | Complete | D-2 explains task vs inline rationale |
| FR-2: Deliverable-review Phase 4 finding→task, no merge-readiness | Scope IN, Affected Files, D-3 | Complete | D-3 gives routing rationale |
| FR-3: Deliverable-review Phase 1 excludes plan artifacts | Scope IN, D-3a | Complete | D-3a lists excluded artifact types |
| FR-4: Design skill requirements-clarity gate | Scope IN, Affected Files, D-1 | Complete | D-1 explains gate placement |
| FR-5: Execution readiness gate coordination complexity | Scope IN, Affected Files, D-5 | Complete | D-5 gives replacement criteria |
| FR-6: Design C.1 TDD integration-first reference | Scope IN, Affected Files | Partial → Fixed | Added D-6: cross-reference only, no new content |
| FR-7: vet-requirement.md verification scope field | Scope IN, Affected Files, D-4 | Complete | D-4 explains when to omit vs include |
| FR-8: pipeline-contracts.md verification scope docs | Scope IN, Affected Files | Partial → Fixed | Added D-9: memory-index home for D-4 rationale |
| FR-9: Orchestrate final checkpoint lifecycle audit | Scope IN, Affected Files | Partial → Fixed | Added D-7: lifecycle audit criterion definition |
| FR-10: outline-review-agent resume completeness | Scope IN, Affected Files | Partial → Fixed | Added D-8: what "resume completeness" means |
| FR-11: tdd-task integration-first awareness | Scope IN, Affected Files | Complete | Propagation of existing strategy, no new definition |
| NFR-1: Additive prose only, no new files | Approach, Scope OUT, Affected Files | Complete | All table entries show +lines only (one -3 removal) |
| NFR-2: All decisions pre-resolved | Approach, Key Decisions, Execution Assessment | Complete | Absorbed designs cited; all decisions have rationale |

**Traceability Assessment**: All requirements covered. Four partial coverages fixed by adding D-6 through D-9.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **FR-6 TDD integration-first had no Key Decision entry**
   - Location: Key Decisions section (before fix)
   - Problem: Design C.1 change was listed in scope and affected files but no decision explained what the reference would contain or why it's a cross-reference vs new content. Implementer would need to infer intent from the problem statement alone.
   - Fix: Added D-6 clarifying it's a cross-reference to existing runbook/SKILL.md definition, no new strategy content generated.
   - **Status**: FIXED

2. **FR-9 lifecycle audit criterion had no Key Decision entry**
   - Location: Key Decisions section (before fix)
   - Problem: "Lifecycle audit at final checkpoint" listed in affected files with +20 lines budget but no definition of what the audit criterion entails. Exit code audit (the model this follows) was not called out as the structural pattern.
   - Fix: Added D-7 defining the criterion: stateful objects (MERGE_HEAD, staged content, lock files), same methodology as exit code audit applied to git state.
   - **Status**: FIXED

3. **FR-10 resume completeness had no definitional note**
   - Location: Key Decisions section (before fix)
   - Problem: "Resume completeness criterion" is a term of art — an implementer editing outline-review-agent.md would need to know what states/transitions to verify. No definition in the outline.
   - Fix: Added D-8 defining resume completeness as: all non-terminal states must have a defined resume path (what agent does when restarted mid-state).
   - **Status**: FIXED

4. **FR-8 pipeline-contracts.md role was not explained**
   - Location: Key Decisions section (before fix)
   - Problem: Both vet-requirement.md (D-4) and pipeline-contracts.md address the verification scope field. The outline didn't explain why both need edits or what pipeline-contracts adds beyond D-4.
   - Fix: Added D-9 clarifying pipeline-contracts is the memory-index/decision-record home (when/why) while vet-requirement is the operational (how) location.
   - **Status**: FIXED

## Fixes Applied

- Key Decisions section — Added D-6: TDD integration-first in design C.1 is a cross-reference only
- Key Decisions section — Added D-7: Orchestrate lifecycle audit criterion definition (stateful objects, exit-code audit model)
- Key Decisions section — Added D-8: outline-review-agent resume completeness definition (non-terminal states, resume paths)
- Key Decisions section — Added D-9: pipeline-contracts.md role as memory-index home for D-4 rationale

## Positive Observations

- Problem Statement clearly separates the three absorbed concerns (pipeline closure gaps, vet scoping deficit, TDD propagation) with distinct rationale for each.
- D-2 correctly identifies the cross-model constraint (orchestrate runs sonnet/haiku; deliverable review needs opus + restart) — prevents a common mistake of inlining review at wrong model tier.
- D-3 ties unconditional /design routing to pipeline-contracts.md by name — traceable and non-arbitrary.
- D-3a specifically lists artifact types to exclude (runbook files, step files, phase files, orchestrator plans, review reports) — precise enough to implement without ambiguity.
- Scope OUT is explicit and well-reasoned: inline-phase-type already implemented, with codebase locations listed. Prevents re-implementation of work already done.
- Execution Assessment applies D-5 criteria to itself — the outline self-validates against its own proposed gate.

## Recommendations

- FR-11 (tdd-task integration-first awareness) has only +5 lines budgeted. If the awareness requires citing the Diamond Shape strategy and providing ordering guidance (unit tests before integration), 5 lines may be tight. Confirm scope at implementation time.
- D-7 lifecycle audit: the orchestrate/SKILL.md final checkpoint section should reference this agent-core learning explicitly (the MERGE_HEAD submodule finding from the merge skill implementation) so the criterion is grounded in a real failure, not abstract policy.

---

**Ready for user presentation**: Yes
