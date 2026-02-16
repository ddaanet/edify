# Design Outline: Error Handling Framework

## Problem Statement

Error handling is fragmented across three subsystems — each with ad-hoc patterns, inconsistent semantics, and gaps:

1. **Runbook orchestration** — Has escalation levels and dirty-tree checks but no rollback strategy, no escalation acceptance criteria, no timeout handling
2. **Task lifecycle** — Only pending/in-progress/complete states. No blocked/failed states, no error recording
3. **CPS skill chains** — Five cooperative skills chain via tail-calls with zero error handling. Chain failure = orphaned continuation, stale session state

The existing `error-handling.md` fragment covers only "don't suppress errors." The `error-classification.md` fragment covers orchestration-only taxonomy. Neither addresses cross-system error propagation.

See `plans/error-handling/reports/explore-error-handling.md` for detailed gap analysis.
See `plans/reports/error-handling-grounding.md` for grounding against established frameworks (Avižienis FEF, Saga pattern, MASFT, Temporal).

## Approach

Unify error handling into a layered framework that respects existing patterns while filling gaps:

**Layer 0: Fault prevention** — Prerequisite validation before execution (existing pattern, ~80% of errors caught early). Foundation for all other layers.
**Layer 1: Error taxonomy** — Extend existing 4-category classification to cover all subsystems. Add fault/failure vocabulary (Avižienis) and inter-agent misalignment category (MASFT). Distinguish retryable from non-retryable failures (Temporal).
**Layer 2: Orchestration hardening** — Escalation acceptance criteria, rollback strategy, timeout handling
**Layer 3: Task failure lifecycle** — Add blocked/failed/canceled states to session.md task notation
**Layer 4: CPS chain error recovery** — Define what happens when a skill fails mid-chain. Classify as retryable or non-retryable before aborting. Identify pivot transactions (points of no return).
**Layer 5: Documentation consolidation** — Merge scattered error patterns into coherent framework

Layers are ordered by implementation dependency: prevention and taxonomy provide foundation, orchestration and task are independent, CPS builds on task states, documentation consolidates all.

**Grounding note:** This layering is project-specific organization (by subsystem), not a claim about universal error handling architecture. The layer structure is adapted from Avižienis's four means to attain dependability: prevention (L0), tolerance (L2-L4), removal (vet reviews, existing), forecasting (L1 taxonomy enables prediction).

## Key Decisions

**D-1: CPS error propagation model** — When a skill fails mid-chain, classify as retryable (transient: hook timeout, write conflict) or non-retryable (deterministic: missing file, design flaw). Non-retryable: abort remaining continuation and record in session.md Blockers section for manual resume. Retryable: retry the failed skill once before aborting. The orphaned continuation is recorded with error context so `r` (resume) can pick up from the failed skill. Identify pivot transactions in the chain — after `/orchestrate` completes, compensation is impractical (Saga pattern concept).

**D-2: Task failure notation** — Add `- [!]` (blocked), `- [✗]` (failed), and `- [–]` (canceled) states to session.md. All include reason text. Blocked transitions back to pending when unblocked; failed is terminal (requires user decision to retry or abandon); canceled is user-initiated abort (distinct from system-detected failure). State model grounded in Temporal's WorkflowExecutionStatus (Running, Completed, Failed, Canceled, TimedOut).

**D-3: Escalation acceptance criteria** — Define per-error-type what "fixed" means: (a) `just dev` passes, (b) git tree clean, (c) output validates against step acceptance criteria. All three criteria are required for successful escalation resolution.

**D-4: Fragment allocation strategy** — Create targeted fragments for new subsystems (task failure lifecycle, escalation acceptance). Extend existing fragments only where natural fit (CPS error recovery → `continuation-passing.md`). Don't force extensions into minimalist fragments (`error-handling.md` is 12 lines by design).

