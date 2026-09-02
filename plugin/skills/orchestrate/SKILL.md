---
name: orchestrate
description: Execute a proofed runbook (plans/<job>/runbook.md) by dispatching standing agents per item. Triggers on /orchestrate or when /runbook hands off in a fresh session.
allowed-tools: Agent, Read, Edit, Bash, SendMessage, TaskOutput
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff:handoff", "/commit-commands:commit"]
---

# Execute Runbooks

Execute `plans/<job>/runbook.md` by dispatching standing agents
(`edify:artisan`, `edify:test-driver`, `edify:corrector`, `edify:refactor`,
`edify:tdd-auditor`).
The orchestrator reads the runbook and composes every dispatch prompt itself,
live, per `references/dispatch-composition.md` — item text inline, design and
recall artifact by path. Plan deviation is handled by re-composing the next
prompt, never by regenerating artifacts.

## 1. Load the Runbook

```
Read plans/<job>/runbook.md
Read plans/<job>/design.md   (or outline.md, whichever the plan has)
```

A missing runbook fails on the Read — there is no preflight. Note the recall
artifact path (`plans/<job>/recall-artifact.md`) for dispatch composition.

**Execution mode:** STRICT SEQUENTIAL. One dispatch per message — items
modify shared state, and parallel dispatch causes race conditions.

## 2. Execute Items

Walk the phases in order. Per item, branch on the phase type.

### 2.1 Inline Items

The orchestrator executes the item itself — Read targets, apply edits,
`just precommit`, commit. No dispatch.

Review follows the Proportionality rule in
`plugin/fragments/review-requirement.md`: self-review via `git diff` only
when ALL of that fragment's self-review conditions hold; otherwise dispatch
`edify:corrector` (Section 4 checkpoint form). This is the one path where
the orchestrator would review its own edits, so the threshold is the
fragment's, not the orchestrator's judgement.

### 2.2 General Items

One dispatch composed per `references/dispatch-composition.md` —
`edify:artisan`, or `edify:corrector` where the item is itself a review.
Then post-item verification (Section 3).

### 2.3 TDD Items

A tdd item lists behaviour slices. Execute slice `N.M/k` as four dispatches,
each composed per `references/dispatch-composition.md`:

**(a) RED** — `edify:test-driver`, RED mode named in the prompt. For k=1 it
stubs the SUT importable but inert, writes the slice's tests, runs them, and
confirms every test fails on its assertion; for k>1 it does not touch the
SUT. No commit — the tests stay uncommitted in the tree; the report carries
the per-test output, and the dispatch ends there.

**(b) Test review** — `edify:corrector` (opus). Scope IN: this slice's test
files plus the RED report. First check is mechanical: every listed test
FAILED on an assertion — none PASSED, none ERROR. Then wrong-reason hunting
per the corrector's own criteria. Fix-all on tests, re-run to confirm still
red. UNFIXABLE → STOP.

**(c) GREEN** — `edify:test-driver`, GREEN mode named in the prompt. Makes
the tests pass one at a time, full suite at the end; commits once per slice,
`<type>: Item N.M/k — <title>`, carrying tests and implementation together
with the suite green. The type is the executor's choice (see
`references/dispatch-composition.md` §Prompt contents) — nothing keys on it.
No commit ever leaves the suite red. The GREEN report names the slice
commit's hash.

**(d) Code review** — `edify:corrector` (opus). Scope IN: the
implementation files. May run the slice's tests once against an in-place
mutated SUT (save, mutate, run, restore — never relocate the tests) and
report whether they redded. Applies fixes; flags in-scope-unfixable
refactorings (module split, new abstraction). UNFIXABLE → STOP.

**After the slice:**

1. **Commit the review fixes:** the corrector never commits. If (d) changed
   anything, the orchestrator commits it — `<type>: Item N.M/k —
   code-review fixes` — before the post-item verification of Section 3, the
   same step §4 takes at a phase boundary. Nothing to commit → go straight
   to verification.
