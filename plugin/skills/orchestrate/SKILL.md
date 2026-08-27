---
name: orchestrate
description: Execute prepared runbooks by dispatching standing agents against step files, with mechanical verification gates
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff:handoff", "/commit-commands:commit"]
---

# Execute Runbooks

Execute prepared runbooks by **delegation by reference**: dispatch a standing agent (`edify:artisan`, `edify:test-driver`, `edify:corrector`) with the path to a step file. The step file's `## Context` block names the design, outline, and shared-context artifacts the executor reads; the orchestrator's prompt carries paths, never content. Sonnet orchestrator coordinates step dispatch, post-step verification, remediation, and phase boundary reviews.

No agents are generated per plan. Nothing is installed into `.claude/agents/`, so agent discoverability never requires a session restart — `/runbook` still hands off to a fresh session, but for model tier and context budget, not discovery.

**Prerequisites:** Runbook prepared with `/runbook` (artifacts created by `prepare-runbook.py`)

## 1. Verify Runbook Preparation

```bash
ls -1 plans/<name>/orchestrator-plan.md
ls -1 plans/<name>/steps/step-*.md 2>/dev/null || true
```

**Required artifacts:**
- `plans/<name>/orchestrator-plan.md` — structured step list and phase-agent mapping
- `plans/<name>/steps/step-*.md` — absent only for all-inline runbooks

Missing orchestrator plan → STOP. Missing step files with only `INLINE` entries → valid all-inline runbook. Missing step files with step references → STOP.

The artifacts a step file names under `## Context` (`design.md`, `outline.md`, `common-context.md`) are written by `prepare-runbook.py` only when the plan has them. Their absence is not a preflight failure — a step file never names an artifact that does not exist.

## 2. Read Orchestrator Plan

```
Read plans/<name>/orchestrator-plan.md
```

**Parse header field:**
- `**Type:**` — `tdd` or `general`

**Parse `## Phase-Agent Mapping` table:** `| Phase | Agent | Type |`. The Agent column names the standing agent to dispatch for that phase's steps — `edify:artisan`, `edify:test-driver`, or `(orchestrator-direct)` for inline phases. Use this as the `subagent_type`; do not substitute another agent.

**Parse `## Steps` section:** Pipe-delimited entries:
- General: `- step-N-M.md | Phase P | model [| PHASE_BOUNDARY]`
- TDD: `- step-N-M-test.md | Phase P | model | TEST [| PHASE_BOUNDARY]`
- TDD: `- step-N-M-impl.md | Phase P | model | IMPLEMENT [| PHASE_BOUNDARY]`
- TDD: `- step-N-M-bootstrap.md | Phase P | model | BOOTSTRAP [| PHASE_BOUNDARY]`
- Inline: `- INLINE | Phase P | —`

**Execution mode:** STRICT SEQUENTIAL. One Task call per message. Steps modify shared state — parallel dispatch causes race conditions.

## 3. Execute Steps

For each entry in the `## Steps` list, branch by type:

### 3.0 Inline Execution (D-6)

Read the phase content from the orchestrator plan's `## Phase Files` section (path for Phase P). If no Phase Files section, read from the runbook directly. Execute edits directly — no Task dispatch.

1. Read target files, apply edits (Read → Edit/Write)
2. `just precommit` — fix failures, escalate if unfixable
3. Phase boundary review: apply the Proportionality rule in `plugin/fragments/review-requirement.md` — self-review via `git diff` only when ALL its self-review conditions hold (≤5 net lines across ≤2 files, additive or corrective, no control-flow/contract/behavioral change); otherwise delegate to corrector (Section 3.5). This is the one path where the orchestrator would review its own edits, so the threshold is the fragment's, not the orchestrator's judgment.
4. Commit inline phase changes

### 3.1 General Step Dispatch (D-2)

```
Agent tool:
  subagent_type: [Agent column for this phase in ## Phase-Agent Mapping]
  prompt: "Execute step from: plans/<name>/steps/<step-file>"
  model: [from step entry model field]
  name: "step-N-M"
  description: "Step N-M: [step file name]"
```

`name` is required for remediation: resuming an agent is a `SendMessage` to its
name (Section 3.4). Do NOT pass `max_turns` — the `Agent` tool has no such
parameter and rejects unknown ones (Section 4).

The prompt is the step-file path and nothing else. The step file's `## Context`
block names design, outline, and shared context; its `## Execution Contract`
footer carries the scope and clean-tree requirements. Do not paste artifact
content into the prompt.

After dispatch → Section 3.3 (verification).

### 3.2 TDD Cycle Dispatch (D-5)

