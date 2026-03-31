# Pipeline Contracts

Centralized I/O contracts for the design-to-deliverable pipeline. Authoritative source — skills reference this document for their input/output specifications.

## When Choosing Review Gate

| # | Transformation | Input | Output | Defect Types | Review Gate | Review Criteria |
|---|---------------|-------|--------|-------------|-------------|----------------|
| T1 | Requirements → Design | requirements.md or inline | design.md, recall-artifact.md (progressively refined at A.1, A.5, C.1) | Incomplete, infeasible | design-corrector (opus) | Architecture, feasibility, completeness |
| T2 | Design → Outline | design.md, recall-artifact.md | runbook-outline.md, recall-artifact.md (augmented at Phase 0.5, re-evaluated at Phase 0.75) | Missing reqs, wrong decomposition, ungrounded corrections | runbook-outline-corrector (opus) | Requirements coverage, phase structure, LLM failure modes |
| T2.5 | Outline → Simplified outline | runbook-outline.md (post-0.85) | runbook-outline.md (consolidated) | Missed patterns, broken numbering | runbook-simplifier (opus) | Pattern detection, requirements preservation |
| T3 | Outline → Phase files | runbook-outline.md | runbook-phase-N.md | Vacuity, prescriptive code, density | runbook-corrector | Type-aware: TDD discipline + general quality + LLM failure modes |
| T4 | Phase files → Runbook | runbook-phase-*.md | runbook.md | Cross-phase inconsistency | runbook-corrector (holistic) | Cross-phase consistency, numbering, metadata |
| T4.5 | Runbook → Validated runbook | runbook-phase-*.md or runbook.md | Validation reports | Model mismatches, lifecycle violations, count errors, implausible REDs | validate-runbook.py (script) | Deterministic structural checks |
| T5 | Runbook → Step artifacts | runbook.md | steps/step-*.md, agent | Generation errors | prepare-runbook.py | Automated validation |
| T6 | Steps → Implementation | step-*.md | Code/artifacts | Wrong behavior, stubs, drift | corrector (checkpoints) | Scope IN/OUT, design alignment |
| T6.5 | Design/Outline → Implementation (inline) | design.md or outline.md, classification.md | Code/artifacts, review report | Wrong behavior, drift from classification | corrector (/inline Phase 4a) + triage-feedback.sh | Scope IN/OUT, design alignment, triage feedback |

## When Routing Artifact Review

**Core routing table:** `plugin/fragments/review-requirement.md` "Reviewer routing by artifact type" (always-loaded, canonical).

**Orchestration-specific extensions:**

| Artifact Type | Reviewer |
|--------------|----------|
| Planning artifacts (runbooks, phases) | runbook-corrector |
| Human documentation (README, guides) | corrector + doc-writing skill (writing style guidance) |

**Orchestrator handles all review delegation.** Sub-agents lack Task and Skill tools — they cannot delegate to any reviewer. All reviews must be delegated to prevent implementer bias (implementer never reviews own work). The execution agent commits; the orchestrator reads the validation section and delegates the review.

**Fix pattern:** All reviewers apply all fixes (critical, major, minor). Caller greps for UNFIXABLE.

**Cross-reference:** `agents/decisions/deliverable-review.md` defines review axes per artifact type.

## How To Review Delegation Scope Template

Every review delegation must include execution context (per `plugin/fragments/review-requirement.md`):

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

Runbook phases declare type: `tdd`, `general` (default), or `inline`.

Type determines:
- **Expansion format:** TDD → RED/GREEN cycles. General → task steps with script evaluation. Inline → pass-through (no decomposition).
- **Review criteria:** TDD → TDD discipline. General → step quality. Inline → vacuity, density, dependency ordering (lighter — no step/script/TDD checks).
- **LLM failure modes:** Apply universally regardless of type.
- **Orchestration delegation model:** TDD/general → per-step agent delegation. Inline → orchestrator-direct (reads phase content from runbook, executes edits without Task dispatch). Batching consecutive inline phases deferred pending empirical data.

Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, checkpoints.