2. **Refactor on signal:** if (d) flagged a refactoring, dispatch
   `edify:refactor` before the next slice's RED, so later tests target the
   refactored shape. It commits its own refactoring commit on a clean tree.
   On `escalated: <reason>` → re-dispatch `edify:refactor` once with model
   opus (the Agent tool's `model` override) and the reason quoted in the
   prompt; a second `escalated` goes in the run summary and execution
   continues. On `error` → log and continue.
3. **List revision:** revise the remaining slices' test lists in
   `runbook.md` from what this slice revealed, or record "List revision:
   none" in the run summary. The orchestrator commits `runbook.md` edits
   after the slice — plan-as-executed vs plan-as-written stays a `git diff`.

## 3. Post-Item Verification

After every dispatch whose work is committed — GREEN (c), code review (d)
once the orchestrator has committed its fixes, and any general item. Not
after (a)/(b), where uncommitted tests are the designed state:

```bash
plugin/skills/orchestrate/scripts/verify-step.sh
```

- Exit 0 (CLEAN) → proceed
- Exit 1 → remediate: resume the named agent once
  (`SendMessage to: <name>`, "Your dispatch left uncommitted changes or
  precommit failures. Fix and commit."). If the resume fails or returns
  without progress, dispatch a fresh `edify:artisan` (sonnet) with the git
  status, diff, and error output — recovery is mechanical, no design context
  needed. If recovery fails, escalate to the user. After any remediation,
  note the RCA follow-up in the run summary.

## 4. Phase Boundary

At the end of each phase:

```bash
just precommit
git diff --name-only
```

Dispatch `edify:corrector` (checkpoint form, composed per
`references/dispatch-composition.md`): scope IN/OUT from the phase's items,
design and recall artifact by path, changed-files list, report path from that
reference's §Prompt contents rule under the dispatch name
`phase-P-corrector`. IN/OUT lists must be non-empty and the changed-files
list present — empty fields → STOP before delegating. UNFIXABLE → STOP and escalate. Otherwise commit and continue.

The **final checkpoint** adds a lifecycle audit: verify all stateful objects
(MERGE_HEAD, staged content, lock files) cleared on success paths.

## 5. Escalation Rules

**2-level model:** the orchestrator handles execution-level issues (missing
files, failed commands, dirty tree); design-level issues escalate to the
user. Every resolution must pass precommit, leave a clean tree, and satisfy
the item's own criteria.

- **Unexpected result, no error** → stop and report to the user: planning
  assumptions were wrong.
- **Report file missing after an agent completes** → ask the agent for the
  report (resume by name); if that fails, investigate before proceeding.
- **Same error from two dispatches** → stop and report the pattern: systemic
  issue, not a one-off.
- **Agent never returns** → check with TaskOutput; hanging → stop the task
  and escalate. There is no in-band turn or duration bound
  (`plugin/fragments/escalation-acceptance.md`) — a runaway agent's only
  stop is the user.
- **Resuming after a context ceiling or kill** → find the last checkpoint
  commit in `git log`, run that checkpoint's verification, build the
  inventory of remaining work from its output, and resume from the next
  item. Do not use `just precommit` as a state-assessment tool — it is a
  pass/fail gate, not a diagnostic.

## 6. Completion

1. **Final review:** single-phase runs get one `edify:corrector` dispatch
   over the whole diff (phase-boundary checkpoints already covered
   multi-phase runs), dispatch name `final-review`.
2. **TDD audit:** if any tdd item ran, dispatch `edify:tdd-auditor`,
   dispatch name `tdd-audit`. Its inputs are the RED, GREEN and review
   reports of every slice, with the session's `subagents/` transcripts as
   fallback where a report is missing; git serves only to confirm and diff
   the commit a report names.
3. **Run summary:** close with the run summary in context — per item its
   dispatches (`item-N-M`, `item-N-M-s<k>-red`, …), each report path, each
   remediation RCA, the list revisions, and the follow-up:
   `/deliverable-review plans/<job>` (opus, fresh session). The default exit
   (`/handoff:handoff`) carries it into the task frame; this skill never
   writes `.claude/handoff-task.md` itself.

## Continuation

Read `plugin/fragments/continuation-passing.md` and follow its §Consumption
Protocol as the final action of this skill; on failure, its §Error
Propagation. This skill has no routing-dependent prepend — step 2 applies
unmodified.

## References

- **Dispatch composition:** `references/dispatch-composition.md`
- **Verification script:** `plugin/skills/orchestrate/scripts/verify-step.sh`
- **Agent behaviour rules:** `plugin/fragments/delegation.md`
- **Continuation:** `plugin/fragments/continuation-passing.md`
