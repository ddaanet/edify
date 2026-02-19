---
name: error-handling
model: opus
---

# Runbook Outline: Error Handling Framework

**Design:** `plans/error-handling/outline.md`
**Status:** Draft
**Created:** 2026-02-19

---

## Requirements Mapping

| Requirement | Description | Phase |
|-------------|-------------|-------|
| L0 (Fault Prevention) | Prevention-first principle, reference prerequisite-validation.md | Phase 1 |
| L1 (Error Taxonomy) | Extend error-classification.md: fault/failure vocab, Category 5, retryable dimension, tier-aware decision tree | Phase 1 |
| D-4 (Fragment allocation) | Targeted new fragments; extend existing files minimally (D-4 constraint) | Phases 1–5 |
| L2 (Orchestration) | Escalation acceptance criteria, rollback strategy, max_turns timeout | Phase 2 |
| D-3 (Acceptance criteria) | precommit pass + clean tree + output validation = all 3 required | Phase 2 |
| D-5 (Rollback) | Revert to last clean commit before failed step | Phase 2 |
| Q1 (Timeout calibration) | max_turns ~150 on Task calls (empirical, 938 observations, p99=73, max=129) | Phase 2 |
| L3 (Task lifecycle) | Blocked/failed/canceled state notation, transitions, error recording | Phase 3 |
| D-2 (Task failure notation) | [!] blocked, [✗] failed, [–] canceled — all with reason text | Phase 3 |
| L4 (CPS chains) | Error propagation: abort + record, pivot transactions, idempotence | Phase 4 |
| D-1 (CPS error propagation) | 0 retries, abort continuation, record in session.md Blockers | Phase 4 |
| L5 (Consolidation) | Hook error protocol, cross-references, consistency review | Phase 5 |
| D-6 (Hook error protocol) | crash→stderr+continue, timeout→degraded, invalid→fallback | Phase 5 |

---

## Phase Structure

### Phase 1: Foundation — Prevention + Taxonomy (type: general)

**Files:** `agent-core/fragments/error-handling.md`, `agent-core/fragments/error-classification.md`
**Model:** Opus (fragment artifacts)
**Complexity:** Low-Medium — 2 prose additions to 2 existing fragments (~20 lines total)

- **Step 1.1: Add prevention-first principle to error-handling.md**
  - Add "Prevention Layer (L0)" subsection after existing content
  - Content: prevention-first principle (validate before execute, ~80% error prevention), reference to `prerequisite-validation.md`, cross-system scope (all subsystems benefit from validated preconditions)
  - D-4 constraint: keep addition minimal — error-handling.md is 12 lines by design; this step adds ~4-6 lines only
  - Target: `agent-core/fragments/error-handling.md` — append new subsection
  - Verification: File grows by 4-6 lines; prerequisite-validation.md reference present; prevention-first principle stated

- **Step 1.2: Extend error-classification.md — taxonomy, retryable dimension, tier-aware classification**
  - Part A (taxonomy): Add Avižienis FEF chain labeling: categories 1 (Prerequisite Failure) and 4 (Ambiguity Error) are **faults** (causes: environment fault, specification fault); categories 2 (Execution Error) and 3 (Unexpected Result) are **failures** (observations: service deviation, output deviation). Response differs: faults → prevention-oriented; failures → tolerance-oriented. Add Category 5: Inter-agent misalignment (MASFT FC2) — agent deviates from specification, ignores context, reasoning-action mismatch, premature termination, incomplete verification. Detection: existing review pipeline (no new mechanism). Add row to taxonomy table; add step 5 to decision tree; add common indicators section.
  - Part B (retryable dimension + tier-aware): Add retryable/non-retryable classification for each of the 5 categories: retryable = transient (env issue, timeout, write conflict); non-retryable = deterministic (missing file, design flaw, spec ambiguity). Add as column in taxonomy table OR as subsection immediately after table. Add tier-aware classification note at top of decision tree: sonnet/opus execution agents self-classify (report category + retryable/non-retryable); haiku agents report raw error, orchestrator classifies. Rationale: haiku lacks reliable judgment for classification.
  - Target: `agent-core/fragments/error-classification.md`
  - Verification: Taxonomy table has 5 rows; fault/failure labels present on categories 1-4; Category 5 row exists with indicators; decision tree has step 5; each category has retryable/non-retryable label; tier-aware note at decision tree top

