# Brief: Quality Grounding

## Problem

High-leverage workflow skills (`/runbook`, corrector, design-corrector, `/orchestrate`, `/handoff`) contain ungrounded methodology claims. The workflow grounding audit (`plans/reports/workflow-grounding-audit.md`) inventoried provenance: 2 skills grounded, 3 partially grounded, 6 high-leverage skills ungrounded. `/design` has since been grounded (`plans/reports/design-skill-grounding.md`), leaving 5.

Separately, decision files and operational rules have accumulated content that may have drifted from their original evidence base, and prose quality directives use terms ("deslop", "framing", "hedging") without externally-validated definitions.

The no-confabulation rule (`agent-core/fragments/no-confabulation.md`) requires ungrounded claims be flagged. This plan executes that requirement systematically rather than ad hoc.

## Scope

Four sub-problems, consolidated from separate tasks during backlog prioritization (commit `21e0d899`). Each produces a grounding report via `/ground` skill execution.

**In scope:**
- Grounding workflow skills against external methodology
- Auditing decision file drift
- Grounding prose quality terminology
- Identifying safety review gaps from grounding findings

**Out of scope:**
- `/design` — already grounded and redesigned
- Low-benefit skills (`/commit`, artisan, test-driver, `/shelve`, `/reflect`, tdd-auditor, runbook-simplifier) — classified as low grounding benefit in audit
- System invariant specification — belongs to system-property-tracing plan (which partially absorbs this plan's "are claims grounded" question but at a different level: specification of what properties hold, vs grounding of how methodology is sourced)

## Sub-problems

### SP-1: Ground workflow skills

Ground remaining high-leverage ungrounded skills against external methodology sources. Per the audit's priority order:
- `/runbook` — three-tier model and testing strategy are project-invented
- Review agents (corrector + design-corrector) — share review methodology, batch together
- `/orchestrate` — weak orchestrator pattern is project-invented
- `/handoff` — session continuity methodology

Each skill gets a `/ground` execution producing a grounding report with provenance classification (grounded / partially grounded / ungrounded with source).

**Independent of other sub-problems.** Can execute in any order. Largest sub-problem by volume.

### SP-2: Decision drift audit (EXTRACTED — separate plan)

**Extracted to:** `plans/decision-drift-audit/brief.md`. Independent sub-problem, split pre-design during /proof review (2026-03-12).

### SP-3: Prose gate terminology

The term "deslop" and related prose quality concepts ("framing", "hedging", D+B pattern naming) are used in operational directives without external grounding. Find proper terminology from writing quality, technical communication, or LLM evaluation literature. Update docs if better terms exist; flag as project-specific if no external equivalent.

D+B ("Deterministic + Behavioral") anchors are used across 10+ skill files as a structural pattern name. The name is project-invented — ground or acknowledge.

**Independent of SP-1 and SP-2.** Smallest sub-problem. Could be a single `/ground` execution.

### SP-4: Safety review expansion

Assess whether grounding findings from SP-1 reveal safety review coverage gaps. This is derivative — it consumes SP-1 outputs and identifies risks that current review agents don't check.

**Depends on SP-1.** Must run after SP-1 completes. Scope is bounded by what SP-1 discovers.

## Dependencies

- **SP-1, SP-2, SP-3:** Independent of each other. Parallelizable.
- **SP-4:** Depends on SP-1 output.
- **system-property-tracing:** That plan partially absorbs this plan's concerns at a higher abstraction level (invariant specification subsumes "are claims grounded"). The two are complementary: this plan grounds specific methodology claims; that plan builds a framework for tracking which properties are defended. Neither blocks the other.
- **`/ground` skill:** Required for SP-1 and SP-3 execution. Exists and is operational.

## Success Criteria

- Each high-leverage ungrounded skill (SP-1) has a grounding report with sources, following the format established by `plans/reports/design-skill-grounding.md`
- Decision files audited (SP-2) with stale/drifted claims flagged and either updated or marked "ungrounded — needs validation"
- Prose quality terms (SP-3) either mapped to external terminology or explicitly acknowledged as project-specific
- Safety gaps identified (SP-4) from grounding findings, with recommendations for review agent updates

## Post-Design Convention

After design phase, split independent sub-problems into separate tasks with explicit dependencies. Parent plan delivers at "designed" status (terminal). Children are new plans starting at "planned." SP-1, SP-2, SP-3 are independent and split post-design. SP-4 depends on SP-1.

## References

- Workflow grounding audit: `plans/reports/workflow-grounding-audit.md`
- Design skill grounding (completed): `plans/reports/design-skill-grounding.md`
- Ground skill research: `plans/reports/ground-skill-research-synthesis.md`
- No-confabulation rule: `agent-core/fragments/no-confabulation.md`
- System property tracing (related): `plans/system-property-tracing/brief.md`
