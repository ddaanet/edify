# Brief: Research Backlog

## Problem

Five deferred research tasks were consolidated from individual backlog items during prioritization (2026-03-06b, ranks 54-59). Each requires investigation before requirements can be written. Several now overlap with infrastructure built since consolidation.

## Scope

Research-only. Each sub-problem produces a report in `plans/reports/` with findings and a recommendation: proceed to requirements, absorb into existing plan, or close as resolved.

## Sub-problems

### SP-1: Ground State Coverage (KILL — absorbed)

**Absorbed into:** system-property-tracing. Workflow state coverage is a system property — the traceability matrix in that plan's brief is this investigation's output format. Workflow closure documented as explicit invariant candidate.

### SP-2: Workflow Formal Analysis (KILL — absorbed)

**Absorbed into:** system-property-tracing. State machine verification is a verification exercise within that plan's framework.

### SP-3: Design-to-Deliverable Pipeline (KILL — absorbed)

**Absorbed into:** system-property-tracing as grounding input. Context loss across session boundaries is a system property ("pipeline preserves context"). Historical evaluation of delivery failures (including deliverable-review corrections) provides grounding evidence for that invariant.

### SP-4: Behavioral Design

**Question:** Are there established specification frameworks for agent behavioral directives? Current approach (prose fragments with anti-pattern/correct-pattern pairs) lacks formal rigor — is there prior art?

**Expected output:** Survey of behavioral specification approaches applicable to LLM agent directives. Assessment of whether current prose-fragment approach is adequate or should be formalized.

**Independence:** Fully independent. No overlap with other sub-problems. Distinct from system-property-tracing (which formalizes *what* properties to enforce, not *how* to specify agent behavior).

**Status check:** workflow-execution.md added a grounding requirement ("internal reasoning + learnings are insufficient for behavioral/design problems with published prior art"). This is a process rule, not a specification framework. SP-4 remains open — the question of whether prose fragments are the right representation is unresolved.

### SP-5: Degraded-Function Protocol (REVISED — was Compensate-Continue)

**Question:** When existing prose or tools are found defective, how should the system formalize degraded function while the fix is built?

**Expected output:** Degraded-function protocol — how to formally mark components as defective, activate fallback behavior, and track resolution. Grounded against compensation/saga patterns from distributed systems literature.

**Independence:** Fully independent. Distinct domain from SP-4.

**Status check:** Multiple recovery mechanisms exist piecemeal (delegate-resume, task-failure-lifecycle, continuation-passing, escalation-acceptance). No protocol for operating in degraded mode when a component is known-defective. Current practice is ad hoc (disable, work around, add blocker note).

## Success Criteria

- SP-1, SP-2, SP-3: absorbed into system-property-tracing (no standalone deliverables)
- SP-4: research report in `plans/reports/` with findings and recommendation
- SP-5: degraded-function protocol specification, grounded against distributed systems literature

## Post-Design Convention

After design phase, split independent sub-problems into separate tasks. SP-4 and SP-5 are independent — split post-design.

## References

- `plans/reports/prioritization-2026-03-06b.md` — WSJF scores (ranks 54-59)
- `plans/system-property-tracing/brief.md` — overlapping plan (invariants + traceability)
- `agents/decisions/pipeline-contracts.md` — pipeline stage documentation
- `agent-core/fragments/task-failure-lifecycle.md` — task state model
- `agent-core/fragments/continuation-passing.md` — skill chaining protocol
- `agent-core/fragments/delegation.md` — delegate resume pattern
- `agent-core/fragments/escalation-acceptance.md` — step-level rollback
- `agent-core/fragments/error-classification.md` — error taxonomy including compensation
