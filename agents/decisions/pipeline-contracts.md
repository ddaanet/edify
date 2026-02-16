# Pipeline Contracts

Centralized I/O contracts for the design-to-deliverable pipeline. Authoritative source — skills reference this document for their input/output specifications.

## When Choosing Review Gate

| # | Transformation | Input | Output | Defect Types | Review Gate | Review Criteria |
|---|---------------|-------|--------|-------------|-------------|----------------|
| T1 | Requirements → Design | requirements.md or inline | design.md | Incomplete, infeasible | design-vet-agent (opus) | Architecture, feasibility, completeness |
| T2 | Design → Outline | design.md | runbook-outline.md | Missing reqs, wrong decomposition | runbook-outline-review-agent | Requirements coverage, phase structure, LLM failure modes |
| T3 | Outline → Phase files | runbook-outline.md | runbook-phase-N.md | Vacuity, prescriptive code, density | plan-reviewer | Type-aware: TDD discipline + general quality + LLM failure modes |
| T4 | Phase files → Runbook | runbook-phase-*.md | runbook.md | Cross-phase inconsistency | plan-reviewer (holistic) | Cross-phase consistency, numbering, metadata |
| T5 | Runbook → Step artifacts | runbook.md | steps/step-*.md, agent | Generation errors | prepare-runbook.py | Automated validation |
| T6 | Steps → Implementation | step-*.md | Code/artifacts | Wrong behavior, stubs, drift | vet-fix-agent (checkpoints) | Scope IN/OUT, design alignment |

## When Routing Artifact Review

Per-step validation routes to domain-specific reviewers based on artifact type.

| Artifact Type | Reviewer |
|--------------|----------|
| Code, tests | vet-fix-agent |
| Skills (SKILL.md, references/) | skill-reviewer |
| Agent definitions | agent-creator (review+autofix prompt) |
| Design documents | design-vet-agent (opus) |
| Planning artifacts (runbooks, phases) | plan-reviewer |
| Human documentation (README, fragments) | vet-fix-agent + doc-writing skill (writing style guidance) |

**Orchestrator handles all review delegation.** Sub-agents lack Task and Skill tools — they cannot delegate to any reviewer. All reviews must be delegated to prevent implementer bias (implementer never reviews own work). The execution agent commits; the orchestrator reads the validation section and delegates the review.

**Fix pattern:** All reviewers apply all fixes (critical, major, minor). Caller greps for UNFIXABLE.

**Cross-reference:** `agents/decisions/deliverable-review.md` defines review axes per artifact type.

## How To Review Delegation Scope Template

Every review delegation must include execution context (per `agent-core/fragments/vet-requirement.md`):

**Required:**
- **Scope IN:** What was produced (files, sections, features)
- **Scope OUT:** What is NOT yet done — reviewer must NOT flag these
- **Changed files:** Explicit file list
- **Requirements:** What the output should satisfy

**Optional (phased work):**
- **Prior state:** What earlier transformations established
- **Design reference:** Path to design document

## When UNFIXABLE Escalation

Reviewers at every gate follow fix-all pattern:
1. Fix all issues directly (critical, major, minor)
2. Label truly unfixable issues as `UNFIXABLE` with rationale
3. Caller greps for UNFIXABLE — if found, stop and escalate to user
4. No recommendation dead-ends — fix or escalate, nothing in between

## When Declaring Phase Type

Runbook phases declare type: `tdd` or `general` (default: general).

Type determines:
- **Expansion format:** TDD cycles (RED/GREEN) vs general steps (script evaluation)
- **Review criteria:** TDD discipline for TDD phases, step quality for general phases
- **LLM failure modes:** Apply universally regardless of type

Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, orchestration, checkpoints.

## When Vet Escalation Calibration

**Decision Date:** 2026-02-12

**Problem:** Vet agents over-escalate alignment issues as UNFIXABLE — pattern-matching tasks labeled as design decisions requiring user input.

**Evidence:** Persistent across overhaul — Phase 5 checkpoint flagged `create_worktree()` not extracted and `_git` naming as UNFIXABLE. Both were deferred design deviation (future phase) and stylistic naming (mechanical find-replace).

**Anti-pattern:** Labeling straightforward pattern-matching tasks as UNFIXABLE.

**Correct pattern:** Check existing patterns, apply consistent choice, execute alignment.

**Root cause:** Agents treat uncertainty as escalation trigger rather than scanning existing patterns for guidance.

### When Vet Flags Out-of-Scope Items

**Decision Date:** 2026-02-12

**Decision:** Distinguish DEFERRED (expected, in scope statement) from UNFIXABLE (blocking).

**Anti-pattern:** Flagging explicitly out-of-scope items as UNFIXABLE.

**Rationale:** UNFIXABLE triggers escalation to user; out-of-scope items are expected and shouldn't block.

**Example:** Cycle 0.6 vet flagged session filtering as UNFIXABLE despite "OUT: Session file filtering (next cycle)" in scope.

### When Vet Receives Execution Context

**Decision Date:** 2026-02-12

**Decision:** Vet validates against current filesystem, not execution-time state — context must be provided explicitly.

**Anti-pattern:** Trusting vet-fix-agent output without providing execution context.

**Evidence:** Phase 6 error: vet "fixed" edify-plugin → agent-core based on stale filesystem state.

**Correct pattern:** Provide execution context (IN/OUT scope, changed files, requirements). Grep UNFIXABLE after return.

### When Vet-Fix-Agent Rejects Planning Artifacts

**Decision Date:** 2026-02-12

**Decision:** vet-fix-agent reviews implementation changes only. Planning artifacts need plan-reviewer agent.

**Evidence:** vet-fix-agent line 27: "Error: Wrong agent type... This agent reviews implementation changes, not planning artifacts."

**Routing:** plan-reviewer for both TDD and general planning artifacts.

## When Reviewing Expanded Phases

**Decision Date:** 2026-02-12

**Decision:** LLM failure mode checks must run at BOTH outline AND expanded phase levels.

**Anti-pattern:** Outline review catches vacuous cycles and density issues, but phase expansion re-introduces them.

**Evidence:** Outline was fixed. But expanded phases contained 3 vacuous cycles and 1 missing requirement.

**Root cause:** plan-reviewer checks TDD discipline but not LLM failure modes after expansion.

**Gap:** Outline checks → expansion → phase review (TDD only) → no LLM failure mode re-validation.
