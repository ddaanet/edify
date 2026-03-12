# Brief: Research Backlog

## Problem

Five deferred research tasks were consolidated from individual backlog items during prioritization (2026-03-06b, ranks 54-59). Each requires investigation before requirements can be written. Several now overlap with infrastructure built since consolidation.

## Scope

Research-only. Each sub-problem produces a report in `plans/reports/` with findings and a recommendation: proceed to requirements, absorb into existing plan, or close as resolved.

## Sub-problems

### SP-1: Ground State Coverage

**Question:** Which workflow state transitions are unmonitored? Where do agents lose track of pipeline state between skills?

**Expected output:** Gap analysis mapping state transitions to monitoring/enforcement mechanisms. Identify undefended transitions.

**Independence:** Overlaps significantly with system-property-tracing (system invariants as formal spec, enforcement matrix). May be fully absorbed — the traceability matrix in that plan's brief ("property -> enforcement mechanism -> verification method") is this investigation's output format.

**Status check:** system-property-tracing plan exists at `briefed` status. If that plan proceeds, SP-1 is redundant. Research value: confirm absorption or identify gaps the tracing plan misses.

### SP-2: Workflow Formal Analysis

**Question:** Do the workflow state machines (design -> runbook -> orchestrate -> inline) contain unreachable states, deadlocks, or missing transitions?

**Expected output:** State machine diagrams with analysis of each skill's state space. Identify structural defects vs documented limitations.

**Independence:** Adjacent to SP-1 but distinct focus. SP-1 asks "what's unmonitored?" SP-2 asks "is the state machine well-formed?" Also overlaps with system-property-tracing Phase 2 (pipeline traceability).

**Status check:** task-failure-lifecycle.md now formalizes the task state model (6 states, grounded in Temporal). continuation-passing.md formalizes skill chaining. Pipeline-contracts.md documents all transformations T1-T6.5. The state machines are more explicit than when this was filed. Formal analysis may now be tractable as a verification exercise rather than discovery.

### SP-3: Design-to-Deliverable Pipeline (restart required)

**Question:** Where does the design-to-deliverable pipeline lose context across session restarts? What information degrades at each boundary?

**Expected output:** Context-loss inventory per pipeline stage. Identify which losses are structural (no persistence mechanism) vs incidental (mechanism exists but isn't used).

**Independence:** Fully independent of SP-1/SP-2. Requires restart to investigate (the restart itself is the experimental condition).

**Status check:** Significant infrastructure built since filing. pipeline-contracts.md documents all stage I/O. Recall artifacts persist across restarts. Brief.md carries cross-tree context. task-context.sh recovers session history. The "loses context across restarts" framing may be partially stale — research should validate which losses persist after these additions.

### SP-4: Behavioral Design

**Question:** Are there established specification frameworks for agent behavioral directives? Current approach (prose fragments with anti-pattern/correct-pattern pairs) lacks formal rigor — is there prior art?

**Expected output:** Survey of behavioral specification approaches applicable to LLM agent directives. Assessment of whether current prose-fragment approach is adequate or should be formalized.

**Independence:** Fully independent. No overlap with other sub-problems. Distinct from system-property-tracing (which formalizes *what* properties to enforce, not *how* to specify agent behavior).

**Status check:** workflow-execution.md added a grounding requirement ("internal reasoning + learnings are insufficient for behavioral/design problems with published prior art"). This is a process rule, not a specification framework. SP-4 remains open — the question of whether prose fragments are the right representation is unresolved.

### SP-5: Compensate-Continue

**Question:** When a skill or agent is interrupted mid-execution, what recovery patterns exist beyond resume-or-restart?

**Expected output:** Survey of compensation patterns (saga, rollback, forward recovery) applicable to LLM agent workflows. Assessment of current coverage gaps.

**Independence:** Fully independent. Distinct domain from SP-1 through SP-4.

**Status check:** Multiple recovery mechanisms now exist: delegate-resume (agent-level, in delegation.md), task-failure-lifecycle (task-level, 6-state model), continuation-passing (skill chaining), escalation-acceptance (step-level rollback via git revert). error-classification.md mentions "compensate" as a failure response. The infrastructure has grown piecemeal — research value is now "are these mechanisms sufficient and coherent?" rather than "what patterns exist?"

## Success Criteria

- Each sub-problem has a research report in `plans/reports/`
- Reports include: findings, coverage of existing infrastructure, recommendation (proceed / absorb / close)
- SP-1 and SP-2 explicitly assess absorption into system-property-tracing
- SP-3 explicitly validates which context-loss scenarios survive current infrastructure
- SP-5 explicitly maps existing recovery mechanisms before identifying gaps

## References

- `plans/reports/prioritization-2026-03-06b.md` — WSJF scores (ranks 54-59)
- `plans/system-property-tracing/brief.md` — overlapping plan (invariants + traceability)
- `agents/decisions/pipeline-contracts.md` — pipeline stage documentation
- `agent-core/fragments/task-failure-lifecycle.md` — task state model
- `agent-core/fragments/continuation-passing.md` — skill chaining protocol
- `agent-core/fragments/delegation.md` — delegate resume pattern
- `agent-core/fragments/escalation-acceptance.md` — step-level rollback
- `agent-core/fragments/error-classification.md` — error taxonomy including compensation
