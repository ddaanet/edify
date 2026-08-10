# Execution Strategy: Three-Tier Model

Why execution has three tiers, what each tier means, and where the boundaries lie. Reference for `/design` skill (execution routing) and `/runbook` skill (tier assessment).

**Decision Date:** 2026-02-26

The three-tier execution structure (inline / delegate / orchestrate) is grounded in operational constraints of the execution environment — context window capacity, delegation overhead, and prompt generation cost. External methodology frameworks (Cynefin, XP, Lean Startup) validate the principle (match process weight to uncertainty); the specific tier structure derives from how the system actually executes work.

## When Choosing Execution Tier

**Tier 1 — Inline:** Work fits in the current session's context window. The agent that designed it has sufficient context to execute it. No delegation overhead needed. Boundary: edits and TDD cycles small enough that implementation + verification + review fit within one session's context budget.

**Tier 2 — Delegated:** Work exceeds inline capacity, but prompt generation is straightforward. The orchestrator writes prompts ad-hoc from design context and dispatches agents. Boundary: step count low enough that the orchestrator can hold full design context and generate prompts on the fly.

**Tier 3 — Orchestrated (Full Runbook):** Prompt generation itself becomes expensive. Many steps, layered context, cross-step dependencies. Pre-generating prompts as a runbook amortizes orchestration cost. Boundary: when steps have layered context, runbook generation is more efficient than direct prompt generation.

## When Tier Boundary Is Capacity vs Orchestration Complexity

| Boundary | Criterion | Mechanism |
|----------|-----------|-----------|
| Tier 1 → Tier 2 | **Capacity** — does the work fit inline? | Session context window is sufficient vs insufficient for implementation + verification |
| Tier 2 → Tier 3 | **Orchestration complexity** — can prompts be generated ad-hoc? | Direct prompt generation from design context vs pre-generated runbook with layered step context |

The Tier 1/2 boundary is about execution capacity. The Tier 2/3 boundary is about orchestration complexity — specifically, whether prompt generation for each step can happen ad-hoc or needs to be pre-computed.

## When Tier Thresholds Are Ungrounded

The specific thresholds currently used (Tier 1: <6 files, Tier 2: 6-15 files, Tier 3: >15 files; Tier 3: >10 TDD cycles) are **ungrounded operational parameters**. They have no empirical calibration data. The tier structure is justified; the thresholds within it need measurement.

Also ungrounded: mid-execution checkpoint frequency for delegated work ("every 3-5 cycles" in /runbook Tier 2). `/inline` deliberately omits mid-execution checkpoints to collect clean execution data — corrector serves as sole semantic review, post-step lint catches mechanical drift.

**Calibration data source:** `plans/reports/triage-feedback-log.md` — collects per-execution evidence (files changed, agent count, behavioral code, classification verdict). After sufficient executions, analyze: at what file/cycle counts did executions struggle? Did Tier 2 executions without checkpoints show compounding drift? The log + git history provide both signals.

## When Relating Execution Tiers to Complexity Routing

Complexity (Stacey axes) determines **design ceremony** — how much upfront analysis before implementation.

Work type (Production/Exploration/Investigation) determines **execution ceremony** — what quality obligations apply.

Execution tier determines **execution mechanics** — how the work is dispatched and supervised.

These are three independent decisions made at different pipeline stages:
1. Phase 0: Complexity classification → design ceremony
2. Phase 0: Work type classification → quality obligations
3. Phase B or `/runbook` entry: Tier assessment → execution mechanics

**Sources:**
- Complexity routing grounding report: `plans/reports/complexity-routing-grounding.md`
- Problem statement: `plans/complexity-routing/problem.md`
- User explanation during grounding discussion (2026-02-26 session)

## When Routing Prototype Work Through Pipeline

**Decision Date:** 2026-02-26

**Anti-pattern:** Design skill's behavioral-code gate routes ALL non-prose work to /runbook. /runbook tier assessment counts files against production conventions. A C-3 prototype script in plans/prototypes/ gets assessed as Tier 3. Procedural momentum from practiced pipeline overrides explicit prototype constraint.

**Correct pattern:** Artifact destination determines ceremony level. Prototype scripts (plans/prototypes/, one-off analysis, spikes) don't need runbooks, TDD, or test files. Design resolves complexity; post-design a prototype is direct implementation regardless of behavioral code.

## When Requirements-Clarity Gate Fires

**Decision Date:** 2026-02-27

**Data point:** /design Phase 0 correctly detected 5 mechanism-free open questions in `plans/triage-feedback/problem.md` and rerouted to /requirements. First empirical validation of the requirements-clarity gate — previously 0 events in n=38 sessions. Structured output block format was sufficient to trigger the correct routing decision without a full D+B tool-call anchor.
