# Pipeline Review Patterns

Model selection, review scoping, recall integration, and classification routing for pipeline review gates.

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
- Operational (always-loaded): `plugin/fragments/review-requirement.md` — optional field in execution context
- Rationale (decision record): this section

**Evidence:** Phase 5 checkpoint audited exit codes cross-cuttingly but missed MERGE_HEAD lifecycle — vet scope was limited to changed files. resolve.py had relevant calls but wasn't in the changed-files list.

## When Review Gates Feel Redundant

**Decision Date:** 2026-02-20

**Anti-pattern:** Skipping procedural review after redrafting because individual changes were user-validated in discussion. Implicit reasoning: "user approved each change → combined redraft doesn't need review."

**Correct pattern:** Review gates are non-negotiable checkpoints, not confidence-gated decisions. User validates *approach*; review agent validates *completeness, internal consistency, requirement coverage*. Combining multiple changes can introduce inconsistencies the individual discussions didn't surface.

**Root cause:** Inserting a confidence assessment step that doesn't exist in the procedure.

## When Recall-Artifact Is Absent During Review

**Decision Date:** 2026-02-24

**Anti-pattern:** Skill says "if absent, proceed without it" and reviewer takes the early exit — no recall at all. Reviewing recall-pass deliverables without performing recall is the exact gap the deliverables are designed to close.

**Correct pattern:** "If absent, do lightweight recall" — read memory-index.md, identify review-relevant entries (quality patterns, failure modes), batch-resolve. The Tier 1/2 sections in the runbook skill already have this fallback.

**Evidence:** Deliverable review of recall-pass ran without any recall. Fixed: added lightweight recall fallback to deliverable-review skill Layer 2.

## When Corrector Agents Lack Recall Mechanism

**Decision Date:** 2026-02-24

**Anti-pattern:** Corrector agents (design-corrector, outline-corrector, runbook-outline-corrector) had no recall loading in their protocols. Reviewing without recall cannot flag project-specific failure modes.

**Correct pattern:** Every corrector agent needs recall via one of: (a) self-contained loading in agent body, (b) caller passing recall entries in delegation prompt, or (c) skill-level Recall Context section. runbook-corrector gets (c) via its `skills: ["review-plan"]` field; design/outline correctors need (a) directly.

**Evidence:** RCA identified the gap. Fixed 3 skills + 3 agents.

## When Treating Recall-Artifact Summary As Recall Pass

**Decision Date:** 2026-02-24

**Anti-pattern:** Reading recall-artifact.md summaries (titles + 2-line descriptions) as terminal recall step. After `/clear`, summaries alone miss behavioral nuance that delegation prompts need verbatim.

**Correct pattern:** Read artifact to identify WHICH decisions matter, then batch-resolve via `edify _recall resolve "when <trigger>" ...` to load WHAT they say (full decision section content). Both steps required in new sessions.

**Evidence:** /reflect RCA identified the root cause.

## When Batch Changes Span Multiple Artifact Types

**Decision Date:** 2026-02-21

**Anti-pattern:** Collapsing a multi-file batch into a single reviewer. Batch framing overrides per-artifact routing — agent fabricates capability limitations to justify the simpler single-reviewer path.

**Correct pattern:** Apply proportionality per-file first (trivial changes → self-review). Route remaining files by artifact type per routing table. Routing is per-artifact-type, not per-batch.

## When Multi-Item Instructions Contain Review Steps

**Decision Date:** 2026-03-11

**Anti-pattern:** Treating "run correctors" as a checkbox item in a sequential list. Agent executes all items without stopping after the review step. Substitutes mechanical validator for corrector sub-agent.

**Correct pattern:** Items invoking review/corrector are gates — stop, present findings, wait for user decision before proceeding. Corrector means sub-agent with clean context, not self-review. Review is lifecycle-derived (artifact type + edits applied → corrector fires), not user-invoked.

## When Simple Routing Bypasses Inline Lifecycle

**Decision Date:** 2026-03-11

**Anti-pattern:** Simple classification routes to "direct execution" — recall, explore, edit, done. Bypasses /inline lifecycle: no integration-test gate, no review dispatch, no triage feedback, no deliverable-review chain.

**Correct pattern:** Simple routes through `/inline plans/<job> execute` like Moderate and Complex. /inline provides the review gating and workflow continuation that "direct execution" lacks. The classification determines design ceremony, not execution ceremony. Same class as Moderate prose bypassing /runbook.