---

### Phase 2: Orchestration Hardening (type: general)
*(Independent of Phase 3 — can run in parallel after Phase 1 completes)*

**Files:** `agent-core/fragments/escalation-acceptance.md` (new), `agent-core/skills/orchestrate/SKILL.md`
**Model:** Opus (fragment + skill artifacts)
**Complexity:** Medium — 1 new fragment (~40 lines), 1 skill addition (~30 lines)

- **Step 2.1: Create escalation-acceptance.md fragment**
  - New fragment defining acceptance criteria for escalation resolution (D-3)
  - Three required criteria: (a) `just precommit` passes, (b) `git status --porcelain` is empty (tree clean), (c) output validates against step's acceptance criteria — ALL THREE required, none optional
  - Per-error-type resolution guidance (for all 5 categories after Phase 1): prerequisite failures → verify resource now exists; execution errors → verify precommit clean + no stderr; unexpected results → validate output against step criteria; ambiguity errors → verify plan/step updated with clarification; inter-agent misalignment → verify agent output now matches specification
  - Target: `agent-core/fragments/escalation-acceptance.md` (create new)
  - Verification: File exists; 3-criteria structure present; all 5 error types have resolution guidance

- **Step 2.2: Update orchestrate/SKILL.md with rollback protocol and timeout**
  - Add rollback section (D-5): When step escalation fails → revert to last clean commit before that step (`git revert` or `git reset` to checkpoint commit); no partial undo attempted; document the assumption (all relevant state is git-managed — if non-git state involved, simple revert breaks)
  - Add timeout section (Q1): Set max_turns ~150 on Task calls when invoking step agents; catches spinning agents (high activity, no convergence); calibrated from 938 clean observations: p90=40, p95=52, p99=73, max=129, threshold=150; duration timeout (~600s, catches hanging agents) deferred — requires Claude Code infrastructure support
  - Add dirty tree recovery: after rollback to checkpoint, re-execute the failed step from clean state
  - Location: Add new "Error Recovery" section after existing "Error Escalation" section (Section 4)
  - Target: `agent-core/skills/orchestrate/SKILL.md`
  - Verification: Rollback procedure present; max_turns ~150 mentioned with calibration rationale; dirty tree recovery documented; assumption about git-managed state noted

---

### Phase 3: Task Lifecycle States (type: general)
*(Independent of Phase 2 — can run in parallel after Phase 1 completes)*

**Files:** `agent-core/fragments/task-failure-lifecycle.md` (new), `agent-core/skills/handoff/SKILL.md`
**Model:** Opus (fragment + skill artifacts)
**Complexity:** Medium — 1 new fragment (~35 lines), 1 skill extension (~20 lines)

- **Step 3.1: Create task-failure-lifecycle.md fragment**
  - State notation (D-2): `- [!]` blocked (waiting on signal, transitions back to pending when unblocked), `- [✗]` failed (terminal, system-detected, requires user decision to retry/abandon), `- [–]` canceled (terminal, user-initiated — choice, not system detection). All three states include mandatory reason text.
  - State machine: pending → in-progress → { complete `[x]` | blocked `[!]` | failed `[✗]` | canceled `[–]` }. Blocked is the only non-terminal non-complete state — it can return to pending.
  - Error context recording template for session.md (what to record when transitioning to blocked/failed/canceled): state notation + reason + chain context (which skill failed, what continuation was pending)
  - Grounding note: Subset of Temporal WorkflowExecutionStatus (Running → in-progress, Completed, Failed, Canceled, TimedOut — TimedOut maps to blocked in practice)
  - Target: `agent-core/fragments/task-failure-lifecycle.md` (create new)
  - Verification: File exists; all 3 new states defined with notation; state machine described; recording template present