**D-5: Rollback is "revert to step start"** — When escalation fails partway through a step, revert to the last clean commit before that step. Don't attempt partial undo. This is a simplification of the Saga compensating transaction pattern, enabled by git's atomic snapshot model: reverting a commit IS restoring state (no concurrent modifications within single orchestration). **Assumption:** All relevant state is git-managed. If non-git state is involved (external service calls, unreachable session.md edits), the simple revert model breaks.

**D-6: Hook error protocol** — Hook failures should be visible (stderr output) but non-fatal for the session. CPS hook already silently catches errors; formalize this as intentional degraded mode. Document expected behavior for hook crash, timeout, and invalid output.

## Open Questions

- Should orchestrator timeout be configurable per-step or per-runbook? (Per-step is more flexible but adds complexity to orchestrator plan format. No grounded recommendation found — Temporal uses per-activity timeouts.)
- Should `- [✗]` (failed) and `- [–]` (canceled) tasks be auto-cleaned on handoff, or persist until user explicitly removes them? (Persistence maintains audit trail but clutters session.md over time.)
- How many retries for retryable CPS failures before escalating? (Temporal defaults to unlimited with exponential backoff; our interactive context suggests 1 retry max.)

## Scope Boundaries

**In scope:**
- CPS chain error recovery protocol (continuation-passing.md update)
- Task lifecycle error states (session.md notation, handoff skill update)
- Orchestration escalation hardening (orchestrate skill update, acceptance criteria)
- Error taxonomy extension (error-classification.md update)
- error-handling.md consolidation (cross-system patterns)

**Out of scope:**
- Hook system architecture changes (Claude Code internals, not modifiable). Hook error *protocol* (stderr visibility, degraded mode) IS in-scope as D-6.
- Agent crash recovery automation (workaround exists: `run_in_background=true`)
- Vet over-escalation pattern library (optimization, not framework)
- Prerequisite validation enforcement in tooling (script change to plan-reviewer, separate task)

## Architecture

### Three Subsystems

**1. Runbook Orchestration (Layer 2)**
- Escalation flow: Agent → Haiku orchestrator → Sonnet diagnostic → User
- Error classification at agent level using 4-category taxonomy
- Acceptance criteria for escalation resolution (dev passes, tree clean, output validates)
- Rollback strategy: revert to last clean commit before failed step
- Timeout handling with configurable limits per step or runbook

**2. Task Lifecycle (Layer 3)**
- Extended state notation: `[ ]` pending, `[>]` in-progress, `[x]` complete, `[!]` blocked, `[✗]` failed, `[–]` canceled
- State transitions: pending → in-progress → (complete | blocked | failed | canceled)
- Blocked = waiting on signal (Temporal concept); transitions back to pending when unblocked
- Failed = terminal, system-detected; requires user decision to retry or abandon
- Canceled = terminal, user-initiated; distinct from failed (choice vs detection)
- Error context recorded inline with task notation
- Grounded in Temporal WorkflowExecutionStatus (subset: Running, Completed, Failed, Canceled, TimedOut)

**3. CPS Skill Chains (Layer 4)**
- Continuation passing via hook injection + skill tail-calls
- Error classification: retryable (hook timeout, write conflict) vs non-retryable (missing file, design flaw)
- Retryable: retry failed skill once before aborting
- Non-retryable: abort remaining continuation, record in session.md Blockers section
- Pivot transactions: after `/orchestrate` completes execution, compensation is impractical (Saga pattern). Record these points-of-no-return in the chain.
- Manual resume via `r` command from recorded error context
- Recovery operations must be idempotent (Saga/Temporal requirement)

### Error Taxonomy (Layer 1)

Existing 4-category classification extended with grounding from established frameworks:

**Fault/failure vocabulary (Avižienis FEF chain):**
- Categories 1 and 4 are **faults** (causes): prerequisite = environment fault, ambiguity = specification fault
- Categories 2 and 3 are **failures** (observations): execution error = service deviation, unexpected result = output deviation
- Response differs: faults → prevention-oriented (validate, clarify); failures → tolerance-oriented (retry, escalate, compensate)

