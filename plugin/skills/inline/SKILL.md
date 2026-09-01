---
name: inline
description: >-
  Sequence inline execution lifecycle: pre-work, execute, post-work.
  Triggers on /inline, "execute inline", "run task", or when /design
  routes execution-ready work. Wraps corrector dispatch, triage feedback,
  and deliverable-review chaining.
allowed-tools: Agent, Read, Write, Edit, Bash, Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff:handoff", "/commit-commands:commit"]
---

# Inline Execution Lifecycle

Sequence the lifecycle for execution-ready work: context loading, implementation, corrector review, triage feedback, deliverable-review chaining. Replaces ad-hoc execution sequences in /design Phase B/C.5.

Covers direct and delegated execution — same lifecycle, different scale. Work that has a runbook uses /orchestrate; this skill never consumes a runbook.

## Entry Points

| Entry | Args pattern | Caller | Pre-work |
|-------|-------------|--------|----------|
| Default | `plans/<job>` | Cold start (new session) | Full |
| Execute | `plans/<job> execute` | /design (context loaded) | Skip |

Check for `execute` token in args → chained invocation (skip Phase 2). Absent → cold start (full workflow).

**State which entry path was taken, in one line, before Phase 1.** The token is the only signal distinguishing the two, and its absence fails open: a chained call that loses the token silently re-runs a recall pass the caller already did. That costs tokens and is invisible in the output unless the path is named. If the run announces "cold start" immediately after `/design` chained into it, the token was dropped — treat that as a caller defect, not as a legitimate cold start.

**Why the artifact cannot replace the token:** `plans/<job>/recall-artifact.md` exists on disk in both cases. It records what an upstream phase selected, not whether those files are in *this* session's context — a genuine cold start must still Read them. Presence of the artifact is therefore not evidence that Phase 2 is redundant.

## Phase 1: Entry Gate

**Git state (D+B anchor):**

```bash
git status --porcelain
```

Non-empty → STOP: "Dirty tree. Commit or stash before /inline."

```bash
just precommit
```

Failure → STOP: "Precommit failing. Fix before /inline."

**Capture baseline** — before any edits:

```bash
BASELINE=$(git rev-parse HEAD)
```

Store for Phase 4b (triage feedback script input).

## Phase 2: Pre-Work (cold start only)

Skip entirely when entry point is `execute` — caller has loaded all context.

### 2.1 Brief Check

Read `plans/<job>/brief.md` if present (cross-tree context from other sessions). In worktrees: `git show main:plans/<job>/brief.md 2>/dev/null`.

### 2.2 Recall (D+B anchor — tool call required)

`Skill(skill: "edify:recall", args: "plans/<job> — execution patterns for this task")`

Patterns for implementing this, not classifying it.

### 2.3 Reference Loading

Load domain-relevant skills and reference files specified in the task description (e.g., `plugin-dev:skill-development` for skill work, `plugin/fragments/continuation-passing.md` for cooperative skills).

## Phase 3: Execute

Perform implementation: edits, TDD for behavioral code, prose changes. This skill provides lifecycle wrapper only — execution approach comes from caller's design/plan.

### Direct Execution

Edits performed in current session. No delegation.

### Delegated Execution

When a task needs a sub-agent (self-modifying work with behavioural code, D-39), compose each dispatch per `plugin/skills/orchestrate/references/dispatch-composition.md` — task text inline, design and recall artifact by path, scope IN/OUT, done criteria, report path, a `name`, and the model assignment with its artifact-type override. Parent does the cognitive work (curating what the dispatch sees); child does the mechanical work — sub-agents have no parent context.

**Post-step verification (single compound command — do not split):**

```bash
git status --porcelain && just lint
```

After each delegated step. Dirty tree or lint failure → diagnose before continuing.

**No mid-execution checkpoints.** Corrector (Phase 4a) is the sole semantic review. Post-step lint catches mechanical issues. Triage feedback (Phase 4b) collects uninterrupted execution data. Revisit after 10+ delegated executions show compounding drift.

## Phase 4: Post-Work

### 4a: Review Gate (D+B anchor)

**Both paths require a tool call on `plans/<job>/reports/`. Neither is skippable.**

#### Path A: Review Dispatch (default)

Route changed files to the appropriate reviewer per `plugin/fragments/review-requirement.md` routing table.

**Dispatch process:**
1. List changed files: `git diff --name-only $BASELINE`
2. Group by artifact type (code/tests/plans, skill definitions, agent definitions, design documents)
3. Look up reviewer per group from routing table
4. Dispatch each group to its reviewer using `references/review-dispatch-template.md` for prompt structure

**Two dispatch patterns:**
- **Fix-capable reviewers** (corrector, agent-creator, design-corrector): Delegate, read report, grep UNFIXABLE. Agent applies fixes directly.
- **Report-only reviewers** (skill-reviewer): Delegate, read report, apply fixes in calling session. Agent has Read plus Bash `rg` only.

**Common fields per dispatch:**
- **Scope:** uncommitted changes for this artifact group — implementation only
- **Design context:** `plans/<job>/outline.md` or `design.md`
- **Recall context:** the plan directory, per `references/review-dispatch-template.md` — the reviewer runs its own recall
- **Report:** `plans/<job>/reports/review.md` (or `review-<type>.md` when multiple groups)

Planning artifacts → runbook-corrector (not this gate).

**Structural proof (D+B anchor):** After review completes, verify report exists:

```
Read(plans/<job>/reports/review.md)
```

This Read proves reviewer produced output. Without it, Phase 4b cannot proceed.

**Handle result:** Read each review report. If UNFIXABLE issues present → STOP, surface to user with report path. Do not proceed to 4b until all issues are resolved or accepted.

#### Path B: Review Skip (gated escape hatch)

When review is genuinely unnecessary (trivial task-frame-only edits, plan artifact cleanup), skip is permitted — but requires an auditable artifact:

```
Write(plans/<job>/reports/review-skip.md)
```

Content must include: what was changed, why review adds no value for this specific change, what verification was performed instead. The justification must be specific enough to survive deliverable-review scrutiny.

**Skip is not confidence-gated.** "Scope is small" or "well-tested" are not valid skip justifications — review exists precisely to catch issues confidence misses.

### 4b: Triage Feedback

```bash
plugin/bin/triage-feedback.sh plans/<job> $BASELINE
```

Read script output. On divergence message → surface inline. On match or no-classification → proceed silently.

### 4c: Deliverable-Review Handoff

Final phase before continuation. Name the follow-up in the final report: `/deliverable-review plans/<job>` (opus, fresh session). The default exit (`/handoff:handoff`) captures it into the task frame from context; this skill never writes `.claude/handoff-task.md` itself.

## Continuation

Read `plugin/fragments/continuation-passing.md` and follow its §Consumption
Protocol as the final action of this skill; on failure, its §Error Propagation.
This skill has no routing-dependent prepend — step 2 applies unmodified.
