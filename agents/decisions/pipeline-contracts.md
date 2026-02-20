# Pipeline Contracts

Centralized I/O contracts for the design-to-deliverable pipeline. Authoritative source — skills reference this document for their input/output specifications.

## When Choosing Review Gate

| # | Transformation | Input | Output | Defect Types | Review Gate | Review Criteria |
|---|---------------|-------|--------|-------------|-------------|----------------|
| T1 | Requirements → Design | requirements.md or inline | design.md | Incomplete, infeasible | design-vet-agent (opus) | Architecture, feasibility, completeness |
| T2 | Design → Outline | design.md | runbook-outline.md | Missing reqs, wrong decomposition, ungrounded corrections | runbook-outline-review-agent (opus) | Requirements coverage, phase structure, LLM failure modes |
| T2.5 | Outline → Simplified outline | runbook-outline.md (post-0.85) | runbook-outline.md (consolidated) | Missed patterns, broken numbering | runbook-simplification-agent (opus) | Pattern detection, requirements preservation |
| T3 | Outline → Phase files | runbook-outline.md | runbook-phase-N.md | Vacuity, prescriptive code, density | plan-reviewer | Type-aware: TDD discipline + general quality + LLM failure modes |
| T4 | Phase files → Runbook | runbook-phase-*.md | runbook.md | Cross-phase inconsistency | plan-reviewer (holistic) | Cross-phase consistency, numbering, metadata |
| T4.5 | Runbook → Validated runbook | runbook-phase-*.md or runbook.md | Validation reports | Model mismatches, lifecycle violations, count errors, implausible REDs | validate-runbook.py (script) | Deterministic structural checks |
| T5 | Runbook → Step artifacts | runbook.md | steps/step-*.md, agent | Generation errors | prepare-runbook.py | Automated validation |
| T6 | Steps → Implementation | step-*.md | Code/artifacts | Wrong behavior, stubs, drift | vet-fix-agent (checkpoints) | Scope IN/OUT, design alignment |

## When Routing Artifact Review

**Core routing table:** `agent-core/fragments/vet-requirement.md` "Reviewer routing by artifact type" (always-loaded, canonical).

**Orchestration-specific extensions:**

| Artifact Type | Reviewer |
|--------------|----------|
| Planning artifacts (runbooks, phases) | plan-reviewer |
| Human documentation (README, guides) | vet-fix-agent + doc-writing skill (writing style guidance) |

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

Runbook phases declare type: `tdd`, `general` (default), or `inline`.

Type determines:
- **Expansion format:** TDD → RED/GREEN cycles. General → task steps with script evaluation. Inline → pass-through (no decomposition).
- **Review criteria:** TDD → TDD discipline. General → step quality. Inline → vacuity, density, dependency ordering (lighter — no step/script/TDD checks).
- **LLM failure modes:** Apply universally regardless of type.
- **Orchestration delegation model:** TDD/general → per-step agent delegation. Inline → orchestrator-direct (reads phase content from runbook, executes edits without Task dispatch). Batching consecutive inline phases deferred pending empirical data.

Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, checkpoints.

### Inline Eligibility Criteria

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

## When Selecting Model For Prose Artifact Edits

**Decision Date:** 2026-02-18

**Rule:** Prose edits to skills, fragments, agent definitions, and architectural documents require opus. These artifacts are LLM-consumed instructions — wording directly determines downstream agent behavior.

**Anti-pattern:** Assigning sonnet/haiku to prose edits based on "edit complexity" rather than artifact type.

**Evidence:** Tier 2 plan assigned sonnet to skill/fragment edits, haiku to agent audit. User corrected: all were prose edits to architectural artifacts requiring opus.

**Classification:**
- Skills, fragments, agent definitions, design documents → opus
- Code implementation, test writing, script edits → model by complexity (haiku/sonnet)
- Mechanical execution (copy-paste, config changes) → haiku

## When Selecting Model For TDD Execution

**Decision Date:** 2026-02-18

**Anti-pattern:** Assigning model by task type (execution = haiku) without considering reasoning complexity. Haiku over-implemented steps 1-2, building guard logic meant for 6 subsequent steps.

**Correct pattern:** Assign model by complexity type:
- Pattern complexity (regexp, wiring, flags) → haiku
- State machine complexity (git ancestry, merge state) → sonnet minimum
- Synthesis complexity (trade-offs, architecture) → opus

**Classification point:** During `/runbook` expansion, not at orchestration time.

**Related:** TDD granularity doesn't help haiku — each step is "simple" but haiku can't stay within scope. Batching code+tests per phase at sonnet produces fewer, better tests with opus review.

## When Reviewing Skill Deliverable

**Decision Date:** 2026-02-18