**Retryable vs non-retryable (Temporal):**
- Each failure classified as retryable (transient: env issue, timeout, write conflict) or non-retryable (deterministic: missing file, design flaw, spec ambiguity)
- Retryable → retry with backoff before escalating. Non-retryable → escalate immediately.

**Category 5: Inter-agent misalignment (MASFT FC2)** — Agent deviates from specification, ignores provided context, reasoning-action mismatch, premature termination, incomplete verification. Empirically the dominant failure category in multi-agent LLM systems. Already observed in this project: vet confabulation, over-escalation, agent skipping steps.

### Error Flow

```
Agent executes → Error occurs → Classify (5 categories) → Retryable?
  ↓                                                          ↓
  ↓                                              Yes: Retry with backoff
  ↓                                              No: Escalate
  ↓
Orchestrator receives error → Check acceptance criteria
  ↓
If fixable: Sonnet diagnostic → Apply fix → Verify acceptance → Retry step
If not fixable: Record in session.md → Escalate to user
  ↓
User resolves → Manual resume from recorded context
```

### Integration Points

- **Taxonomy (Layer 1)** provides error categories for all three subsystems
- **Task states (Layer 3)** used by CPS chains to record blocked/failed continuations
- **Orchestration acceptance (Layer 2)** defines verification protocol reused in CPS skill error handling
- **Documentation (Layer 5)** consolidates patterns from all subsystems into unified fragments

## Implementation Plan

### Phase 0: Prevention (Layer 0)
- Document prerequisite validation as explicit error prevention layer
- Reference existing `prerequisite-validation.md` patterns
- Establish prevention-first principle across all subsystems

### Phase 1: Foundation (Layer 1)
- Extend `error-classification.md` with fault/failure vocabulary (Avižienis FEF chain)
- Add 5th category: inter-agent misalignment (from MASFT FC2)
- Add retryable vs non-retryable distinction per category (Temporal pattern)
- Update agent-level classification decision tree for all 5 categories

### Phase 2: Orchestration (Layer 2)
- Create `escalation-acceptance.md` fragment defining success criteria
- Update `orchestrate/SKILL.md` with rollback protocol and timeout handling
- Document recovery paths for dirty tree violations

### Phase 3: Task Lifecycle (Layer 3)
- Create `task-failure-lifecycle.md` fragment with state notation and transitions
- Update `handoff/SKILL.md` to handle blocked/failed task states
- Add task error recording template for session.md

### Phase 4: CPS Chains (Layer 4)
- Extend `continuation-passing.md` with error propagation model
- Update cooperative skills (`/design`, `/runbook`, `/orchestrate`, `/handoff`) with error handling
- Document orphaned continuation recovery protocol

### Phase 5: Consolidation (Layer 5)
- Review all error-related fragments for consistency
- Add cross-references between subsystems
- Document common patterns (mechanical detection, clean tree requirements, prevention over recovery)

## Success Metrics

**Completeness:**
- All three subsystems have documented error handling protocols
- Error taxonomy covers runbook, task, and CPS subsystem failures
- Every error category has defined escalation path and acceptance criteria

**Clarity:**
- Agent-level classification decision tree is actionable (agents can self-classify)
- Rollback procedures are unambiguous (no "it depends" guidance)
- Task state transitions are explicit with documented triggers

**Feasibility:**
- No changes required to Claude Code internals (hook protocol only)
- Existing patterns preserved (weak orchestrator, continuation passing)
- Implementation can proceed in phases without breaking existing workflows

**Validation:**
- Test each error category with real scenarios from exploration report
- Verify acceptance criteria are measurable (dev output, git status, validation checks)
- Confirm CPS error recovery works for multi-skill chains (`/design, /runbook, /orchestrate`)
- Validate hook error protocol with intentional hook failures
