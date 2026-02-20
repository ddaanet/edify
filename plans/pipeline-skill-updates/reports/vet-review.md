# Vet Review: Pipeline Skill Updates (D-1 through D-9)

**Scope**: 9 design decisions from `plans/pipeline-skill-updates/outline.md` implemented as additive prose edits across 7 files (6 in agent-core submodule, 1 in parent repo)
**Date**: 2026-02-20
**Mode**: review + fix

## Summary

All 9 design decisions are correctly implemented. Cross-references between files are consistent (D-4/D-9 vet-requirement↔pipeline-contracts, D-6 design↔tdd-task). D-5 coordination complexity wording is consistent across all 4 locations in design/SKILL.md. No issues found.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

No fixes needed.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-1: Requirements-clarity gate before triage | Satisfied | `agent-core/skills/design/SKILL.md:27-33` — gate at top of Section 0, before "Before doing design work" |
| D-2: Deliverable-review pending task | Satisfied | `agent-core/skills/orchestrate/SKILL.md:303-307` — step 4 creates pending task, explicit "Do NOT run inline" |
| D-3: Unconditional /design routing | Satisfied | `agent-core/skills/deliverable-review/SKILL.md:153-155` — task format routes to `/design`, line 157 prohibits merge-readiness language |
| D-3a: Exclude plan artifacts from line count | Satisfied | `agent-core/skills/deliverable-review/SKILL.md:46` — exclusion with rationale |
| D-4: Verification scope optional field | Satisfied | `agent-core/fragments/vet-requirement.md:96` (field definition) + lines 118-120 (template section) |
| D-5: Coordination complexity replaces ≤3 files | Satisfied | 4 locations updated: line 39 (artifact check), lines 152-156 (post-outline re-check), lines 217-222 (sufficiency gate), lines 419-424 (C.5). Remaining ≤3 files on line 116 is A.2 exploration delegation — different context, not execution readiness |
| D-6: TDD integration-first cross-reference | Satisfied | `agent-core/skills/design/SKILL.md:322` (C.1 design output) + `agent-core/agents/tdd-task.md:24` (execution awareness). Complementary references to Diamond Shape |
| D-7: Final checkpoint lifecycle audit | Satisfied | `agent-core/skills/orchestrate/SKILL.md:188-194` — conditional on final phase boundary, methodology matches exit code audit pattern |
| D-8: Resume completeness criterion | Satisfied | `agent-core/agents/outline-review-agent.md:103-107` — scoped to agent/state machine designs, targets non-terminal states |
| D-9: Verification scope decision section | Satisfied | `agents/decisions/pipeline-contracts.md:274-293` — links D-4, documents indicators and identification method |

**Gaps:** None.

## Cross-Reference Verification

| Cross-reference | Status |
|----------------|--------|
| D-4 vet-requirement.md ↔ D-9 pipeline-contracts.md | Consistent — pipeline-contracts.md:290 references vet-requirement.md as operational location |
| D-6 design/SKILL.md ↔ tdd-task.md | Complementary — design references Diamond Shape for output guidance, tdd-task references it for execution awareness |
| D-5 consistency (4 locations) | Consistent — artifact check uses "low coordination complexity" shorthand; re-check, sufficiency gate, and C.5 all use full criteria lists |
| D-7 orchestrate ↔ pipeline-contracts.md:264-272 | Consistent — orchestrate implements what the existing decision section describes |

## Positive Observations

- D-5 was applied to all 4 locations including the artifact check shorthand — thorough propagation
- D-2 explicitly prohibits inline execution with rationale (model tier, context, restart)
- D-3 routing is clean — unconditional `/design` with explicit "No merge-readiness language" prohibition
- D-8 scoping qualifier ("Applicable when outline defines agents, state machines, or multi-step workflows") prevents the criterion from applying to inappropriate contexts
- Post-Outline Re-check uses a different but compatible criteria set from the full direct execution criteria — appropriate since it gates complexity downgrade, not execution readiness