### When Phase Qualifies As Inline

A phase qualifies as `inline` when outcome is fully determined by instruction + target file state:
- No runtime feedback loop (tests, scripts, external state)
- Prose edits, config additions, cross-reference insertions, mechanical content application
- All decisions pre-resolved in design

Inline phases in orchestrator-plan.md use `Execution: inline` (vs `Execution: steps/step-N-M.md` for general/TDD phases). prepare-runbook.py skips step-file generation for inline phases.

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

**Anti-pattern:** Trusting corrector output without providing execution context.

**Evidence:** Phase 6 error: reviewer "fixed" edify-plugin → plugin based on stale filesystem state.

**Correct pattern:** Provide execution context (IN/OUT scope, changed files, requirements). Grep UNFIXABLE after return.

### When Corrector Rejects Planning Artifacts

**Decision Date:** 2026-02-12

**Decision:** corrector reviews implementation changes only. Planning artifacts need runbook-corrector agent.

**Evidence:** corrector line 27: "Error: Wrong agent type... This agent reviews implementation changes, not planning artifacts."

**Routing:** runbook-corrector for both TDD and general planning artifacts.

## When Reviewing Expanded Phases

**Decision Date:** 2026-02-12

**Decision:** LLM failure mode checks must run at BOTH outline AND expanded phase levels.

**Anti-pattern:** Outline review catches vacuous cycles and density issues, but phase expansion re-introduces them.

**Evidence:** Outline was fixed. But expanded phases contained 3 vacuous cycles and 1 missing requirement.

**Root cause:** runbook-corrector checks TDD discipline but not LLM failure modes after expansion.

**Gap:** Outline checks → expansion → phase review (TDD only) → no LLM failure mode re-validation.

## When Outline Review Produces Ungrounded Corrections

**Decision Date:** 2026-02-16

**Decision:** Outline review agent runs at opus (was sonnet). Added grounding constraint to fix-all policy.

**Problem:** Sonnet review agent's fix-all policy generates plausible but ungrounded corrections — confabulated operation sequences, removed design-specified features, fabricated file sizes.

**Evidence:** 2x2 controlled experiment (generator × reviewer model):
- Sonnet review on sonnet outline: confabulated rm() operation list contradicting design flow diagram
- Sonnet review on opus outline: removed design-specified diagnostic logging as "vacuous", fabricated utils.py size (150 vs actual 38 lines)
- Opus review on both outlines: grounded in source material, no confabulations
- Delegation prompts: structurally equivalent across all conditions (eliminated as variable)

**Root cause:** Sonnet identifies non-problems as problems ("vague integration guidance" when design has the detail), then confabulates fixes. The outline is a structural document that references the design; the review agent treated it as standalone.

**Fix:** (1) Model tier: opus for outline review — once per plan, errors propagate to all execution steps. (2) Grounding constraint: expansion guidance must reference design sections, not reproduce implementation detail.

**Experimental branches:** `runbook-opus-test` (opus generation + opus review), `runbook-sonnet-test` (opus generation + sonnet review). Session transcript: `6f7636e0-2455-406b-bc2b-49bd74b98db1`.

## When Simplifying Runbook Outlines

**Decision Date:** 2026-02-18

**Anti-pattern:** Planning 4 identical-pattern cycles separately (e.g., 4 status levels each adding one artifact check to the same function), then optimizing post-hoc.

**Correct pattern:** Detect identical patterns during Phase 1 expansion and consolidate upfront. Indicators: same function modified, same test structure, only fixture data differs. Parametrized cycle with table of inputs replaces N separate RED/GREEN rounds.