**Anti-pattern:** Delegating skill deliverable review to Task agent — agent lacks cross-project context (other skills' allowed-tools, fragment conventions, memory index patterns).

**Correct pattern:** Route to skill-reviewer agent (has cross-skill context) or review interactively in main session. The reviewer needs to compare against project-wide patterns, not just the artifact's internal consistency.

**Evidence:** Task agent found 5 minor issues but missed the major finding (Write missing from allowed-tools). Only detectable by comparing against 18 other skills' allowed-tools fields.

## When Concluding Reviews

**Decision Date:** 2026-02-18

**Anti-pattern:** Review classifies findings as Major, then adds "doesn't block merge, follow-up work" — reviewer making merge-readiness judgment and converting findings into aspirational prose nobody tracks.

**Correct pattern:** Review reports severity counts. Creates one pending task referencing the report → `/design`. No merge-readiness language. User reads severity counts, user decides.

**Root cause:** Sycophancy in artifact form — reviewer softens its own classification to avoid blocking the pipeline.

## When Routing Implementation Findings

**Decision Date:** 2026-02-18

**Anti-pattern:** Conditional dispatch based on fix size or "architectural" judgment (e.g., "small fix → direct, design gap → /requirements"). Reintroduces judgment at a stage that should be mechanical.

**Correct pattern:** Unconditional `/design` for all findings. `/design` triage handles proportionality — simple fixes execute directly, complex ones get full treatment. No routing judgment at review time.

## When Selecting Review Model

**Decision Date:** 2026-02-19

**Anti-pattern:** Matching review model to author's model ("haiku wrote it → sonnet reviews it"). Also: blanket opus review because orchestrator is opus (inheritance makes everything opus).

**Correct pattern:** Match review model to the correctness property being verified:
- State machine routing, architectural wiring, design invariant compliance → opus
- Behavioral changes within functions (check=False, abort removal) → sonnet
- Prose artifacts consumed by LLMs → opus
- Mechanical substitutions → sonnet (test pass/fail is sufficient signal)

**Rationale:** Haiku can write state machine code that looks plausible but has subtle wiring errors. These are architectural properties that sonnet may accept. Conversely, opus reviewing grep-and-replace is waste.

## When Holistic Review Applies Fixes

**Decision Date:** 2026-02-19

**Anti-pattern:** Fixing one reference to a changed value without checking for other references in the same artifact.

**Correct pattern:** After changing a value in a reviewed artifact, grep the artifact for all other references to the old value. Fix-all means all occurrences, not just the first one found.

**Evidence:** Cycle 2.1 step file had "exit code is 0 or 3" in assertions but "Assert exit code == 3" in test setup — agent writing test would see conflicting instructions.

## When Scoping Vet For Cross-Cutting Invariants

**Decision Date:** 2026-02-19

**Anti-pattern:** Scoping vet "Changed files" to only files modified in the current phase. For cross-cutting design decisions (D-8 "all output to stdout", NFR-2 "no data loss"), the invariant domain spans the entire call graph.

**Correct pattern:** Add "Verification scope" to vet execution context listing all files that participate in the cross-cutting invariant. Identify via grep (e.g., `err=True` across merge call graph for D-8).

**Evidence:** resolve.py has `err=True` calls in the merge code path but wasn't in Phase 5's changed-files list.

## When Reviewing Final Orchestration Checkpoint

**Decision Date:** 2026-02-19

**Anti-pattern:** Scoping the final phase vet to only that phase's changes, even when the checkpoint already performs cross-cutting audits.

**Correct pattern:** Final checkpoint should include lifecycle audits for all stateful objects created during the implementation (MERGE_HEAD, staged content, lock files). Same methodology as exit code audit: trace through all code paths, flag any path that exits success with state still active.

**Evidence:** Phase 5 opus vet audited all 12 SystemExit calls (cross-cutting) but did not audit MERGE_HEAD lifecycle — same class of trace applied to git state instead of exit codes.

## When Adding Verification Scope To Vet Context

**Decision Date:** 2026-02-20

**Source:** D-4 (pipeline-skill-updates outline)

**Rule:** Add "Verification scope" to vet execution context when design decisions specify cross-cutting invariants — constraints spanning the full call graph, not just changed files.

**Indicators:**
- Design decision says "all X must Y" (e.g., "all output to stdout")
- NFR spans multiple modules (e.g., "no data loss across all code paths")
- Invariant domain is broader than the changed-files list

**Identification method:** Grep for the invariant pattern (e.g., `err=True` for output routing, `MERGE_HEAD` for state lifecycle) across the codebase.

**Where documented:**
- Operational (always-loaded): `agent-core/fragments/vet-requirement.md` — optional field in execution context
- Rationale (decision record): this section

**Evidence:** Phase 5 checkpoint audited exit codes cross-cuttingly but missed MERGE_HEAD lifecycle — vet scope was limited to changed files. resolve.py had relevant calls but wasn't in the changed-files list.
