---
name: build
description: >-
  Execute planned work — a proofed runbook (plans/<job>/runbook.md), or a
  design or outline that has no runbook. Triggers on /build,
  "execute the runbook", "execute this plan", or when /design or /runbook
  hands work off for execution.
allowed-tools: Agent, Read, Write, Edit, Bash, Skill, SendMessage, TaskOutput, TaskStop
user-invocable: true
---

# Build

Run the execution lifecycle over planned work: entry gate, context, item walk,
finish. The work may be a proofed runbook or a design with no runbook — same
lifecycle either way.

A lean hub. Subagent ceremony where the work needs it, in-session where it does
not: whether an item is delegated is decided per item at dispatch time, never by
a property of the plan. The steps that fire once — a phase boundary, finishing
the job — are reference nodes, each named below with the condition that reaches
it. A run spanning several sessions loads only what its own session hits.

## 1. Load the work

```bash
ls plans/<job>
```

Take the first that exists:

1. `plans/<job>/runbook.md` — phased, typed items. Also Read
   `plans/<job>/design.md` or `outline.md`, whichever the plan has.
2. `plans/<job>/design.md` or `plans/<job>/outline.md` — work with no runbook.
   The design itself is the work.
3. Neither — take the task from the invocation.

Existence is tested, not discovered by a failing Read: a missing runbook is a
fallback, not an error. Note the recall artifact path
(`plans/<job>/recall-artifact.md`) for dispatch composition, and the job
directory — Section 5 writes under `plans/<job>/reports/`.

**Execution mode:** STRICT SEQUENTIAL. One dispatch per message — items modify
shared state, and parallel dispatch causes race conditions.

## 2. Entry gate (D+B anchor)

```bash
plugin/skills/build/scripts/verify-step.sh
```

- Exit 0 (CLEAN) → proceed.
- Exit 1 with `DIRTY:` → STOP: "Dirty tree. Commit or stash before /build."
- Exit 1 with `PRECOMMIT:` → STOP: "Precommit failing. Fix before /build."
- Exit 2 → STOP: the script itself failed, so there is no verdict.

Run it with `dangerouslyDisableSandbox: true`, here and at every other call
site; a sandboxed run yields no verdict.

This script is the skill's single definition of a clean tree; Section 4 and
`references/phase-boundary.md` call the same one. A bare
`git status --porcelain` here would refuse states the later gates are documented
to tolerate.

**Capture the baseline** — before any edits:

```bash
mkdir -p tmp && git rev-parse HEAD > tmp/build-baseline
```

A file, not a shell variable: each Bash call is its own shell, so a `BASELINE=`
assignment here is gone by Section 5. `tmp/` is gitignored, so the baseline
never enters the diff it defines. Section 5 reads it back with
`$(cat tmp/build-baseline)`.

## 3. Pre-work

Unconditional — run it even when `/design` chained straight in with context
already loaded. The alternative is a caller-supplied token asserting the context
is warm, and such a token fails open and invisibly: a chained call that drops it
re-runs a recall pass with nothing in the output saying so. One cheap duplicate
recall is the cheaper side of that trade.

### 3.1 Brief check

Read `plans/<job>/brief.md` if present — cross-tree context from other sessions.
In worktrees: `git show main:plans/<job>/brief.md`.

### 3.2 Recall (D+B anchor — tool call required)

`Skill(skill: "edify:recall", args: "plans/<job> — execution patterns for this task")`

Patterns for implementing this, not for classifying it.

### 3.3 Reference loading

Load the domain-relevant skills and reference files the work names — e.g.
`plugin-dev:skill-development` for skill work.

## 4. Execute

Walk the work in order: a runbook's phases and items, or an outline's or
design's items. Per item, decide **at dispatch time** whether to do it in
session or delegate — the batching rule: an agent offsets context churn in this
session, so one agent owning a run of mechanical edits is right where one agent
per edit is not. No type plays a part: §4.3 fires on the item carrying
`Slices:`, whether a runbook, an outline or a design holds it.

### 4.1 Direct execution

Read the targets, apply the edits, `just precommit`, commit.

Review is **not** the executor's judgement. Self-review via `git diff` only when
every self-review condition in `plugin/fragments/review-requirement.md`
§Proportionality holds; otherwise dispatch `edify:corrector` in its checkpoint
form. This is the one path where the executor would review its own edits, and
per-item choice makes it common — so the threshold is the fragment's.