**Consolidation timing:** Consolidate at the earliest pipeline point where patterns are detectable. Identical patterns (same function, varying fixture data) are visible from outline titles — expanded RED/GREEN detail not needed for detection. Moving consolidation from Phase 1.5 to outline level (after Phase 0.85) saves expansion cost for ~12 items.

**Evidence:** Workwoods P1 cycles 1.2-1.5, P5 cycles 5.5-5.7, P4 cycles 4.3-4.6 all exhibited this pattern. Post-hoc optimization saved 12 items but required 5 parallel agents + holistic re-review.

## When Using Inline Execution Lifecycle

`/inline` wraps Tier 1 (direct) and Tier 2 (delegated) execution with a standard lifecycle: entry gate → pre-work → execute → corrector → triage feedback → deliverable-review chain. Invoked by `/design` (Phase B/C.5 execution-ready paths) and `/runbook` (Tier 1/2 assessment).

**When to use:** Work classified as execution-ready by /design sufficiency gate or /runbook tier assessment (Tier 1 or Tier 2).

**When NOT to use:** Tier 3 (full runbook) — uses `/orchestrate` instead.

### How To Dispatch Corrector From Inline Skill

Corrector dispatch follows standardized template in `plugin/skills/inline/references/corrector-template.md`. Key fields: scope (uncommitted changes via git diff against baseline), design context (from outline.md or design.md), recall context (review-relevant entries from recall-artifact.md or lightweight fallback), report path.

### When Triage Feedback Shows Divergence

`triage-feedback.sh` compares post-execution evidence against pre-execution classification.md. Divergence surfaced inline — no automatic action. Divergence data accumulates in `plans/reports/triage-feedback-log.md` for future threshold calibration. Current heuristics are initial estimates (C-3 constraint).

### When Proximal Requirements Reveal Lifecycle Gaps

**Decision Date:** 2026-02-27

**Pattern:** A specific requirement (e.g., "post-execution comparison point") that can't map to any existing pipeline stage reveals a structural gap. The pipeline state machine (/requirements → /design → /runbook → /orchestrate → /deliverable-review → /commit) has no stage for execution-ready work between /design and /handoff.

**Correct pattern:** The proximal requirement points at the structural gap. Fix the gap (inline execution skill covering pre-work + execute + post-work), and the proximal requirement becomes one FR among many.

**Corollary:** Conditional gates ("skip Read if no /design ran") reintroduce prose-gate failure modes. The D+B principle applies: unconditional Read, file absence is the negative path.

## When Classifying Composite Tasks

**Decision Date:** 2026-03-02

**Anti-pattern:** Batch-classifying a task containing multiple discrete work items (deliverable review findings, PR comments, multi-FR list). Group reasoning averages heterogeneous items — a behavioral code change gets masked by non-behavioral siblings.

**Correct pattern:** Decompose before classifying. If the input artifact contains N discrete work items, produce a per-item behavioral code check. Any item that adds conditional branches, functions, or logic paths elevates that item to Moderate minimum.

**Distinct from:** Companion tasks (explicit user bundling in session notes). Composite tasks are implicitly bundled by the task's nature — decomposition requires reading the input artifact.

**Evidence:** M-1 (precondition guard adding conditional branch) batch-classified as Simple alongside M-2 (comment) and M-3 (assertion tightening). Third instance of "behavioral code as Simple" pattern.

## When Routing Moderate Classification To Runbook

**Decision Date:** 2026-03-02

**Anti-pattern:** Requirements can be behaviorally complete (every FR has testable acceptance criteria) but structurally incomplete (no module layout, function decomposition, wiring decisions). The /design Moderate route skips design entirely — "Route to /runbook."

**Correct pattern:** When requirements lack structural decisions, generate a lightweight outline before /runbook. The outline materializes "how" decisions (module structure, component boundaries, wiring) alongside the "what" (behavioral spec). Skip only when requirements are functionally complete — behavioral + structural.

**Evidence:** Single data point (recall-cli-integration). Trigger condition needs sharper criteria before modifying /design skill.
