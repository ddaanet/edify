# Deliverable review, Layer 1: agentic prose (build-defects)

Range `d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`. The baseline is
`plans/build-defects/outline.md`, covering KD-1..KD-7, Items 2.1–2.9 and
Scope. The axes come from `docs/references/deliverable-review.md` D-56. Each
file was read whole as it stands and diffed over the range. I then grepped
`plugin/` for stale forms and checked the findings against
`plans/skill-reviews/reports/verify-inline.md` and `verify-orchestrate.md`.

**Counts:** Critical 0, Major 5, Minor 19.

## Conformance: item bullets

Every bullet of Items 2.1–2.9 has a deliverable.

| Item | Bullet | Status |
|---|---|---|
| 2.1 | `TaskOutput`/`TaskStop` dropped from `allowed-tools` | Done |
| 2.1 | §1 `<job>` from the invocation, resumed run re-invoked with it | Done |
| 2.1 | §2 DIRTY: three exemptions named, mask re-run routed to escalation.md | Done |
| 2.1 | §3.2 sentence | Done ("Select patterns for implementing this task, not for classifying it.") |
| 2.1 | §4.1 "checkpoint form" replaced | Done ("scoped to this item's changes, named `item-N-M`") |
| 2.1 | §4.2 review-item commit before §4.4 | Done |
| 2.1 | §4.4 case added | Done (and the phase-boundary corrector too) |
| 2.2 | verify-step run dropped, KD-1 base, "checkpoint-form" replaced, halt widened | Done |
| 2.3 | §1 scope per group share, UNFIXABLE validation, report-only second pass, verify-step before §2, §2 WARNING, one planning-artifact paragraph | Done |
| 2.4 | explicit Changed-files list, Constraints block, agent-definition criteria, report/return deferral, Field Rules pointer, routing pointer | Done |
| 2.5 | `review-<group>` in §Naming, second exception, UNFIXABLE inside report, `git commit -- <paths>`; test-driver and refactor | Done |
| 2.6 | mask re-run at head of exit-1, KD-4 procedure, remediation governs fragment, §Resuming KD-6 + KD-1 | Done |
| 2.7 | Changed files from `<base>`, never bare | Done (see m2 on the HEAD refinement) |
| 2.8 | §Dirty tree recovery defers per KD-5 | Done |
| 2.9 | one script owns the verdict, why `&&` fails, named by skill | Done |

Stale-form grep over `plugin/`:

- No bare `git diff --name-only` remains in prose. `plugin/bin/triage-feedback.sh` still has the working-tree form; see m18.
- No `checkpoint form` or `checkpoint-form` remains.
- `TaskOutput` appears nowhere.
- `TaskStop` appears only in `escalation-acceptance.md` §Timeout handling, as "unprobed", which is consistent with KD-4.
- `git clean -fd` appears only at the two KD-5 sites and in `deliverable-review/references/example-report.md`, which is an example and not in scope.
- No `git add -A` is prescribed anywhere.
- One pathspec-less orchestrator commit remains, in `tdd-slice.md`; see M3.

Every § citation in the listed files resolves to an existing heading or bold
label. One pre-existing citation is stale, in a file outside the list (m14).

The three surfaces read the same on both rules below:

- **KD-5, the dirty-tree rule.** `SKILL.md` §2, `escalation.md` §Post-item remediation and `escalation-acceptance.md` §Dirty tree recovery.
- **KD-7, the sandbox-mask re-run.** Re-run once, act on the re-run, and stop if it is annotated again.

`review-<group>` is used consistently in `dispatch-composition.md`,
`finishing.md` and the template. Its slug is not determined (m9).

The condensing in `SKILL.md` lost nothing load-bearing from §2. `finishing.md`
§1 and §2 carry the `$(cat tmp/build-baseline)` read-back and the "not from a
variable" reason. §3 loses only its cost argument. The 200-line cap did
displace the resume test out of the hub, though (M1).

## Major

### M1 — `plugin/skills/build/SKILL.md` §1 and §2, with `references/escalation.md` §Resuming after a context ceiling or a kill

**Axes:** determinism, functional correctness.

The hub's §1 says "A resumed run Reads `references/escalation.md` §Resuming before §2". §2's capture is skipped only "not on a resumed run, which keeps the file". The test for *being* resumed lives only in escalation.md: "A run is resumed when the invocation says so, or when `plans/<job>/reports/` already holds this run's reports". escalation.md is read only after the run is already known to be resumed, so the criterion cannot be reached from the hub.

A fresh-session `/build plans/<job>` whose invocation does not say "resume" gets no rule telling it to check `reports/`. It then runs §2's `git rev-parse HEAD > tmp/build-baseline`. That shrinks the review gate's diff (`finishing.md` §1), triage's baseline and phase 1's base to the post-resume commits. Every earlier item silently drops out of review.

