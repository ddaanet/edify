# Design Outline: Pipeline Skill Updates

## Problem Statement

Three pipeline closure gaps and one vet scoping deficit discovered through deliverable review analysis and 5-round discussion in runbook-skill-fixes worktree.

**Pipeline closure gaps:**
1. Orchestrate completes without creating deliverable review task — findings never tracked
2. Deliverable-review writes report but doesn't create follow-up task — findings become aspirational prose
3. Design skill lacks requirements-clarity gate — designs proceed against vague requirements

**Vet scoping deficit (absorbed from vet-invariant-scope):**
- Phase checkpoint vet verifies delta (changed files only), misses cross-cutting invariants
- Final checkpoint applies cross-cutting methodology selectively (exit codes but not state lifecycle)
- Outline review doesn't verify resume completeness for state machines

**TDD definition propagation (absorbed insight):**
- Integration-first (Diamond Shape) testing strategy exists in runbook/SKILL.md but not in design skill (which produces TDD mode guidance) or tdd-task agent (which executes cycles)

**Execution readiness gate stale wording:**
- Design skill still uses ≤3 files heuristic, superseded by coordination complexity discriminator (workflow-optimization.md updated 2026-02-19)

## Approach

Additive prose edits to existing pipeline artifacts. No new files, no code changes. All decisions pre-resolved from absorbed designs and prior discussion.

inline-phase-type already fully implemented in codebase (pipeline-contracts.md, runbook/SKILL.md, plan-reviewer.md, review-plan/SKILL.md, orchestrate/SKILL.md, prepare-runbook.py) — no remaining work.

## Key Decisions

**D-1: Requirements-clarity gate placement.** Insert BEFORE complexity triage (new Section 0 top), not within A.0. Rationale: triage reads artifacts that depend on requirements being clear. Gate fires before any artifact reading.

**D-2: Orchestrate deliverable-review is a pending task, not inline execution.** Creates pending task at session exit, not running deliverable-review in the orchestration session. Rationale: orchestrate runs at sonnet/haiku; deliverable review needs opus + cross-project context + restart (for any new agents produced).

**D-3: Deliverable-review finding→task is unconditional /design.** Per pipeline-contracts.md "When Routing Implementation Findings" — all findings route to /design, which triages proportionality. No severity-based routing at review time.

**D-3a: Deliverable line count excludes plan artifacts.** Phase 1 inventory line counts (used for Layer 1 gating) must exclude plan directory artifacts (runbook files, step files, phase files, orchestrator plans, review reports). These are planning/execution artifacts, not production deliverables. Including them inflates the count and triggers unnecessary Layer 1 delegation.

**D-4: Verification scope is optional in vet template.** Added when cross-cutting invariants exist (D-N "all X must Y", NFR spanning multiple modules). Omitted for local requirements. Orchestrator identifies from design decisions.

**D-5: Execution readiness gate uses coordination complexity.** Replace ≤3 files criterion in both Sufficiency Gate and C.5 with: all decisions pre-resolved + changes additive + cross-file deps phase-ordered + content derivable from architecture. File count is a proxy; the underlying property is "no implementation loops."

**D-6: TDD integration-first in design C.1 is a cross-reference only.** Design C.1 generates TDD mode guidance notes. Add a reference to the Diamond Shape integration-first strategy (already defined in runbook/SKILL.md) so the design phase output guides TDD execution correctly. No new content generated — reference to existing strategy definition.

**D-7: Orchestrate lifecycle audit criterion is a checklist addition.** Final checkpoint already performs cross-cutting exit code audit. Add a parallel criterion: audit stateful objects (MERGE_HEAD, staged content, lock files) created during implementation for lifecycle completeness — every code path that exits success must have cleared active state. Same methodology as exit code audit, applied to git state.

**D-8: outline-review-agent resume completeness targets state machine transitions.** "Resume completeness" means: verify that all non-terminal states have a defined resume path (what the agent does when restarted mid-state). Catches agent designs that define entry/exit but leave intermediate states unrecoverable.

**D-9: pipeline-contracts.md verification scope is the memory-index home for D-4.** vet-requirement.md is always-loaded context; pipeline-contracts.md is the decision record. The pipeline-contracts entry captures when/why to add the field, linking to D-4 framing. Both are needed: operational (vet-requirement) + rationale (pipeline-contracts).

## Scope Boundaries

**IN:**
- Design skill: requirements-clarity gate (Phase 0), execution readiness update (Sufficiency Gate + C.5), TDD integration-first reference (C.1)
- Orchestrate skill: deliverable-review pending task at completion, lifecycle audit at final checkpoint
- Deliverable-review skill: finding→task creation in Phase 4, remove merge-readiness language, exclude plan artifacts from line count
- vet-requirement.md: verification scope field in execution context template
- pipeline-contracts.md: verification scope documentation
- outline-review-agent.md: resume completeness criterion
- tdd-task agent: integration-first awareness

**OUT:**
- inline-phase-type implementation (already in codebase)
- prepare-runbook.py changes (inline already handled)
- Batching threshold measurement (deferred — D-3 in inline-phase-type)
- Runbook skill / plan-reviewer / review-plan changes (inline already handled)
- New tooling or scripts

## Affected Files

| File | Changes | Approx Lines |
|------|---------|-------------|
| `agent-core/skills/design/SKILL.md` | Requirements-clarity gate, execution readiness gate update, TDD integration-first ref | +25 |
| `agent-core/skills/orchestrate/SKILL.md` | Deliverable-review task at completion, lifecycle audit at final checkpoint | +20 |
| `agent-core/skills/deliverable-review/SKILL.md` | Finding→task in Phase 4, remove merge-readiness, exclude plan artifacts from line count | +15, -3 |
| `agent-core/fragments/vet-requirement.md` | Verification scope optional field in template | +8 |
| `agents/decisions/pipeline-contracts.md` | Verification scope documentation section | +15 |
| `agent-core/agents/outline-review-agent.md` | Resume completeness criterion | +8 |
| `agent-core/agents/tdd-task.md` | Integration-first awareness | +5 |

**Total:** 7 files, ~91 net lines added. All additive prose.

## Execution Assessment

All criteria for execution readiness hold:
- Decisions pre-resolved (absorbed designs + discussion)
- Changes additive (inserting sections/fields)
- Cross-file deps phase-ordered (can sequence edits)
- Content derivable (source material fully loaded)
- No implementation loops (prose edits, no test/build feedback)

Recommend: skip /runbook, execute directly from this outline with vet.