Per TDD cycle (paired TEST + IMPLEMENT entries, optionally preceded by a BOOTSTRAP entry).

Tester and implementer are two **instances of the same standing agent** (`edify:test-driver`, per the Phase-Agent Mapping). The role separation is the `name` and the step file, not the agent type — the ping-pong is preserved because each instance keeps its own transcript.

**Step A — Dispatch tester:**
```
Agent tool:
  subagent_type: [Agent column for this phase — edify:test-driver]
  prompt: "Execute test spec from: plans/<name>/steps/<test-file>"
  model: [from step entry]
  name: "step-N-M-test"
```
The `name` is the resume handle — resume via `SendMessage` to that name.

A BOOTSTRAP entry, when present, dispatches to the same agent type ahead of the TEST entry, named `step-N-M-bootstrap`.

**Step B — RED gate:**
```bash
plugin/skills/orchestrate/scripts/verify-red.sh <test_file_path>
```
- Exit 0 (test fails) → RED confirmed, proceed
- Exit 1 (test passes) → resume tester to fix, or escalate

**Step C — Test review:**
```
Agent tool:
  subagent_type: "edify:corrector"
  model: sonnet
  name: "step-N-M-test-review"
  prompt: |
    Review test quality for Cycle N.M.

    **Scope:**
    - IN: the test files listed below — behavioral assertions, RED phase correctness
    - OUT: implementation details. Do NOT flag them.

    **Step file:** plans/<name>/steps/<test-file>
    **Changed files:** [git diff --name-only output]

    Fix all issues. Write report to: plans/<name>/reports/cycle-N-M-test-review.md
    Return filepath or "UNFIXABLE: [description]"
```
If UNFIXABLE → STOP.

**Step D — Dispatch implementer:**
```
Agent tool:
  subagent_type: [Agent column for this phase — edify:test-driver]
  prompt: "Execute implementation from: plans/<name>/steps/<impl-file>"
  model: [from step entry]
  name: "step-N-M-impl"
```
The `name` is the resume handle — resume via `SendMessage` to that name.

**Step E — GREEN gate:**
```bash
just test && plugin/skills/orchestrate/scripts/verify-step.sh
```
- Both pass → proceed
- Test failure → resume implementer to fix, or escalate
- Dirty tree / precommit failure → remediate (Section 3.4)

**Step F — Implementation review:**
Same dispatch as Step C with the scope inverted — IN: correctness, minimal implementation, GREEN phase compliance on the implementation files; OUT: test details. Name it `step-N-M-impl-review`, report to `plans/<name>/reports/cycle-N-M-impl-review.md`. If UNFIXABLE → STOP.

**Agent resume across cycles:** Resume the tester instance for subsequent TEST steps (preserves test context). Resume the implementer instance for subsequent IMPLEMENT steps (preserves codebase context). Launch fresh when a resume fails or the resumed agent returns without progress — the orchestrator cannot observe an agent's message count, so there is no turn-based cutoff. Correctors are never resumed — each review is independent.

### 3.3 Post-Step Verification

```bash
plugin/skills/orchestrate/scripts/verify-step.sh
```

- Exit 0 (CLEAN) → proceed to phase boundary check (Section 3.5)
- Exit 1 (DIRTY/SUBMODULE/PRECOMMIT) → remediate (Section 3.4)

### 3.4 Post-Step Remediation (D-3)

**Resume step agent** — it has context for fixing its own issues:
```
SendMessage:
  to: [name given to the step agent at spawn]
  message: "Your step left uncommitted changes or precommit failures. Fix and commit."
```
A send resumes the agent from its transcript. This requires that the step agent
was spawned with an explicit `name` — see 3.1. There is no `resume` parameter on
`Agent`; naming at spawn time is what makes resumption possible.

Resume once. If the resumed agent returns without fixing the issue, do not resume again — launch fresh.

**If resume fails or the resumed agent made no progress** — delegate recovery to fresh sonnet agent:
```
Agent tool:
  subagent_type: "edify:artisan"
  model: sonnet
  prompt: "[step file reference, git diff, git status, error output] Fix lint and commit issues."
```
Recovery is mechanical (lint-clean + git-clean). No design/outline context needed.

**After any remediation** — note the RCA follow-up (`Step N dirty tree — [brief description]`) in the run summary; the default exit (`/handoff:handoff`) carries it into the task frame.

**If recovery fails** — escalate to user with full context (Section 4).

### 3.5 Phase Boundary

Detect phase boundaries via the `PHASE_BOUNDARY` marker in the orchestrator plan step entry (or final step):

```bash
just precommit
git diff --name-only
```

