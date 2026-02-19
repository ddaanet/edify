---
name: error-handling
model: opus
---

# Error Handling Framework

**Context**: Implement layered error handling across three subsystems — runbook orchestration, task lifecycle, and CPS skill chains. Six key decisions (D-1 through D-6) are all pre-resolved in the design.
**Design**: `plans/error-handling/outline.md`
**Status**: Ready
**Created**: 2026-02-19

---

## Weak Orchestrator Metadata

**Total Steps**: 11

**Execution Model**: Opus for ALL steps (artifact-type override — all targets are skills or fragments)

**Step Dependencies**:
```
Phase 1 (Steps 1.1, 1.2) → [Phase 2 (2.1, 2.2) ∥ Phase 3 (3.1, 3.2)] → Phase 4 (4.1, 4.2) → Phase 5 (5.1, 5.2, 5.3)
```
- Phases 2 and 3 are independent — execute in parallel after Phase 1 completes
- Phase 4 requires BOTH Phase 2 (escalation-acceptance.md content) AND Phase 3 (task-failure-lifecycle.md state notation)
- Phase 5 requires Phases 1–4 complete (consolidates all new content)

**Error Escalation**:
- Opus → User: Design decisions needed, architectural changes required, or opus cannot resolve (no haiku/sonnet steps in this runbook)

**Report Locations**: `plans/error-handling/reports/step-{N}-execution.md`

**Success Criteria**: All 11 steps complete; 7 error-related artifacts (5 fragments, 2 skills) form a coherent, cross-referenced framework covering all three subsystems.

**Prerequisites**:
- `agent-core/fragments/error-handling.md` — exists (✓ verified: 12-line minimalist fragment)
- `agent-core/fragments/error-classification.md` — exists (✓ verified: 131-line fragment with 4-category taxonomy)
- `agent-core/fragments/continuation-passing.md` — exists (✓ verified: cooperative skills protocol)
- `agent-core/skills/orchestrate/SKILL.md` — exists (✓ verified: 471-line skill file)
- `agent-core/skills/handoff/SKILL.md` — exists (✓ verified: 330-line skill file)
- `agent-core/skills/design/SKILL.md` — exists (✓ verified)
- `agent-core/skills/runbook/SKILL.md` — exists (✓ verified)
- `agent-core/fragments/escalation-acceptance.md` — does NOT exist (created in Step 2.1)
- `agent-core/fragments/task-failure-lifecycle.md` — does NOT exist (created in Step 3.1)

---

## Common Context

**Design decisions (pre-resolved — do NOT re-derive):**
- **D-1**: CPS error propagation: 0 retries, abort continuation, record in session.md Blockers with classification + chain context
- **D-2**: Task failure notation: `- [!]` blocked, `- [✗]` failed, `- [–]` canceled — all include reason text
- **D-3**: Escalation acceptance: ALL THREE required — (a) `just precommit` passes, (b) tree clean, (c) output validates against step criteria
- **D-4**: Fragment allocation: create targeted new fragments; extend existing minimalist fragments only minimally (error-handling.md is 12 lines by design)
- **D-5**: Rollback = revert to last clean commit before failed step; no partial undo; assumption: all state is git-managed
- **D-6**: Hook error protocol: crash → stderr + session continues; timeout → degraded mode; invalid output → fallback to no-hook behavior
- **Q1**: max_turns ~150 on Task calls (spinning guard; calibrated from 938 clean observations: p99=73, max=129)

**Scope boundaries (do NOT implement):**
- Hook system architecture changes (Claude Code internals)
- Agent crash recovery automation
- Vet over-escalation pattern library
- Prerequisite validation enforcement in tooling (plan-reviewer script change)

**Key constraints:**
- D-4 applies to every step: do not expand minimalist fragments into narrative documents
- All targets are architectural artifacts — opus model required, no exceptions
- error-handling.md growth budget: ~14-16 lines total (Steps 1.1 + 5.1 combined)

**Project paths:**
- Fragments: `agent-core/fragments/`
- Skills: `agent-core/skills/<name>/SKILL.md`
- Reports: `plans/error-handling/reports/`
- Design: `plans/error-handling/outline.md`

---

### Phase 1: Foundation — Prevention + Taxonomy (type: general)

## Step 1.1: Add prevention-first principle to error-handling.md