- **Step 3.2: Update handoff/SKILL.md for failed/blocked task handling**
  - Extend "7. Trim Completed Tasks" section: explicitly exclude `[!]` blocked, `[✗]` failed, `[–]` canceled states from trimming. Rationale: failed/canceled tasks are blockers — trimming them on handoff loses the signal that something needs user attention. Different lifecycle from completed tasks.
  - Add reference to `task-failure-lifecycle.md` in an appropriate location (near step 7 or in step 1 context-gathering)
  - Note: Do NOT trim failed/canceled tasks even after they appear committed — they require explicit user resolution (unlike completed tasks which trim after commit + prior session)
  - Target: `agent-core/skills/handoff/SKILL.md`
  - Verification: Step 7 explicitly lists excluded states ([!], [✗], [–]); task-failure-lifecycle.md referenced; rationale for non-trimming present

---

### Phase 4: CPS Chain Error Recovery (type: general)
*Depends on: Phase 2 (acceptance criteria concept referenced), Phase 3 (Blockers state notation)*

**Files:** `agent-core/fragments/continuation-passing.md`, `agent-core/skills/design/SKILL.md`, `agent-core/skills/runbook/SKILL.md`
**Model:** Opus (fragment + skill artifacts)
**Complexity:** Medium — 1 fragment extension (~25 lines), 2 skill cross-reference additions (~5 lines each)

- **Step 4.1: Extend continuation-passing.md with error propagation model**
  - Add "Error Handling" section (after the Cooperative Skills table, before Adding Continuation section)
  - Error propagation model (D-1): When skill fails mid-chain → (1) classify error as retryable or non-retryable (informs recorded context, not immediate response); (2) abort remaining continuation regardless of classification; (3) record in session.md Blockers: state notation from task-failure-lifecycle.md + error classification + chain state (which skill failed, what continuation was pending, resume command)
  - Pivot transactions: After `/orchestrate` completes execution, compensation is impractical (Saga pattern). Document these points-of-no-return — specific chain stages where abortion means user must re-evaluate rather than simply resume.
  - Recovery idempotence: recovery operations must be idempotent so user can safely retry after fixing root cause. State-checking before write, no duplicate-create operations.
  - Manual resume: User reads Blockers entry, runs `r` to resume from recorded chain state
  - Target: `agent-core/fragments/continuation-passing.md`
  - Verification: Error Handling section present; abort-and-record pattern described; pivot transactions identified; idempotence requirement stated; Blockers recording format shown

- **Step 4.2: Add error handling cross-references to design/SKILL.md and runbook/SKILL.md**
  - Both skills: add short note in their Continuation section — "On error during this skill's execution: abort continuation and record in session.md Blockers per continuation-passing.md error protocol. Do not propagate continuation to subsequent skills."
  - Do NOT duplicate the protocol — skills reference continuation-passing.md as authoritative source
  - Targets: `agent-core/skills/design/SKILL.md`, `agent-core/skills/runbook/SKILL.md`
  - Verification: Both files have error-on-chain note; note references continuation-passing.md

---

### Phase 5: Consolidation (type: general)
*Depends on: Phases 1–4 (consolidates all new content)*

**Files:** `agent-core/fragments/error-handling.md`, `agent-core/fragments/error-classification.md`, `agent-core/fragments/task-failure-lifecycle.md`, `agent-core/fragments/continuation-passing.md` (cross-references + review)
**Model:** Opus (fragment artifacts)
**Complexity:** Low-Medium — hook protocol addition (~10 lines), cross-references (~2 lines each), consistency review

- **Step 5.1: Add hook error protocol to error-handling.md (D-6)**
  - Add "Hook Error Protocol" subsection (after Prevention Layer subsection added in Step 1.1)
  - Three failure modes: (a) Hook crash → stderr output visible to user + session continues (intentional degraded mode — CPS hook already silently catches errors, this formalizes the pattern); (b) Hook timeout → degraded mode for that event (hook behavior absent, session continues without hook for that invocation); (c) Invalid hook output → fallback to no-hook behavior (hook result ignored, session continues)
  - D-4 constraint: adds ~8-10 lines — keeps error-handling.md focused, does not expand into narrative
  - Target: `agent-core/fragments/error-handling.md`
  - Verification: Hook Error Protocol subsection present; all 3 failure modes covered; degraded mode concept defined