`review-skill.md` records this placement as deliberate, "keeps `SKILL.md` at its 200-line hard cap" (S3). That makes this the load-bearing cost of the cap.

The unscoped `tmp/build-baseline` compounds it. It is tracked as (b) in `.claude/handoff-todo.md`, and the resume test there is to key on the per-job file. Until then, the gap is live.

### M2 — `plugin/skills/build/references/escalation.md` §Resuming after a context ceiling or a kill, with `references/phase-boundary.md`

**Axes:** functional completeness, functional correctness.

Step 1 finds "the last committed item or phase-boundary commit". Step 3, however, builds the inventory as "the work's items minus those step 1 shows landed". Phase boundaries are not items, so a run killed after a phase's last item commit but before its `phase-<P>-corrector.md` commit resumes at phase P+1's first item. Phase P's boundary review is skipped.

KD-1's premise, "That commit always exists, because the phase-boundary commit always happens", then fails at P+1's boundary. `git log --diff-filter=A --format=%H -- plans/<job>/reports/phase-<P>-corrector.md` prints nothing. `phase-boundary.md` gives no instruction for an empty resolution.

Substituting an empty base yields `git diff --name-only HEAD`, a working-tree diff. That diff lists modified exempt paths such as `.claude/handoff-task.md` and is not empty, so it can pass the empty-field STOP with the wrong list. Which substitution an orchestrator makes is unverified.

Two edge cases share this cause:

- A second run of the same job modifies an existing `phase-<P>-corrector.md` rather than adding it, so the query returns the prior run's commit.
- A report added more than once returns several hashes.

Otherwise the P>1 resolution is executable as written.

### M3 — `plugin/skills/build/references/tdd-slice.md` §After the slice (not in the review list)

**Axes:** consistency (KD-7), functional correctness.

Step 1, the orchestrator's code-review commit, says only "Stage those paths by name." It does not name `git commit -- <paths>`. Step 3's `runbook.md` list-revision commit gives no form either.

KD-7's safety argument is stated in the outline and in the `verify-step.sh` comment: "commits them with `git commit -- <paths>`, so exempt dirt never enters a commit, even when already staged". That argument needs every committing path to use that form. These two paths are the remaining exceptions.

`tdd-audit.md` records the staged-exempt-dirt U-DESIGN as still open. With a pathspec-less `git commit`, a staged `.claude/handoff-task.md` would ride the code-review commit. `SKILL.md` §4.1/§4.2, `phase-boundary.md`, `finishing.md` §1 and both agents were updated. This file was not, because no outline item names it.

### M4 — `plugin/skills/build/references/finishing.md` §2 Triage feedback and §3 Completion

**Axes:** functional completeness; consistency with KD-1 and KD-2.

After §1's commit and `verify-step.sh`, nothing commits or verifies what the later steps leave:

- §2's `triage-feedback.sh` appends to `plans/reports/triage-feedback-log.md`.
- §3.1 dispatches a `final-review` corrector, which "commits nothing" per `dispatch-composition.md` item 4 and may apply fixes.
- §3.2's `tdd-audit` writes a report.
- `SKILL.md` §5's `Write(plans/<job>/reports/review-skip.md)` path has no commit either.

The run ends on an uncommitted tree, and the next `/build` entry gate reports DIRTY. This is the same defect class as orch M4 and inline m12, which this job fixed for §4 and §1. Evidence: this job's own `72f92c3a` ("build-defects §5 — TDD audit and triage log entry") committed `tdd-audit.md` and the triage log line ad hoc.

The gap is outside the outline's items but inside KD-2's "review dispatch commits nothing" consequence.

### M5 — `plugin/skills/build/SKILL.md` §4.1 Direct execution

**Axes:** vacuity; functional correctness.

The item is now explicitly committed first: "`just precommit`, then stage the edited paths and commit them with `git commit -- <paths>`". Then comes "Self-review via `git diff` only when every self-review condition … holds".

After the commit, `git diff` is empty, and so is the fragment's own "Run `git diff HEAD`" in `review-requirement.md` §Self-review process. The self-review path therefore passes vacuously. It is the same wound KD-1 fixed for the phase gate, a bare diff read after a commit. §4.1 itself says "per-item choice makes it common".

The defect is pre-existing. `review-skill.md` recorded it under "Noted, not flagged". I found no task tracking it in `.claude/handoff-todo.md`, which D-58 counts as unresolved.

## Minor

### m1 — `plugin/skills/build/references/finishing.md` §1 Review gate step 1, and `references/phase-boundary.md` opening paragraph

**Axis:** accuracy.

The two claims are:

- finishing.md: "apart from them the tree holds only paths `verify-step.sh` exempts, and no commit carries those".
- phase-boundary.md: "taken against `HEAD`, not the working tree, so the paths `verify-step.sh` exempts stay out".