**Delegate checkpoint to corrector:**
```
Agent tool:
  subagent_type: "edify:corrector"
  model: sonnet
  name: "phase-P-corrector"
  prompt: |
    Phase P Checkpoint

    **First:** Run `just dev`, fix any failures, commit.

    **Scope:**
    - IN: [from Phase Summaries section]
    - OUT: [from Phase Summaries section]

    **Design reference:** plans/<name>/design.md
    **Outline:** plans/<name>/outline.md
    **Shared context:** plans/<name>/common-context.md
    **Review recall:** `Skill(skill: "edify:recall", args: "plans/<name> — <topic derived from phase scope>")`
    **Changed files:** [git diff --name-only output]

    Fix all issues. Write report to: plans/<name>/reports/checkpoint-P-review.md
    Return filepath or "UNFIXABLE: [description]"
```

Name only the reference artifacts that exist — the same three a step file's `## Context` block names. Omit a line rather than pointing the corrector at a missing file.

Read report. If UNFIXABLE → STOP and escalate. Otherwise commit checkpoint, continue.

**Final checkpoint** adds lifecycle audit: verify all stateful objects (MERGE_HEAD, staged content, lock files) cleared on success paths.

**Template enforcement:** IN/OUT scope lists must be non-empty. Changed files list must be present. Empty fields → STOP before delegating.

### 3.6 Refactor Dispatch

After any corrector review (phase checkpoint, test review, or implementation review), check the report for refactoring signals:

**Trigger:** Corrector report contains complexity warnings (e.g., "REFACTOR-NEEDED", file exceeds line limits, high cyclomatic complexity, duplicated patterns across files).

**Dispatch:**
```
Agent tool:
  subagent_type: "edify:refactor"
  model: sonnet
  name: "refactor-phase-P"
  prompt: "Refactor flagged files: [files from corrector report]. Warnings: [quoted warning text]. Design reference: plans/<name>/design.md"
```

The refactor agent applies deslop directives (factorization-before-splitting) and returns `success`, `escalated: [reason]`, or `error: [reason]`. On `escalated` → note the opus-level refactoring follow-up in the run summary. On `error` → log and continue (refactoring is advisory, not blocking).

## 4. Error Escalation (D-4)

**2-level model:** Sonnet orchestrator handles execution-level issues (missing files, failed commands, dirty tree). Design-level issues escalate to user.

**Escalation prompt:**
```
Diagnose and fix from step N:
Error: [error message]
Step: [step objective]
Read step at: [step-path]
Write diagnostic to: plans/<name>/reports/step-N-diagnostic.md
Return: "fixed: [summary]" or "blocked: [what's needed]"
```

**Acceptance criteria:** Every resolution must pass precommit, leave clean tree, validate against step criteria.

**Execution bounds:** none currently enforceable. The `Agent` tool has no `max_turns` parameter and no duration bound, and passing one is rejected. Both spinning and hanging guards are platform gaps; see `plugin/fragments/escalation-acceptance.md`. A runaway agent has no in-band stop — the orchestrator's only recourse is the user.

## 5. Progress Tracking

Log each step: `Step N-M: [name] - completed` or `Step N-M: [name] - failed: [error]`

**Detailed tracking:** Read `references/progress-tracking.md` for optional progress file format.

## 6. Completion

```bash
git diff --name-only $(git rev-list --max-parents=0 HEAD | head -1)..HEAD
```

1. **Final review:** If multi-phase, phase boundary correctors already ran. Single-phase: delegate to `edify:corrector` with the reference artifacts (design, outline, shared context) and changed files. Report to `plans/<name>/reports/review.md`.
2. **TDD audit:** If `**Type:** tdd`, delegate to `edify:tdd-auditor`. Report to `plans/<name>/reports/tdd-process-review.md`.
3. **Deliverable review:** Name the follow-up in the run summary: `/deliverable-review plans/<name>` (opus, fresh session). The default exit (`/handoff:handoff`) captures it into the task frame from context; this skill never writes `.claude/handoff-task.md` itself.

There is no agent cleanup step. `prepare-runbook.py` installs nothing into `.claude/agents/`; the plan's generated artifacts all live under `plans/<name>/` and are part of the commit history.

## Continuation

Read `plugin/fragments/continuation-passing.md` and follow its §Consumption
Protocol as the final action of this skill; on failure, its §Error Propagation.
This skill has no routing-dependent prepend — step 2 applies unmodified.

## References

- **Verification scripts:** `plugin/skills/orchestrate/scripts/verify-step.sh`, `verify-red.sh`
- **Common scenarios:** `references/common-scenarios.md`
- **Progress tracking:** `references/progress-tracking.md`
- **Continuation:** `plugin/fragments/continuation-passing.md`
