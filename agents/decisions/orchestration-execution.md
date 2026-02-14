# Orchestration Execution Patterns

Patterns for delegation, orchestration protocol, model selection, and execution-time practices.

## .Delegation Execution

### When Delegation Requires Commit Instruction

**Decision Date:** 2026-02-12

**Anti-pattern:** Agent writes artifact, returns filepath, leaves tree dirty.

**Correct pattern:** Include explicit "commit your output before returning" in every delegation prompt.

**Root cause:** Agents optimize for the stated task; cleanup is not implied. Vet-fix-agent especially frequent offender.

### When Context Defines Scope Boundary

**Decision Date:** 2026-02-12

**Anti-pattern:** Full context + "Execute ONLY this step" prose → agents violate.

**Correct pattern:** Give executing agent step + design + outline only. Scope enforced structurally by context absence.

**Rationale:** Executing agents don't get other step files — can't scope-creep. Phase context injected only at feedback points (vet-fix-agent) for alignment checking.

### When Deduplicating Delegation Prompts

**Decision Date:** 2026-02-12

**Decision:** Write shared content to a file, reference path in prompts.

**Anti-pattern:** Repeating boilerplate in each parallel agent prompt — bloats orchestrator context.

**Benefit:** Orchestrator context doesn't grow N× for N parallel dispatches.

### When Managing Orchestration Context

**Decision Date:** 2026-02-12

**Decision:** Handoff is NOT delegatable — it requires current agent's session context. Commit is mechanical, can delegate.

**Correct pattern:** Plan for restart boundary: planning → restart → execution (different sessions, different model tiers).

### When No Post-Dispatch Communication Available

**Decision Date:** 2026-02-12

**Anti-pattern:** Launch agent, then try to adjust scope mid-flight via resume.

**Correct pattern:** Partition scope completely before launch — no mid-flight messaging available.

**Consequence:** Over-scoped agents waste work, under-scoped agents miss context — partitioning is one-shot.

## .Orchestration Protocol

### When Running Post-Step Verification

**Decision Date:** 2026-02-12

**Decision:** After each step: git status → if dirty, resume agent or vet-fix to commit → grep UNFIXABLE in vet reports.

**Anti-pattern:** Trust agent completion report without verification.

**Rationale:** Clean tree is hard requirement, no exceptions.

### When Planning Is Parallelizable

**Decision Date:** 2026-02-12

**Decision:** Planning phases decompose into independent delegations. Phase expansions are fully parallel — all read same inputs (design + outline), write different files.

**Evidence:** 8 concurrent sonnet agents produced correct output; git handled concurrent commits.

**Constraint:** Per-phase review needs full outline context. Holistic review runs once after all phases complete.

## .Model Selection Patterns

### When Stabilizing Orchestrator Model

**Decision Date:** 2026-02-12

**Decision:** Stabilize with sonnet orchestrator, optimize to haiku once patterns are proven and failure modes understood.

**Anti-pattern:** Default to haiku for cost savings before patterns validated.

**Key insight:** Model tier is a configurable knob, not an architectural constraint.

### When Using Opus For RCA Delegation

**Decision Date:** 2026-02-12

**Decision:** Use opus for RCA Task agents. Opus first-pass ≈ sonnet + one deepening round.

**Key delta:** Opus reads actual artifacts where sonnet trusts summarized descriptions.

**Cost:** ~30% more tokens per agent, but eliminates orchestrator deepening round.

### When Sonnet Inadequate For Synthesis

**Decision Date:** 2026-02-12

**Decision:** Use opus for extracting/synthesizing requirements from nuanced multi-turn discussions.

**Rationale:** Sonnet misses implicit requirements in moderately complex conversations.

### When No Model Tier Introspection Available

**Decision Date:** 2026-02-12

**Decision:** Don't guess model tier. Ask, stay silent about it, or rely on external signal (hook).

**Rationale:** No introspection API; agent consistently misidentifies as sonnet when running as opus.

## .Scripting Principles

### When Always Scripting Non-Cognitive Solutions

**Decision Date:** 2026-02-12

**Decision:** If solution is non-cognitive (deterministic, pattern-based), script it. Always auto-fix when possible.

**Anti-pattern:** Using agent judgment for deterministic operations.

**Corollary:** Reserve agent invocations for cognitive work (design, review, ambiguous decisions).

### When Script Validates It Should Generate

**Decision Date:** 2026-02-12

**Anti-pattern:** Script validates metadata presence but expects cognitive agent to generate it.

**Correct pattern:** If metadata is deterministic and standard, script injects it during assembly.

### When Bootstrapping Around Broken Tools

**Decision Date:** 2026-02-12

**Decision:** When replacing a workflow tool, assess tier from design and execute directly if feasible.

**Key insight:** The design document IS the execution plan when work is well-specified.

## .TDD Quality Patterns

### When Assessing RED Pass Blast Radius

**Decision Date:** 2026-02-12

**Decision:** When unexpected RED pass occurs, run blast radius across all remaining phase cycles.

**Classification:** over-implementation (commit test, skip GREEN), test flaw (rewrite assertions), correct (proceed).

**Critical finding:** Test flaws are deliverable defects — feature silently skipped when test passes for wrong reason.

### When Unifying Over Patching

**Decision Date:** 2026-02-12

**Decision:** When >50% of code is shared and gaps trace to a bifurcation itself, unify first.

**Rationale:** Patches add complexity to maintain; unification removes root cause.

## .Agent Context Patterns

### When Common Context Competes With Step

**Decision Date:** 2026-02-12

**Decision:** Common context must be phase-neutral (project conventions, package structure). Phase-specific paths belong in cycle step files only.

**Rationale:** Persistent common context is stronger signal than one-time step file input. At haiku capability, persistent signal wins.

### When Capturing Requirements From Conversation

**Decision Date:** 2026-02-12

**Decision:** Primary mode is conversation-to-artifact capture; elicitation is secondary mode for cold-start.

**Rationale:** User's actual need was "formalize what we just discussed" not "guide me through questions".