Exempt paths are committed within a run by `/handoff` and by memory pointer commits. This range's own diffstat carries `.claude/handoff-task.md`, `.claude/handoff-todo.md` and `memory`, so `<base> HEAD` lists them and routes them to reviewers. The `HEAD` form excludes uncommitted exempt dirt only. The text overstates it.

### m2 — `plugin/fragments/review-requirement.md` §Execution Context, Changed files

**Axis:** consistency (KD-1 refinement).

The text gives "from `git diff --name-only <base>` … under `/build`, the run's or phase's base as `…/phase-boundary.md` resolves it". Every `/build` surface uses `git diff --name-only <base> HEAD`.

`review-fragments.md` (issue 4) kept the working-tree form deliberately, for `/review` of uncommitted work. The sentence still pairs a `/build` pointer with the non-`/build` command form. A reader under `/build` gets the working-tree form from this line.

### m3 — `plugin/skills/build/references/phase-boundary.md`, the dispatch paragraph

**Axes:** consistency (KD-2); determinism.

- "UNFIXABLE → STOP and escalate" skips the `review-requirement.md` §UNFIXABLE Detection Protocol validation. KD-2 states that validation generally, and `finishing.md` §1 applies it.
- The UNFIXABLE branch ends at "resume `phase-P-corrector` by `SendMessage`". The phase commit that KD-1's P>1 base depends on is sequenced only by "Otherwise commit and continue". The "always happens" clause implies the commit but does not order it after the resume.

### m4 — `plugin/skills/build/references/finishing.md` §1 Structural proof, and `references/review-dispatch-template.md` §Report-only variant

**Axis:** determinism.

The protocol's per-issue validation requires "subcategory code (U-REQ, U-ARCH, or U-DESIGN)" and an "investigation summary showing all 3 gates checked". The report-only prompt asks only "Mark a blocker "UNFIXABLE: [description]"". Every report-only UNFIXABLE therefore fails validation.

The protocol's remedy, "resume corrector for reclassification", names an agent that did not produce the finding.

### m5 — `plugin/skills/build/references/escalation.md` §Post-item remediation, exit-1 bullet

**Axes:** scope boundaries, determinism.

`SKILL.md` §2 routes the entry gate's mask re-run here. The bullet says "The re-run's verdict is the one acted on, at the entry gate as after an item". Its next sentence is "Any other exit 1 → remediate".

At the entry gate the rule is `SKILL.md`'s STOP ("Dirty tree. Commit or stash before /build."), not remediation. The section's lead-in, "`scripts/verify-step.sh` after a dispatch whose work is committed:", scopes it to post-item anyway. A reader arriving from §2 can remediate the user's pre-existing dirt with a fresh `edify:artisan`.

### m6 — `plugin/skills/build/references/escalation.md` §Post-item remediation closing paragraph, and `plugin/fragments/escalation-acceptance.md` §Dirty tree recovery

**Axis:** determinism.

"the orchestrator never cleans up in its own session" and "`git checkout -- . && git clean -fd` runs only where no agent owns the dirt, and only after the user confirms it" leave the command's actor unstated.

No step in the exit-1 chain reaches "no agent owns the dirt". The no-named-agent case goes to "the fresh `edify:artisan`".

That the command also destroys KD-7 exempt dirt is tracked as (a) in `.claude/handoff-todo.md`. The actor ambiguity is not.

### m7 — `plugin/skills/build/references/escalation.md` §Escalation, "Agent never returns"

**Axis:** determinism.

The bullet reads "check its report path, `git log` and the tree … Then resume it by name once, and then escalate". It gives no branch for the check finding the report written or the commit landed, where the agent has in effect returned. It also gives no branch for a resume that produces the report.

### m8 — `plugin/skills/build/references/dispatch-composition.md` §Prompt contents item 5

**Axis:** determinism.

For the report-only reviewer, the session "resumes it by name for the next part while a part ends `CONTINUED`, and writes the parts to the assigned path only once one ends `END OF REPORT`". A part ending in neither marker is exactly the truncation the markers exist to expose, and it leaves the loop with no instruction.

### m9 — `plugin/skills/build/references/dispatch-composition.md` §Naming and resumption

**Axes:** determinism, naming.

The rule is "`<group>` a lowercase one-word slug for the artifact group `finishing.md` §1 routed". finishing.md §1's groups are "code/tests/plans, skill definitions, agent definitions, design documents", which do not map mechanically to one word.

This run produced `review-code`, `review-skill`, `review-agents` and `review-fragments`. The names mix singular and plural, and "fragments" is not a routing group. This is tracked as (c) in `.claude/handoff-todo.md`.

### m10 — `plugin/skills/build/references/dispatch-composition.md` §Naming and resumption, against `finishing.md` §3

**Axis:** consistency. Pre-existing.