**Objective**: Document fault prevention (Layer 0) in error-handling.md — establish the prevention-first principle across all subsystems by referencing existing prerequisite-validation.md patterns.
**Script Evaluation**: Small (≤25 lines inline — append ~4-6 lines to existing 12-line fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-handling.md` — understand existing content and minimalist structure (12 lines by design).

**Implementation**:
Add a new "Prevention Layer (L0)" subsection at the end of `agent-core/fragments/error-handling.md` (after the existing exception note). Content:
- Prevention-first principle: validate before execute — ~80% of errors caught before propagation
- Reference `prerequisite-validation.md` (existing patterns document the validation checklist)
- Cross-system scope: all three subsystems (orchestration, task lifecycle, CPS chains) benefit from validated preconditions before execution begins
- Keep addition to 4-6 lines only (D-4 constraint — error-handling.md is intentionally minimalist)

**Expected Outcome**: error-handling.md grows from 12 lines to ~16-18 lines. New subsection "Prevention Layer (L0)" present with prerequisite-validation.md reference.

**Error Conditions**:
- If adding more than 8 lines, STOP — revisit scope (D-4 constraint violated)

**Validation**:
- File has "Prevention Layer" or "L0" heading
- `prerequisite-validation.md` referenced
- File stays under 20 lines total

---

## Step 1.2: Extend error-classification.md — taxonomy + behavioral dimensions

**Objective**: Extend the 4-category taxonomy to 5 categories with fault/failure vocabulary (Avižienis), add retryable/non-retryable dimension, and add tier-aware classification guidance.
**Script Evaluation**: Prose (25-100 lines — substantial additions to 131-line fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-classification.md` — understand existing 4-category taxonomy table, decision tree (4 steps), and common patterns sections.

**Implementation — Part A (taxonomy, apply first)**:

1. Add fault/failure vocabulary to the taxonomy section header or as a subsection immediately after the taxonomy table:
   - Categories 1 (Prerequisite Failure) and 4 (Ambiguity Error) are **faults** (root causes: environment fault, specification fault respectively). Response: prevention-oriented (validate, clarify before executing).
   - Categories 2 (Execution Error) and 3 (Unexpected Result) are **failures** (observable deviations: service deviation, output deviation respectively). Response: tolerance-oriented (retry if retryable, escalate, compensate).
   - Grounding: Avižienis Fault-Error-Failure chain (FEF).

2. Add Category 5 (Inter-agent misalignment) — new row in taxonomy table:
   - Definition: Agent deviates from specification, ignores provided context, reasoning-action mismatch, premature termination, incomplete verification
   - Examples: vet confabulation (invented test claim), agent skipping steps, over-escalation
   - Trigger Conditions: Agent output contradicts specification; review pipeline catches deviation; agent terminates without meeting step criteria
   - Escalation Path: Sonnet verification → if confirmed misalignment → plan correction or re-execution with stronger constraints
   - Add step 5 to the decision tree: "5. Does agent output contradict specification, ignore provided context, or skip required verification? YES → INTER_AGENT_MISALIGNMENT (escalate to sonnet for verification)"
   - Add indicators to "Common Patterns" section: agent returns success without evidence of verification, output missing required sections specified in step, agent ignores explicit constraints in step definition

**Implementation — Part B (behavioral dimensions, apply after Part A)**:

3. Add retryable/non-retryable classification — add column to taxonomy table OR add subsection "Retryable vs Non-Retryable" after the table:
   - Prerequisite Failure: non-retryable (missing resource is deterministic — won't fix itself)
   - Execution Error: retryable if transient (env issue, write conflict, timeout); non-retryable if deterministic (test logic error, build configuration wrong)
   - Unexpected Result: non-retryable (output deviation persists without fix)
   - Ambiguity Error: non-retryable (requires plan update, not retry)
   - Inter-agent misalignment: non-retryable (re-running same agent with same context reproduces deviation)

4. Add tier-aware classification note at the TOP of the "Error Classification Logic for Agents" decision tree section:
   - Sonnet/opus execution agents: self-classify using decision tree below — report BOTH category AND retryable/non-retryable determination with rationale
   - Haiku execution agents: report raw error + observed facts only; orchestrator applies decision tree for classification
   - Rationale: classification requires judgment that haiku cannot reliably provide; orchestrator already knows agent model tier

**Expected Outcome**:
- Taxonomy table has 5 rows (Categories 1-5)
- Fault/failure labels visible on categories 1-4
- Each category has retryable/non-retryable classification
- Decision tree has 5 steps
- Tier-aware note at decision tree top

**Error Conditions**:
- If table structure becomes unclear with added column, use separate subsection instead
- Part B must be applied after Part A (category 5 must exist before it can be classified as retryable/non-retryable)

**Validation**:
- `grep -c "INTER_AGENT_MISALIGNMENT\|Category 5\|Inter-agent" agent-core/fragments/error-classification.md` returns > 0
- Decision tree section has 5 numbered steps
- "tier-aware" or "haiku" or "self-classify" language present in decision tree header
- Fault/failure labels present for categories 1-4

---

### Phase 2: Orchestration Hardening (type: general)
*(Independent of Phase 3 — run in parallel after Phase 1 completes)*

## Step 2.1: Create escalation-acceptance.md fragment

**Objective**: Create new fragment defining acceptance criteria for escalation resolution (D-3). Establishes the three required criteria that must ALL pass before an escalated error is considered "fixed."
**Script Evaluation**: Small (create new file, ~40 lines)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-classification.md` (post-Step-1.2 state) — understand all 5 error categories to write per-category resolution guidance.

**Implementation**:
Create `agent-core/fragments/escalation-acceptance.md` with:

1. Section: "Escalation Resolution Criteria (D-3)" — three required criteria (ALL must pass):
   - (a) `just precommit` passes — no lint, format, or test failures
   - (b) `git status --porcelain` returns empty — working tree clean
   - (c) Step output validates against the step's acceptance criteria (from step definition Validation section)
   None of the three is optional. Sonnet diagnostic resolves by applying fix + verifying all three pass before reporting success.

2. Section: "Per-Category Resolution Guidance" — what "fixed" means for each error type:
   - Prerequisite Failure: resource now exists at expected path (verify with Read/Glob/Bash before re-executing step)
   - Execution Error: command now exits 0 and precommit clean; if test failure, test now passes
   - Unexpected Result: output now matches step validation criteria (re-read step definition criteria, validate output against them)
   - Ambiguity Error: step definition updated with clarification; ambiguous language replaced with unambiguous instruction; escalated to orchestrator for plan update
   - Inter-agent misalignment: re-executed agent output now matches specification; if same agent with stronger constraints still misaligns, escalate to user

3. Short section: "Verification Sequence" — the order to verify:
   - Fix the root cause first (resource, code, plan update)
   - Run `just precommit` — all checks must pass
   - Run `git status --porcelain` — must be empty
   - Re-read step's Validation section — run each check manually
   - Only report success after all three pass

**Expected Outcome**: New file `agent-core/fragments/escalation-acceptance.md` exists with ~40 lines. Three-criteria structure present. All 5 error categories have resolution guidance.

**Error Conditions**:
- STOP if file already exists (unexpected state — report to user)

**Validation**:
- `test -f agent-core/fragments/escalation-acceptance.md` succeeds
- File contains "just precommit" reference
- File contains "git status --porcelain" reference
- All 5 category names present (Prerequisite Failure, Execution Error, Unexpected Result, Ambiguity Error, Inter-agent misalignment / INTER_AGENT_MISALIGNMENT)

---

## Step 2.2: Update orchestrate/SKILL.md with rollback protocol and timeout

**Objective**: Add error recovery section to orchestrate/SKILL.md covering rollback strategy (D-5), timeout handling (Q1), and dirty tree recovery protocol.
**Script Evaluation**: Prose (25-100 lines — new section added to 471-line file)
**Execution Model**: Opus (skill artifact)

**Prerequisite**: Read `agent-core/skills/orchestrate/SKILL.md` sections 3 (Execute Steps Sequentially) and 4 (Error Escalation) — understand current dirty-tree check and escalation flow before adding recovery protocol.

**Implementation**:
Add a new "### 4b. Error Recovery" section immediately after the existing "### 4. Error Escalation" section (before "### 5. Progress Tracking"):

1. **Rollback Protocol (D-5)**:
   - Trigger: When Sonnet diagnostic confirms step cannot be fixed (level 2 escalation path fails)
   - Action: Revert to last clean git commit before the failed step. Use `git log --oneline -5` to identify the checkpoint commit; `git reset --hard <checkpoint-sha>` to restore
   - Principle: No partial undo — reverting a commit IS restoring state (git's atomic snapshot model)
   - Assumption: All relevant state is git-managed. If non-git state is involved (external service calls, unreachable session.md edits), the simple revert model breaks — escalate to user rather than reverting
   - After rollback: Clean tree confirmed → step can be retried with corrected context or user revises the step

2. **Timeout Protocol (Q1)**:
   - Spinning failure mode (high activity, no convergence): Set `max_turns=150` on Task calls when invoking step agents
   - Calibration: 938 clean Task observations; p90=40 turns, p95=52, p99=73, max=129; threshold 150 provides ~99.9th percentile headroom
   - If step agent hits max_turns: orchestrator receives "max turns exceeded" result → treat as execution error → escalate to Sonnet diagnostic
   - Duration timeout (hanging failure mode, no activity): Deferred — requires Claude Code infrastructure support not currently available to project

3. **Dirty Tree Recovery**:
   - Trigger: `git status --porcelain` returns output after step completion (step left uncommitted changes — current behavior: STOP orchestration)
   - With rollback: After stopping, revert to last checkpoint commit → re-execute the failed step from clean state
   - The clean tree check (existing section 3.3) remains unchanged — STOP is correct. This section documents what happens AFTER the stop: rollback then retry

**Expected Outcome**: New "4b. Error Recovery" section in orchestrate/SKILL.md with rollback, timeout, and dirty tree recovery. max_turns ~150 documented with calibration rationale.

**Error Conditions**:
- If section 4 location unclear after reading, search for "Error Escalation" heading and insert after

**Validation**:
- `grep -n "Error Recovery\|4b" agent-core/skills/orchestrate/SKILL.md` returns match
- "max_turns" and "150" both present in new section
- "git reset" or "revert" (rollback mechanism) present
- Calibration data (938 observations, p99=73) referenced

---

### Phase 3: Task Lifecycle States (type: general)
*(Independent of Phase 2 — run in parallel after Phase 1 completes)*

## Step 3.1: Create task-failure-lifecycle.md fragment

**Objective**: Create new fragment defining the extended task state model — blocked, failed, and canceled states with notation, state machine, error recording template, and grounding.
**Script Evaluation**: Small (create new file, ~35 lines)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-handling.md` and scan `agents/session.md` (already in context via CLAUDE.md @-reference) — understand existing `[x]` complete notation before adding new states.

**Implementation**:
Create `agent-core/fragments/task-failure-lifecycle.md` with:

1. Section: "Extended Task State Notation (D-2)" — define the three new states:
   - `- [!] **Task Name** — reason: [why blocked]` — blocked: waiting on external signal, transitions back to pending when unblocked
   - `- [✗] **Task Name** — failed: [what failed and why]` — failed: terminal, system-detected; requires explicit user decision to retry or abandon
   - `- [–] **Task Name** — canceled: [reason]` — canceled: terminal, user-initiated; distinct from failed (intentional choice vs system detection)
   - All three states include mandatory reason text — state without reason is invalid notation

2. Section: "State Machine" — transitions:
   ```
   pending → in-progress → complete [x]
                         → blocked  [!]  → pending (when unblocked)
                         → failed   [✗]  (terminal — user decision required)
                         → canceled [–]  (terminal — user-initiated)
   ```
   - Blocked is the only non-terminal non-complete state (can return to pending)
   - Failed and canceled both require explicit user action — handoff does NOT trim them
   - Grounding: Subset of Temporal WorkflowExecutionStatus (Running, Completed, Failed, Canceled, TimedOut — TimedOut maps to blocked in practice)

3. Section: "Error Context Recording Template" — when transitioning a task to blocked/failed/canceled, record:
   ```markdown
   - [✗] **Task Name** — failed: [brief reason]
     - Error: [error category from error-classification.md] — [specific message]
     - Chain: [which skill failed] → [continuation that was pending]
     - Resume: fix [root cause]; `r` to resume
   ```
   Use `[!]` for blocked (pending fix), `[✗]` for failed (terminal), `[–]` for canceled.

**Expected Outcome**: New file `agent-core/fragments/task-failure-lifecycle.md` exists with state notation, state machine, and recording template.

**Error Conditions**:
- STOP if file already exists (unexpected state)

**Validation**:
- `test -f agent-core/fragments/task-failure-lifecycle.md` succeeds
- All 3 new state symbols present: `[!]`, `[✗]`, `[–]`
- State machine section present
- Recording template present with Chain and Resume fields

---

## Step 3.2: Update handoff/SKILL.md for failed/blocked task handling

**Objective**: Extend handoff skill to explicitly preserve failed/blocked/canceled tasks (not trim them), and reference task-failure-lifecycle.md for state notation.
**Script Evaluation**: Prose (25-100 lines — targeted additions to 330-line file)
**Execution Model**: Opus (skill artifact)

**Prerequisite**: Read `agent-core/skills/handoff/SKILL.md` section "### 7. Trim Completed Tasks" — understand current trim logic before extending it.

**Implementation**:

1. **Extend Section 7 (Trim Completed Tasks)**:
   Add explicit exclusion rule immediately after "Rule: Delete completed tasks only if BOTH conditions are true":
   > **NEVER trim tasks in blocked `[!]`, failed `[✗]`, or canceled `[–]` states.** These states signal unresolved issues requiring user attention — trimming them on handoff silently loses the signal. Failed/canceled tasks persist until the user explicitly resolves them (retries, abandons, or cancels). This differs from completed `[x]` tasks, which trim after commit + prior session.

2. **Add reference to task-failure-lifecycle.md**:
   In Section 1 (Gather Context) or at the start of Section 7, add:
   > Task failure states ([!] blocked, [✗] failed, [–] canceled) are defined in `agent-core/fragments/task-failure-lifecycle.md`. See that fragment for notation, state transitions, and error context recording template.

**Expected Outcome**: Section 7 explicitly excludes [!], [✗], [–] states from trimming with rationale. task-failure-lifecycle.md referenced.

**Error Conditions**:
- If "Trim Completed Tasks" section has moved or been renamed, search for trim-related content and add the exclusion rule in the appropriate location

**Validation**:
- `grep -n "\[!\]\|\[✗\]\|\[–\]" agent-core/skills/handoff/SKILL.md` returns match in section 7 area
- `grep "task-failure-lifecycle" agent-core/skills/handoff/SKILL.md` returns match
- Rationale for non-trimming present ("signal", "user attention", or equivalent)

---

### Phase 4: CPS Chain Error Recovery (type: general)
*Depends on: Phase 2 (escalation-acceptance.md content) AND Phase 3 (task-failure-lifecycle.md state notation)*

## Step 4.1: Extend continuation-passing.md with error propagation model

**Objective**: Add error handling section to continuation-passing.md documenting what happens when a skill fails mid-chain — abort protocol, Blockers recording format, pivot transactions, and idempotence requirement.
**Script Evaluation**: Prose (25-100 lines — new section added to existing fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/continuation-passing.md` — understand cooperative skills table and continuation protocol. Read `agent-core/fragments/task-failure-lifecycle.md` (created in Step 3.1) — understand Blockers recording format before documenting it here.

**Implementation**:
Add "## Error Handling" section after the "## Cooperative Skills" table and before "## Adding Continuation to a New Skill":

1. **Error Propagation Model (D-1)**:
   - When a cooperative skill fails mid-execution:
     1. Classify the error as retryable or non-retryable (per error-classification.md decision tree) — informs recorded context, does NOT change immediate response
     2. Abort the remaining continuation — do not propagate to next skill in chain
     3. Record in session.md Blockers section using task-failure-lifecycle.md recording template: error category, retryable classification, which skill failed, what continuation was pending, and resume instructions

2. **Pivot Transactions**:
   - After `/orchestrate` completes its execution phase, compensating for failures becomes impractical (Saga pattern — no rollback for multi-step committed state). These are points-of-no-return in the chain.
   - Chain stages and their pivot status:
     - Before `/orchestrate` begins: all prior artifacts can be revised (non-pivot)
     - After `/orchestrate` completes execution: compensating individual steps impractical (pivot point)
   - If failure occurs after a pivot: record the pivot status in the Blockers entry so user knows compensation context

3. **Recovery Idempotence**:
   - All recovery operations must be idempotent — safe to retry after the user fixes the root cause
   - Idempotence patterns: check-before-write (verify resource doesn't exist before creating), upsert over insert, version-check before overwrite
   - Required because: user may resume with `r` after partial fix, re-executing the last skill's recovery actions

4. **Manual Resume**:
   - User reads the Blockers entry from session.md
   - Fixes the root cause documented in the entry
   - Runs `r` to resume from the recorded chain state
   - The `r` command picks up the in-progress task, which references the continuation state

**Expected Outcome**: Error Handling section present in continuation-passing.md with abort-and-record model, pivot transactions, idempotence requirement, and resume instructions.

**Error Conditions**:
- If task-failure-lifecycle.md recording template format unclear (Step 3.1 not complete), STOP and report dependency not met

**Validation**:
- "Error Handling" or "Error Propagation" heading present in continuation-passing.md
- "Blockers" or "session.md Blockers" referenced (abort-and-record)
- "pivot" or "point-of-no-return" concept present
- "idempotent" or "idempotence" requirement stated
- `grep -n "abort\|Blockers\|pivot\|idempoten" agent-core/fragments/continuation-passing.md` returns 3+ matches

---

## Step 4.2: Add error handling cross-references to all cooperative skills

**Objective**: Add a brief error handling note to the Continuation section of all four cooperative skills (design, runbook, orchestrate, handoff) — directing each to abort and record in Blockers per the continuation-passing.md protocol.
**Script Evaluation**: Small (≤25 lines — ~5 lines added to each of 4 files)
**Execution Model**: Opus (skill artifacts)

**Prerequisite**: Read all four skill files — `agent-core/skills/design/SKILL.md`, `agent-core/skills/runbook/SKILL.md`, `agent-core/skills/orchestrate/SKILL.md`, `agent-core/skills/handoff/SKILL.md` — locate the Continuation section in each (or identify where to add one).

**Implementation**:
In each skill's Continuation section, add a short error handling note immediately before or after the consumption protocol steps:

```
**On error during this skill's execution:** Abort the remaining continuation — do not propagate to the next skill. Record the failure in session.md Blockers using the template in `agent-core/fragments/task-failure-lifecycle.md`. The continuation-passing.md error protocol is authoritative for the abort-and-record model.
```

Do NOT duplicate the full protocol — these are cross-references only. The skills point to continuation-passing.md as the source of truth.

**Expected Outcome**: All four cooperative skills (design, runbook, orchestrate, handoff) have the error handling note in or near their Continuation/tail-call section. Notes reference continuation-passing.md.

**Error Conditions**:
- If a skill does not have a Continuation section, add the note adjacent to the existing tail-call or handoff invocation (do not restructure the skill's exit flow)

**Validation**:
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/design/SKILL.md` returns match
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/runbook/SKILL.md` returns match
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/orchestrate/SKILL.md` returns match
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/handoff/SKILL.md` returns match

---

### Phase 5: Consolidation (type: general)
*Depends on: Phases 1–4 complete*

## Step 5.1: Add hook error protocol to error-handling.md (D-6)

**Objective**: Formalize the hook error protocol in error-handling.md — what happens when hooks crash, timeout, or produce invalid output. The CPS hook already silently catches errors; this step makes the intended degraded-mode behavior explicit.
**Script Evaluation**: Small (≤25 lines — append ~8-10 lines to ~18-line fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-handling.md` (post-Step-1.1 state) — understand current content before adding hook protocol subsection.

**Implementation**:
Add "Hook Error Protocol (D-6)" subsection at the end of `agent-core/fragments/error-handling.md`:

Three failure modes, each with defined behavior:
- **Hook crash**: stderr output visible to user + session continues (intentional degraded mode — CPS hook design silently catches errors, this formalizes that as the intended behavior, not a bug)
- **Hook timeout**: degraded mode for that event — hook behavior absent for the current invocation; session continues without hook processing
- **Invalid hook output**: fallback to no-hook behavior — hook result ignored; session continues as if hook were not installed

Apply D-4 constraint: addition must stay focused (8-10 lines). No narrative explanation of why hooks fail.

**Expected Outcome**: error-handling.md grows to ~26-28 lines total (12 original + ~6 from Step 1.1 + ~8-10 from this step). Hook Error Protocol subsection present with all 3 failure modes.

**Error Conditions**:
- If adding more than 12 lines, STOP — revisit scope (D-4 constraint violated)

**Validation**:
- "Hook Error Protocol" or "D-6" heading present
- All 3 failure modes present: crash, timeout, invalid output
- "degraded mode" concept documented for timeout case
- File total length ≤ 30 lines

---

## Step 5.2: Add cross-references between error-related fragments

**Objective**: Add "See Also" sections to each error-related fragment pointing to related fragments, enabling navigation across the framework.
**Script Evaluation**: Small (≤25 lines — 2-line See Also additions to 5 files)
**Execution Model**: Opus (fragment artifacts)

**Prerequisite**: Verify all target files exist (Phases 1-4 must be complete). Read each file to find appropriate insertion point (end of file or after final section).

**Implementation**:
Add "**See Also:**" note at the end of each fragment (append, additive only — no modification of existing content):

- `error-handling.md` → "See Also: `error-classification.md` (taxonomy), `escalation-acceptance.md` (resolution criteria), `task-failure-lifecycle.md` (task states), `continuation-passing.md` (CPS chain error protocol)"
- `error-classification.md` → "See Also: `escalation-acceptance.md` (resolution criteria for each category)"
- `escalation-acceptance.md` → "See Also: `error-classification.md` (category definitions), `agent-core/skills/orchestrate/SKILL.md` (recovery protocol)"
- `task-failure-lifecycle.md` → "See Also: `continuation-passing.md` (CPS chain recording), `agent-core/skills/handoff/SKILL.md` (trim rules)"
- `continuation-passing.md` → "See Also: `task-failure-lifecycle.md` (Blockers notation)"

**Expected Outcome**: Each of the 5 target fragments has a See Also note at its end. All additions are ≤2 lines per file.

**Error Conditions**:
- If a target file doesn't exist (Phase dependency not met), STOP and report which step failed

**Validation**:
- `grep "See Also" agent-core/fragments/error-handling.md` returns match
- `grep "See Also" agent-core/fragments/error-classification.md` returns match
- `grep "See Also" agent-core/fragments/escalation-acceptance.md` returns match
- `grep "See Also" agent-core/fragments/task-failure-lifecycle.md` returns match
- `grep "See Also" agent-core/fragments/continuation-passing.md` returns match

---

## Step 5.3: Cross-document terminology consistency review

**Objective**: Read all error-related artifacts and verify terminology is consistent across documents. Fix any discrepancies found.
**Script Evaluation**: Prose (review pass — read 7 files, targeted edits where discrepancies found)
**Execution Model**: Opus (all targets are architectural artifacts)

**Prerequisite**: All of Phases 1–4 must be complete. Read all 7 target files before assessing consistency.

**Implementation**:
Read all 7 files: `error-handling.md`, `error-classification.md`, `escalation-acceptance.md`, `task-failure-lifecycle.md`, `continuation-passing.md`, `orchestrate/SKILL.md`, `handoff/SKILL.md`.

Check for consistency across documents:
1. **Fault/failure vocabulary**: "fault" and "failure" used identically per Avižienis FEF chain (categories 1&4=faults, 2&3=failures, 5=neither — it's a misalignment, not categorized in FEF)
2. **Retryable/non-retryable**: same definition (transient vs deterministic) and same examples across every document that uses these terms
3. **State notation**: `[!]` blocked, `[✗]` failed, `[–]` canceled used identically wherever referenced
4. **Acceptance criteria**: D-3's three criteria (precommit, clean tree, output validation) referenced consistently when mentioned

For each discrepancy found: apply targeted fix (edit the document with the inconsistency to match the authoritative source — error-classification.md for taxonomy, task-failure-lifecycle.md for state notation, escalation-acceptance.md for acceptance criteria).

If no discrepancies found: confirm consistency in report, no edits needed.

Write report to: `plans/error-handling/reports/step-5.3-consistency.md`

**Expected Outcome**: Report documents which terminology checks passed, which had discrepancies, and what fixes were applied (or confirms no fixes needed). All 7 documents use consistent terminology.

**Error Conditions**:
- If a fundamental contradiction is found (two documents define the same term incompatibly and neither is clearly correct per the design outline), STOP and escalate to user

**Validation**:
- Report file exists at `plans/error-handling/reports/step-5.3-consistency.md`
- Report confirms all 4 consistency checks (fault/failure, retryable, state notation, acceptance criteria)
- If fixes applied: each fix targets specific document with specific change
