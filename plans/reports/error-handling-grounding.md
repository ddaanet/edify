# Error Handling Framework Grounding Report

**Grounding:** Moderate — 5 established frameworks found with partial applicability. Outline patterns operationally sound but taxonomically imprecise. Several gaps where established frameworks improve the design.

---

## Research Foundation

### Established Frameworks Examined

**1. Avižienis Fault-Error-Failure (FEF) Chain** (2004)
The canonical dependability taxonomy. Defines a causal chain: **fault** (adjudged cause) → **error** (state deviation) → **failure** (service deviation). Four means to attain dependability: prevention, tolerance, removal, forecasting. Six attributes: availability, reliability, safety, integrity, maintainability, confidentiality.

**2. Saga Pattern / Compensating Transactions** (Microsoft Azure Architecture)
Distributed transaction management via sequence of local transactions + compensating transactions for rollback. Key concepts: compensable transactions (undoable), pivot transactions (point of no return), retryable transactions (idempotent, post-pivot). Two approaches: orchestration (centralized controller) and choreography (event-driven).

**3. MASFT — Multi-Agent System Failure Taxonomy** (Cemri et al., 2025)
14 failure modes across 3 categories from empirical study of multi-agent LLM systems (Cohen's κ = 0.88):
- FC1: Specification and System Design Failures (5 modes)
- FC2: Inter-Agent Misalignment (6 modes)
- FC3: Task Verification and Termination (3 modes)

**4. Temporal Workflow Orchestration**
Durable workflow execution with activity-level retry, non-retryable error classification, saga compensation, error wrapping/propagation across workflow layers. Key distinction: retryable (transient) vs non-retryable (deterministic) failures at each activity level.

**5. LLM Agentic Failure Archetypes** (arxiv 2512.07497)
Four recurring archetypes: premature action without grounding, over-helpfulness under uncertainty, context pollution vulnerability, fragile execution under cognitive load. Key finding: superior models win through recovery capability, not error avoidance.

---

## Framework Mapping

### Outline Claim 1: 4-Category Error Taxonomy

**Outline:** Prerequisite Failure, Execution Error, Unexpected Result, Ambiguity Error.

**FEF chain gap:** The outline conflates faults and failures. In Avižienis:
- "Prerequisite Failure" is a **fault** (missing resource causes error)
- "Execution Error" is a **failure** (service deviated from specification)
- "Unexpected Result" is a **failure** (output deviates from spec)
- "Ambiguity Error" is a **fault** (specification defect)

The 4 categories mix two levels of the causal chain. This matters because the appropriate response differs:
- **Faults** (prerequisite, ambiguity) → prevention-oriented response (validate before execution, clarify spec)
- **Failures** (execution error, unexpected result) → tolerance-oriented response (retry, escalate, compensate)

**MASFT gap:** The outline ignores FC2 (Inter-Agent Misalignment) entirely — yet MASFT found this is the dominant failure category in multi-agent systems. Relevant failure modes for this project:
- FM-2.3 Task derailment (agent deviates from objectives)
- FM-2.5 Ignored other agent's input (disregarding instructions)
- FM-2.6 Reasoning-action mismatch (disconnect between logic and execution)

These are real failure modes in the existing system (vet over-escalation, agent confabulation) but the taxonomy has no category for them.

**Recommendation:** Either restructure as a fault-error-failure chain (significant redesign) or add an explicit "Inter-Agent Misalignment" category to capture FM-2.3/2.5/2.6 failures alongside the existing 4 categories.

### Outline Claim 2: 5-Layer Architecture

**Outline:** Taxonomy → Orchestration → Task Lifecycle → CPS Chains → Documentation, ordered by implementation dependency.

**Avižienis mapping:**
| Outline Layer | Avižienis Means |
|---|---|
| Error taxonomy (L1) | Fault forecasting (classification enables prediction) |
| Orchestration hardening (L2) | Fault tolerance (escalation, retry, rollback) |
| Task failure lifecycle (L3) | Fault tolerance (state machine records failures) |
| CPS chain recovery (L4) | Fault tolerance (abort-and-record) |
| Documentation (L5) | Fault removal (reduce errors through better docs) |

**Gap:** No layer maps to **fault prevention**. The existing prerequisite-validation.md pattern IS prevention but isn't represented in the 5-layer architecture. Prevention is arguably the most cost-effective means (catches ~80% of errors per internal inventory). It should be a layer or explicitly noted as foundational.

**Assessment:** The layering is project-specific organization, not a universal framework. This is fine — but the outline presents it without acknowledging the organizational choice. The dependency ordering (taxonomy first, then independent subsystems, then consolidation) is sound.

### Outline Claim 3: Task Lifecycle States

**Outline:** `[ ]` pending, `[>]` in-progress, `[x]` complete, `[!]` blocked, `[✗]` failed.

**Temporal mapping:**
| Outline State | Temporal Equivalent | Notes |
|---|---|---|
| `[ ]` pending | Scheduled | — |
| `[>]` in-progress | Running | — |
| `[x]` complete | Completed | — |
| `[!]` blocked | Waiting on signal | Temporal supports external signals to unblock |
| `[✗]` failed | Failed | Terminal in both |
| — | Canceled | Not in outline (user-initiated abort) |
| — | TimedOut | Not in outline |
| — | ContinuedAsNew | Not applicable |

**Assessment:** Well-grounded. The 5 states are a reasonable subset of Temporal's workflow execution states. Missing "Canceled" (user abandons task) and "TimedOut" (task exceeds time limit) — both noted as open questions in the outline.

**Recommendation:** Consider adding `[–]` canceled as distinct from failed (user-initiated vs system-detected). Timeout could be a trigger for failed rather than a separate state.

### Outline Claim 4: Rollback = Revert to Step Start (D-5)

**Saga pattern mapping:** Compensating transactions are more nuanced than simple state restoration:
- Compensating transactions undo *effects*, not necessarily restore *state*
- They must account for concurrent modifications
- They may not follow exact reverse order
- Idempotency is required for compensation steps

**Git simplification:** The outline's approach works specifically because:
1. Git commits are atomic snapshots (entire tree state captured)
2. No concurrent modifications within a single orchestration run
3. Reverting a commit IS restoring state (not just compensating for effects)
4. Git revert is inherently idempotent

**Assessment:** Sound *for this system* because git provides atomic snapshots. The outline should acknowledge this is a simplification enabled by git's snapshot model. The Saga pattern's more complex compensation mechanics (reverse order, idempotency, concurrent access) don't apply here because the orchestrator is single-threaded and git provides atomicity.

**Recommendation:** Document the git-atomic-snapshot assumption explicitly. If the system ever needs rollback for non-git state (e.g., external service calls, session.md edits not yet committed), the simple revert model breaks.

### Outline Claim 5: CPS Abort-and-Record (D-1)

**Temporal mapping:** Maps to "non-retryable failure with state recording for manual intervention." Temporal distinguishes:
- **Retryable:** transient failures, activity retried with backoff
- **Non-retryable:** deterministic failures, activity fails permanently, workflow must handle

**Gap:** The outline treats all CPS failures as non-retryable (abort remaining chain). Some failures in the CPS chain could be transient:
- Hook timeout during `/handoff` → retryable (retry the skill)
- Missing file during `/commit` → non-retryable (requires user action)
- Session.md write conflict → retryable (re-read and retry)

**Recommendation:** Classify CPS failures as retryable or non-retryable before deciding to abort. Abort-and-record is correct for non-retryable; retry-with-backoff is more appropriate for transient failures.

### Outline Claim 6: Escalation Acceptance Criteria (D-3)

**Outline:** Three criteria required: (a) `just dev` passes, (b) git tree clean, (c) output validates against step acceptance criteria.

**Temporal mapping:** This is a verification activity pattern — define measurable health checks after recovery. Standard in workflow orchestration.

**Saga pattern mapping:** Maps to "retryable transactions are idempotent" — the acceptance check verifies the system reached a consistent state after recovery.

**Assessment:** Operationally sound. The three criteria provide measurable, mechanical verification.

---

## Adaptations

### From Avižienis: Fault-Error-Failure Vocabulary

The outline uses "error" loosely to mean any undesirable event. Adopting FEF vocabulary doesn't require restructuring the taxonomy, but would improve precision:
- Call prerequisite/ambiguity issues **faults** (they're causes)
- Call execution/unexpected result issues **failures** (they're observed deviations)
- Reserve **error** for the intermediate state (e.g., agent holds incorrect variable, wrong file read)

This is a vocabulary improvement, not a structural change.

### From MASFT: Inter-Agent Misalignment Category

The outline's biggest gap. Add consideration of:
- Agent deviates from task specification (FM-1.1 / FM-2.3)
- Agent ignores provided context (FM-2.5)
- Reasoning-action mismatch (FM-2.6) — agent reasons correctly but acts differently
- Premature termination (FM-3.1) — agent stops before objectives met
- Incomplete verification (FM-3.2) — agent declares success without checking

These are empirically the dominant failure modes in multi-agent LLM systems and already observed in this project (vet confabulation, over-escalation, agent skipping steps).

### From Saga Pattern: Pivot Transaction Concept

The CPS chain has implicit pivot points. After `/orchestrate` completes execution, compensation (undoing all implementation) is impractical. The outline should identify pivot transactions in the CPS chain — points after which abort-and-record is the only option because compensation is too costly.

### From Temporal: Retryable vs Non-Retryable

Apply to all three subsystems, not just CPS:
- **Orchestration:** Some step failures are retryable (transient env issue) vs non-retryable (design flaw)
- **Task lifecycle:** Blocked tasks are "waiting for signal" (retryable); failed tasks are non-retryable
- **CPS:** Distinguish transient (hook timeout) from deterministic (missing file)

### Deliberately Excluded

- **Avižienis safety/confidentiality attributes:** Not applicable to LLM agent workflows
- **Saga choreography approach:** System uses orchestration pattern exclusively
- **Temporal durable execution:** Requires runtime infrastructure changes beyond scope
- **MASFT data anomaly countermeasures** (semantic locks, commutative updates): Applies to concurrent multi-agent writes, not relevant to single-orchestrator pattern

---

## Grounding Assessment

**Quality label: Moderate**

**Evidence basis:**
- 5 established frameworks examined (FEF, Saga, MASFT, Temporal, LLM agentic failures)
- Partial applicability: FEF vocabulary and MASFT categories directly improve the outline; Saga and Temporal patterns validate existing decisions with suggested refinements
- The outline's core architecture (subsystem-based layers, git-atomic rollback, weak orchestrator escalation) is not derived from any single framework but is a reasonable project-specific synthesis

**Searches performed:**
- "error handling framework multi-agent orchestration systems fault tolerance taxonomy"
- "workflow orchestration error recovery patterns rollback compensating transactions state machine"
- "LLM agent error handling patterns failure recovery autonomous agents"
- "error taxonomy classification framework distributed systems established methodology"
- "Temporal workflow orchestration error handling retry compensation activity failure"

**Gaps remaining:**
- No framework specifically addresses "LLM agent orchestration via markdown-based runbooks with git as state store" — the combination is novel
- The inter-agent misalignment category (MASFT FC2) needs empirical validation against this system's actual failure data
- Timeout handling has no grounded recommendation — per-step vs per-runbook remains an open design question

---

## Specific Outline Corrections Needed

### Must Fix (established frameworks contradict outline)

1. **Add inter-agent misalignment to error taxonomy** — MASFT's dominant failure category is absent. The project already experiences these failures (confabulation, over-escalation, step skipping).

2. **Distinguish retryable from non-retryable** across all subsystems — Temporal's fundamental distinction is missing. Currently all failures are treated as "escalate or stop."

3. **Acknowledge git-atomic-snapshot assumption** in rollback strategy — The simple revert model depends on git providing atomicity. If non-git state is ever involved, the model breaks.

### Should Fix (established frameworks improve outline)

4. **Adopt fault/failure vocabulary** — FEF chain terminology adds precision without restructuring. Prerequisite and ambiguity are faults; execution and unexpected result are failures.

5. **Add fault prevention as explicit layer or foundation** — Avižienis's four means include prevention, which is the existing prerequisite-validation pattern. Currently absent from the 5-layer architecture.

6. **Identify pivot transactions in CPS chains** — Saga pattern's pivot concept applies: after orchestration completes, compensation is impractical. Record these points.

7. **Add idempotency requirement for recovery operations** — Standard in Saga/Temporal patterns. The outline's acceptance criteria verify state but don't require idempotent recovery steps.

### Consider (project-specific extensions of frameworks)

8. **Add "Canceled" task state** — Temporal includes this; distinct from "Failed" (user choice vs system detection).

9. **Map vet over-escalation to MASFT FM-2.6** (reasoning-action mismatch) — provides framework for understanding and mitigating a known problem.

10. **Recovery capability > error avoidance** — LLM agentic failure research shows superior models win through recovery, not prevention. The outline's emphasis on escalation and acceptance criteria aligns with this finding.

---

## Sources

### Primary (Framework Originators)
- [Avižienis et al. — Basic Concepts and Taxonomy of Dependable and Secure Computing (2004)](https://www.landwehr.org/2004-aviz-laprie-randell.pdf) — Fault-error-failure chain, dependability means, canonical taxonomy
- [Microsoft Azure — Saga Design Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga) — Compensating transactions, orchestration vs choreography, pivot transactions
- [Microsoft Azure — Compensating Transaction Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) — Rollback mechanics, idempotency requirements, when to compensate vs retry
- [Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (2025)](https://arxiv.org/html/2503.13657v1) — MASFT: 14 failure modes, 3 categories, empirical validation (κ=0.88)

### Secondary (Practice Patterns, Analysis)
- [LLM Agentic Failure Taxonomy (2024)](https://arxiv.org/html/2512.07497v2) — Four failure archetypes, recovery > avoidance finding
- [Temporal Error Handling in Practice](https://www.flightcontrol.dev/blog/temporal-error-handling-in-practice) — Retryable vs non-retryable, activity-level retry, error wrapping
- [Temporal Workflow Orchestration (2026)](https://james-carr.org/posts/2026-01-29-temporal-workflow-orchestration/) — Durable execution, saga compensation
- [Orkes — Compensation Transaction Patterns](https://orkes.io/blog/compensation-transaction-patterns/) — Practical compensation implementation
- [Towards Data Science — Why Your Multi-Agent System is Failing](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/) — 17x error amplification, coordination topology
- [Augment Code — Why Multi-Agent LLM Systems Fail](https://www.augmentcode.com/guides/why-multi-agent-llm-systems-fail-and-how-to-fix-them) — Practical mitigation strategies