Naming describes `final-review` as "a single-phase run's closing corrector". finishing.md §3.1 triggers it for "a run whose review was skipped, and one whose routing left a group of changed files unreviewed".

### m11 — `plugin/skills/build/references/review-dispatch-template.md` §Example: Skill Creation Task

**Axis:** consistency.

The example dispatches a skill-definition group with the fix-capable §Template: "Fix all issues", a `Skill(skill: "edify:recall", …)` recall line, and "Write report to". The routing table sends skill definitions to `plugin-dev:skill-reviewer`, which takes the §Report-only variant.

The example was edited in range (Changed files, Constraints, return line). It matches only the "plugin-dev not installed" fallback, and it does not say so.

### m12 — Return-contract drift outside `dispatch-composition.md`

**Axis:** consistency (KD-2).

`dispatch-composition.md` item 5 fixes "the report path on success, or `blocked: <reason>`". Four other surfaces disagree:

- `plugin/agents/corrector.md` §6 Return Result: "Error: [What failed]".
- `plugin/agents/artisan.md` §Output Format: "`error: [brief description]`".
- `plugin/fragments/delegation.md` §Quiet Execution Pattern: "filepath (success) or error message (failure)".
- `plugin/fragments/review-requirement.md` delegation template: "Return filepath or error."

Item 5 says the prompt overrides an agent's own default only for the report path ("whatever default its own definition carries"), not for the return contract.

### m13 — `plugin/fragments/escalation-acceptance.md` §Required and §Verification sequence

**Axis:** consistency (KD-7).

The fragment requires "Git tree clean — no uncommitted changes (`git status --porcelain` returns empty)" and step 3, "If dirty: commit fix, verify clean". Both contradict the KD-7 exemptions. `SKILL.md` §2 itself says "A bare `git status --porcelain` here would refuse states the later gates are documented to tolerate".

With an uncommitted `inbox/*.md` brief, which this tree has now, the criterion can never pass. The §Rollback `git checkout -- .` is tracked in (a) of `.claude/handoff-todo.md`. These two lines are not.

### m14 — `plugin/skills/build/references/tdd-slice.md` §After the slice step 1 (not in the review list)

**Axis:** broken reference. Pre-existing.

"the same step §5 takes at a phase boundary": `SKILL.md` §5 is Finish, and the phase boundary is §4.5 / `phase-boundary.md`.

### m15 — `plugin/agents/tdd-auditor.md` §Inputs (not in the review list)

**Axis:** naming.

"Phase checkpoints: `phase-P-corrector.md`" keeps the term that orch m3 and this job's m8 renamed to "phase boundaries".

### m16 — `plugin/skills/build/SKILL.md` as a whole

**Axis:** constraint precision.

The hub sits at exactly 200 lines, and its §2 and §3 rationale was condensed to hold that. The condensing lost nothing load-bearing: §2's read-back lives in `finishing.md`, and §3 keeps "fail open, invisibly".

The shared convention, however, names a file parked at exactly its cap as having "stopped emitting the signal". The cap already displaced one rule (M1). The next edit has no room.

### m17 — Surfaces outside `plugin/` and the list

**Axes:** accuracy, consistency.

- `docs/references/pipeline-contracts.md` (the D-86 argument) says "`verify-step.sh`, which tolerates nothing but ` M memory`" in the present tense. That is stale against KD-7.
- `plugin/README.md` lists verify-step's call sites as "GREEN, code review and general items". It omits review items, §4.1's corrector, the phase-boundary commit and the review gate.

### m18 — `plugin/bin/triage-feedback.sh` (the code reviewer's file; flagged for cross-check)

**Axis:** consistency (KD-1 refinement).

The script computes `files_changed=$(git diff --name-only "$baseline_commit" | wc -l …)`. This is the one remaining working-tree form on `/build`'s path. It counts uncommitted exempt dirt, and at §2, before the M4 gap is closed, uncommitted reports, into "Files changed".

### m19 — `plugin/skills/build/references/review-dispatch-template.md` §Report-only variant

**Axis:** completeness.

The replacement block defines no failure return: nothing tells the reviewer it may return `blocked: <reason>`. item 5's "Two exceptions" leaves the report-only reviewer with no path for "cannot proceed".

## Unverified

- That the `sandbox-lies` `phantom-untracked` hook annotates `verify-step.sh`'s DIRTY output when that output comes from an unsandboxed call (`dangerouslyDisableSandbox: true`). Every KD-7 re-run rule depends on the annotation reaching the orchestrator. I did not run the hook.
- The M2 consequence of an empty phase base depends on how an orchestrator substitutes a blank `<phase base>`. It was not observed.
- The reachability of a resumed report-only reviewer by `SendMessage` after it returned `END OF REPORT` (finishing.md §1 second pass). This run's `review-skill.md` second pass shows that it worked once.
