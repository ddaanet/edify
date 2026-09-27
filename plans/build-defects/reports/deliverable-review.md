# Deliverable Review: build-defects

**Date:** 2026-09-26
**Methodology:** docs/references/deliverable-review.md

Range `d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`, from
`edify-review-range.sh plans/build-defects/outline.md` (the outline's
Provenance base). `tmp/build-baseline` holds `f44ddbbf`, two commits later; both
intervening commits touch only `plans/` and `inbox/`, so the deliverable set is
the same under either base. Layer 1 ran (two opus agents); findings are
attributed `[code]`, `[prose]` or `[L2]` (this session's cross-cutting read).

## Inventory

| Type | File | +/− |
|------|------|-----|
| Code | `plugin/bin/triage-feedback.sh` | 9/2 |
| Code | `plugin/skills/build/scripts/verify-step.sh` | 25/3 |
| Test | `tests/test_triage_feedback.py` | 124/0 |
| Test | `tests/test_verify_step.py` | 320/0 |
| Agentic prose | `plugin/skills/build/SKILL.md` | 34/22 |
| Agentic prose | `plugin/agents/refactor.md` | 5/2 |
| Agentic prose | `plugin/agents/test-driver.md` | 4/2 |
| Human docs | `plugin/skills/build/references/dispatch-composition.md` | 34/22 |
| Human docs | `plugin/skills/build/references/escalation.md` | 42/13 |
| Human docs | `plugin/skills/build/references/finishing.md` | 38/14 |
| Human docs | `plugin/skills/build/references/phase-boundary.md` | 26/12 |
| Human docs | `plugin/skills/build/references/review-dispatch-template.md` | 32/18 |
| Human docs | `plugin/fragments/review-requirement.md` | 5/2 |
| Human docs | `plugin/fragments/escalation-acceptance.md` | 10/4 |
| Human docs | `plugin/fragments/delegation.md` | 5/3 |
| Configuration | `justfile` (`run-pytest` sentinel hunk) | 1/0 |

In range but not this job's work, and not reviewed: `.bin/claude`, `.gitignore`
and the `justfile` `clean` recipe (commit `18890cfc`, the dist-copy launcher);
`CLAUDE.md` (a wording change in `836ac12d`); the `memory` pointer;
`inbox/brief-runbook-slice-enumerates-predicate-boundaries.md`;
`.claude/handoff-todo.md`.

**Design conformance:** every Scope IN deliverable exists — two scripts, two
new test files, `SKILL.md`, five references, three fragments, two agent
definitions — and every bullet of Items 1.1–2.9 has a deliverable [prose, code].
Both tdd items' slices were checked by mutation: the triage test fails against
the base script; the four Item 1.2 slice-2 tests fail against `31fe4a16`'s
script [code]. 7/7 tests pass. The `run-pytest` sentinel hunk is correct and
sufficient [code]. No stale `TaskOutput`, `checkpoint form`, bare
`git diff --name-only` in prose, or prescribed `git add -A` remains in
`plugin/` [prose, L2].

## Critical Findings

None.

## Major Findings

1. **`plugin/skills/build/SKILL.md` §1 / §2, with `references/escalation.md`
   §Resuming — resume test unreachable from the hub** [prose M1]. Design: KD-6,
   KD-1 (phase 1's base is `tmp/build-baseline`). §2 skips the baseline capture
   "not on a resumed run", but the test for being resumed ("when
   `plans/<job>/reports/` already holds this run's reports") lives only in
   `escalation.md`, which the hub sends a run to only once it already knows it
   is resumed. A fresh-session `/build plans/<job>` that does not say "resume"
   recaptures `tmp/build-baseline`, and every earlier item drops out of the
   review gate, triage and phase 1's base. The placement was chosen to hold the
   200-line cap (`review-skill.md` S3). Related to queued job (b), whose resume
   test keys on the per-job baseline file; the hub-side unreachability is not
   named there.

2. **`references/escalation.md` §Resuming, with `references/phase-boundary.md`
   — a skipped phase boundary breaks KD-1's P>1 base** [prose M2, L2]. Design:
   KD-1 ("That commit always exists, because the phase-boundary commit always
   happens"). Resume step 3 inventories remaining *items*; a run killed after a
   phase's last item but before its `phase-<P>-corrector.md` commit resumes at
   phase P+1 and skips P's boundary review. At P+1's boundary the
   `git log --diff-filter=A` resolution prints nothing, and `phase-boundary.md`
   has no instruction for an empty base. Same cause: a re-run of the same job
   returns a prior run's commit, and a report added more than once returns
   several hashes.

3. **`references/tdd-slice.md` §After the slice — orchestrator commits without
   `git commit -- <paths>`** [prose M3]. Design: KD-7's safety argument ("It then
   commits with `git commit -- <paths>`… so exempt dirt already staged stays
   out"). Step 1's code-review commit says only "Stage those paths by name"; step
   3's `runbook.md` revision commit gives no form. A staged
   `.claude/handoff-task.md` rides those commits. Not named by any outline item,
   but KD-7's exemption is safe only if every commit path uses the form.

4. **`references/finishing.md` §2 and §3 — later steps leave uncommitted
   artifacts** [prose M4]. Design: KD-2 (review dispatches commit nothing, the
   orchestrator commits). §2's triage appends to
   `plans/reports/triage-feedback-log.md`, §3.1's `final-review` corrector and
   §3.2's `tdd-audit` write reports and possibly fixes, and `SKILL.md` §5's
   `review-skip.md` is written — none is committed or verified. The run ends
   dirty; the next entry gate reports DIRTY. This job's own `72f92c3a`
   committed the tdd audit and triage log line by hand.

5. **Conflict between KD-5 and KD-7 — the confirmed cleanup and the rollback
   destroy exempt dirt** [L2; queued job (a)]. `escalation.md` §Post-item
   remediation and `escalation-acceptance.md` §Dirty tree recovery keep
   `git checkout -- . && git clean -fd` as the no-owner fallback; it reverts
   modified `.claude/handoff-*.md` and deletes untracked `inbox/*.md`, the dirt
   KD-7 declares legitimate. `escalation-acceptance.md` §Rollback protocol still
   prescribes an unconfirmed `git checkout -- .`. The delivered text conforms to
   KD-5; the defect is in the design. Queued job (a) replaces the command with
   `verify-step.sh` revert mode.

6. **`tests/test_verify_step.py` — "any porcelain state" untested beyond `MM`
   and `??`** [code F-1]. Design: KD-7 ("The exemptions, in any porcelain
   state"), naming the handoff file's staged state. No test covers `A `,
   `D `/` D` or unmerged states. A mutant restricting the XY columns to
   `[ M?]` passes all six tests. The shipped script handles these states
   correctly (probed: `D  inbox/old.md`, ` D .claude/handoff-task.md` → CLEAN).

7. **`SKILL.md` §4.1 Direct execution — self-review is vacuous after the
   commit** [prose M5; pre-existing]. The item is committed before review, and
   the self-review path is `git diff` (`review-requirement.md` §Self-review
   process says `git diff HEAD`), empty once committed. Same failure KD-1 fixed
   for the phase gate. Pre-existing ordering (base §4.1 also committed first);
   this job rewrote the section. `review-skill.md` noted it without flagging it,
   and no task tracks it.

## Minor Findings

**Changed-files form (KD-1 refinement)**

- `plugin/fragments/review-requirement.md` §Execution Context, Changed files:
  `git diff --name-only <base>` (working-tree form) beside a pointer to `/build`'s
  resolution, while every `/build` surface uses `<base> HEAD` [prose m2, L2].
  `review-fragments.md` kept it for `/review` of uncommitted work; a reader
  under `/build` still gets the wrong form from this line.
- `plugin/bin/triage-feedback.sh` `files_changed`: the one remaining
  working-tree form on `/build`'s path; counts uncommitted exempt dirt (and,
  until Major 4 closes, uncommitted reports) [prose m18, L2].
- `finishing.md` §1 step 1 and `phase-boundary.md` opening: "no commit carries
  those" / "the paths `verify-step.sh` exempts stay out" overstate — `/handoff`
  and memory-pointer commits land exempt paths within a run (this range carries
  `.claude/handoff-todo.md` and `memory`) [prose m1].

**Escalation and dirty-tree prose**

- `escalation.md` §Post-item remediation exit-1 bullet: "at the entry gate as
  after an item" followed by "Any other exit 1 → remediate" lets a reader from
  `SKILL.md` §2 remediate the user's pre-existing dirt instead of STOP
  [prose m5].
- `escalation.md` §Post-item remediation closing paragraph and
  `escalation-acceptance.md` §Dirty tree recovery: no step reaches "no agent
  owns the dirt", and the command's actor is unstated [prose m6, L2].
- `escalation-acceptance.md` §Dirty tree recovery says it defers to
  `escalation.md`, then restates the procedure — a second copy that already
  omits the skip-the-resume cases (no named agent, a review dispatch, no edit
  tools) [L2].
- `escalation-acceptance.md` §Required and §Verification sequence: "`git status
  --porcelain` returns empty" and "If dirty: commit fix" contradict KD-7; with
  an uncommitted `inbox/*.md` the criterion never passes [prose m13].
- `escalation.md` §Escalation "Agent never returns": no branch for the check
  finding the report or commit landed, or for a resume that produces it
  [prose m7].

**Review gate and dispatch contracts**

- `phase-boundary.md` dispatch paragraph: UNFIXABLE skips the §UNFIXABLE
  Detection Protocol that KD-2 and `finishing.md` §1 apply; the phase commit is
  not ordered after the UNFIXABLE resume [prose m3].
- `finishing.md` §1 Structural proof with `review-dispatch-template.md`
  §Report-only variant: the protocol requires a U-REQ/U-ARCH/U-DESIGN code and
  a 3-gate summary the report-only prompt never asks for, so every report-only
  UNFIXABLE fails validation [prose m4].
- `dispatch-composition.md` §Prompt contents item 5: a report-only part ending
  in neither `CONTINUED` nor `END OF REPORT` has no instruction [prose m8].
- `review-dispatch-template.md` §Report-only variant: no `blocked: <reason>`
  return for the reviewer [prose m19].
- `dispatch-composition.md` §Naming: `review-<group>` slug undetermined against
  `finishing.md` §1's groups; this run produced `review-code`, `review-skill`,
  `review-agents`, `review-fragments` [prose m9, L2; queued job (c)].
- `dispatch-composition.md` §Naming: `final-review` described as "a
  single-phase run's closing corrector", against `finishing.md` §3.1's triggers
  [prose m10; pre-existing].
- `review-dispatch-template.md` §Example: a skill-definition group dispatched
  with the fix-capable §Template, though routing sends skill definitions to the
  report-only reviewer; edited in range [prose m11].
- Return-contract drift from item 5's "report path or `blocked: <reason>`":
  `corrector.md` §6, `artisan.md` §Output Format, `delegation.md` §Quiet
  Execution Pattern, `review-requirement.md` delegation template [prose m12, L2].

**Stale text outside the listed files**

- `tdd-slice.md` §After the slice: "the same step §5 takes at a phase boundary"
  — §5 is Finish [prose m14; pre-existing].
- `tdd-auditor.md` §Inputs: "Phase checkpoints" keeps the term orch m3 renamed
  [prose m15].
- `docs/references/pipeline-contracts.md` (D-86 argument): "`verify-step.sh`,
  which tolerates nothing but ` M memory`", present tense, stale against KD-7;
  `plugin/README.md` lists verify-step's call sites as "GREEN, code review and
  general items" only [prose m17].

**Hub size**

- `SKILL.md` at exactly its 200-line cap: the condensing lost nothing
  load-bearing, but the cap already displaced the resume test (Major 1) and
  the next edit has no room [prose m16].

**`verify-step.sh` and tests**

- `exempt` pattern: any path named `memory` is exempt in any state, gitlink or
  not (probe: untracked regular file `memory` → CLEAN) [code F-2].
- `exempt` pattern: a rename between two exempt paths
  (`R  inbox/old.md -> inbox/new.md`) is DIRTY; fails closed, but KD-7 does not
  record the carve-out [code F-3].
- `tests/test_verify_step.py`: single-level `[^/]+` not pinned — a `.+` mutant
  passes all tests [code F-4].
- Both test modules copy `os.environ` without clearing `GIT_DIR`,
  `GIT_INDEX_FILE`, `GIT_WORK_TREE`; no current trigger, pattern inherited from
  `tests/review_range_helpers.py` [code F-5].
- `triage-feedback.sh`: the `\s` → `[[:space:]]` change is unspecified excess
  (a code-review fix in `7cc0e5c2`), portable, BSD behaviour unverified
  [code F-6].

## Gap Analysis

| Design requirement | Status |
|---|---|
| KD-1 phase base resolved from predecessor's report | Covered; resume edge Major 2; form drift Minor (changed-files) |
| KD-1 explicit Changed-files list, full §Execution Context halt | Covered |
| KD-1 `verify-step.sh` exit 0 before triage | Covered |
| KD-2 one rule for report path and return | Covered in `dispatch-composition.md`; drift elsewhere Minor |
| KD-2 UNFIXABLE validated, report-only second pass | Covered at review gate; phase boundary Minor |
| KD-3 `reports_count` exclusions, WARNING handling | Covered |
| KD-4 no `TaskOutput`/`TaskStop`, never-returns procedure | Covered |
| KD-5 remediation governs dirty tree, cleanup confirmed | Covered; design conflict with KD-7 Major 5 |
| KD-6 `<job>` from the invocation | Covered; resume detection Major 1 |
| KD-7 exemptions, `--untracked-files=all`, mask re-run | Covered; test gap Major 6; commit-form gap Major 3 |
| Item 1.1 slice 1 | Covered |
| Item 1.2 slices 1–2 | Covered |
| Items 2.1–2.9 | Covered |

## Summary

Critical 0 · Major 7 · Minor 25.

Of the Majors, 5 is queued as job (a) and 1 is partly covered by job (b); 7 is
pre-existing in a section this job rewrote. Majors 2, 3, 4, 6 and 7 are not
tracked anywhere.

## Sub-reports

- `plans/build-defects/reports/deliverable-review-code-tests.md`
- `plans/build-defects/reports/deliverable-review-prose.md`