### 4.2 Delegated execution

One dispatch: Read `references/dispatch-composition.md` and compose by it —
`edify:artisan`, or `edify:corrector` where the item is itself a review. The
parent does the cognitive work (curating what the dispatch sees); the child does
the mechanical work, since subagents have no parent context.

### 4.3 TDD items

**When the item carries `Slices:`** it carries nothing else to execute: Read
`references/tdd-slice.md` and execute each slice by it.

### 4.4 Post-item verification

After every dispatch whose work is committed — a slice's GREEN, a slice's code
review once its fixes are committed, and any general or directly executed item.
Not after RED or test review, where uncommitted tests are the designed state:

```bash
plugin/skills/build/scripts/verify-step.sh
```

- Exit 0 (CLEAN) → proceed.
- Exit 2 → the script itself failed, not the dispatch. Stop and report; do not
  remediate, since there is no established verdict to remediate against.
- Exit 1 → remediate: resume the named agent once (`SendMessage to: <name>`,
  "Your dispatch left uncommitted changes or precommit failures. Fix and
  commit."). If the resume fails or returns without progress, dispatch a fresh
  `edify:artisan` (sonnet) with the git status, diff and error output — recovery
  is mechanical, no design context needed. If recovery fails, escalate to the
  user. After any remediation, note the RCA follow-up in the run summary.

**Invent no further checkpoints.** A run's semantic reviews are exactly two —
the phase-boundary corrector below, where the work is a phased runbook, and
Section 5's review gate. Post-item verification catches everything mechanical
between them.

### 4.5 Phase boundary

**When the work came from a phased runbook and a phase has just ended:** Read
`references/phase-boundary.md` and follow it. Work with no runbook has no phases
and skips this.

## 5. Finish

**When every item in the work is done, and not before.** A run spanning several
sessions reaches this once, in its last one.

Read `references/finishing.md` and follow it: review gate, triage feedback,
completion. **Not skippable** — whichever way the branch below goes, it ends in
a tool call on `plans/<job>/reports/`.

The one branch this hub owns is the review gate's. Where review is genuinely
unnecessary — trivial task-frame-only edits, plan artifact cleanup — the review
dispatch is replaced by an auditable artifact:

```
Write(plans/<job>/reports/review-skip.md)
```

It must state what changed, why review adds no value for this specific change,
and what verification was performed instead, specifically enough to survive
deliverable-review scrutiny. **Skip is not confidence-gated:** "scope is small"
and "well-tested" are not justifications — review exists precisely to catch what
confidence misses. Triage feedback and completion still run.

## 6. Escalation

**2-level model:** execution-level issues (missing files, failed commands, dirty
tree) are handled here; design-level issues escalate to the user. Every
resolution must pass precommit, leave a clean tree, and satisfy the item's own
criteria.

- **Unexpected result, no error** → stop and report to the user: the planning
  assumptions were wrong.
- **Report file missing after an agent completes** → ask the agent for the
  report (resume by name); if that fails, investigate before proceeding.
- **Same error from two dispatches** → stop and report the pattern: a systemic
  issue, not a one-off.
- **Agent never returns** → check with `TaskOutput`; hanging → stop the task and
  escalate. There is no in-band turn or duration bound
  (`plugin/fragments/escalation-acceptance.md`) — a runaway agent's only stop is
  the user.

**When resuming after a context ceiling or a kill:** Read
`references/resuming.md` before assessing state.

## References

Each node names the condition that reaches it; none is loaded unconditionally.

- **`references/dispatch-composition.md`** — composing any dispatch prompt
- **`references/tdd-slice.md`** — §4.3, an item carrying `Slices:`
- **`references/phase-boundary.md`** — §4.5, end of a runbook phase
- **`references/finishing.md`** — §5, every item done
- **`references/review-dispatch-template.md`** — reviewer prompts, from
  `finishing.md` §1
- **`references/resuming.md`** — §6, resuming an interrupted run
- **`scripts/verify-step.sh`** — the clean-tree verdict, §2, §4.4, §4.5
- **`plugin/fragments/delegation.md`** — agent behaviour rules