- **Step 5.2: Add cross-references between error-related fragments**
  - Add "See Also" or "Related" note at end of each error-related fragment pointing to the others:
    - `error-handling.md` → error-classification.md, escalation-acceptance.md, task-failure-lifecycle.md, continuation-passing.md
    - `error-classification.md` → escalation-acceptance.md (for resolution criteria after classification)
    - `escalation-acceptance.md` → error-classification.md (for category definitions), orchestrate/SKILL.md
    - `task-failure-lifecycle.md` → continuation-passing.md (for CPS chain recording), handoff/SKILL.md
    - `continuation-passing.md` → task-failure-lifecycle.md (for Blockers notation)
  - All changes are additive (append See Also section); no modification of existing content
  - Targets: 5 fragments
  - Verification: Each target file has See Also section with appropriate references

- **Step 5.3: Cross-document terminology consistency review**
  - Read: error-handling.md, error-classification.md, escalation-acceptance.md, task-failure-lifecycle.md, continuation-passing.md, orchestrate/SKILL.md, handoff/SKILL.md
  - Check for consistency: (a) fault/failure vocabulary (Avižienis terms used identically across documents); (b) retryable/non-retryable (same definition and examples); (c) state notation ([!][✗][–] used identically); (d) acceptance criteria (D-3's three criteria referenced consistently)
  - Fix any terminology discrepancies found — targeted edits only, no rewrites
  - Target: All 7 files above (read all; edit only where discrepancies found)
  - Verification: No conflicting definitions for fault/failure, retryable/non-retryable, or state notation across documents

---

## Expansion Guidance

**Model assignment:** ALL steps use opus — all targets are architectural artifacts (skills, fragments). Artifact-type override applies uniformly. No haiku/sonnet steps.

**Parallelism opportunity:** After Phase 1 completes, Phase 2 and Phase 3 can run simultaneously. Each targets a distinct file set with no overlap:
- Phase 2: escalation-acceptance.md (new), orchestrate/SKILL.md
- Phase 3: task-failure-lifecycle.md (new), handoff/SKILL.md

**Dependency chain:**
```
Phase 1 → [Phase 2 ∥ Phase 3] → Phase 4 → Phase 5
```

**Phase 0 consolidation:** Original design outline had Phase 0 (prevention documentation) as a separate phase. Consolidated into Phase 1 Step 1.1 — both are prose documentation phases; running a separate agent invocation for 4-6 lines is disproportionate overhead.

**Phase 4 dependency specifics:**
- Needs Phase 3 (task-failure-lifecycle.md state notation) to document Blockers recording format
- Needs Phase 2 (escalation-acceptance.md acceptance criteria) as conceptual reference (the "verification before resume" requirement in recovery idempotence)
- Both Phase 2 and Phase 3 must complete before Phase 4 begins

**Step 1.2 performs two sequential additions to error-classification.md:** Part A (taxonomy + Category 5) must complete before Part B (retryable dimension + tier-aware classification) — Part B classifies all 5 categories. Both parts execute within a single agent invocation; the agent applies Part A edits first, then Part B.

**Phase 5 step 5.2 spans 5 files:** Agent reads each, appends See Also section, commits all changes together. Changes are additive only — no risk of conflicting with prior phase content.

**validate-runbook.py not present:** Phase 3.5 (pre-execution validation) will be skipped — graceful degradation per skill spec.

---

## Key Decisions Reference

See `plans/error-handling/outline.md` for full rationale and resolved questions.

| Decision | Summary | Phase |
|----------|---------|-------|
| D-1 | CPS error propagation: 0 retries, abort + record in Blockers | Phase 4 |
| D-2 | Task failure notation: [!] [✗] [–] states with reason text | Phase 3 |
| D-3 | Escalation acceptance: precommit + clean tree + output validation (all 3) | Phase 2 |
| D-4 | Fragment allocation: targeted fragments; minimize extensions to minimalist files | All |
| D-5 | Rollback: revert to last clean commit (git snapshot = state restore) | Phase 2 |
| D-6 | Hook error protocol: stderr visibility + degraded mode | Phase 5 |
| Q1 | Timeout: max_turns ~150 (spinning guard, calibrated from 938 observations) | Phase 2 |
