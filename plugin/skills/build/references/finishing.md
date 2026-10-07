# Finishing the Work

Reached after the last item, in the session that completes it. Three steps in
order: review gate, triage feedback, completion. `/build` §5 owns the one branch
before this file — whether review is dispatched or skipped. A skipped review
still runs §1's report commit, which carries its `review-skip.md`, then §2 and
§3 here.

## 1. Review gate

**Landed check first.** A finished job re-invoked, or a run resumed after a kill
inside this file, reaches it again, and a stage that has landed is not re-run.
The gate has landed when a commit after the run's last item-report commit
touches a review-gate report:

```bash
git log -1 --no-show-signature --format=%H -- ':(glob)plans/<job>/reports/item-*'
git log -1 --no-show-signature --format=%H <L>..HEAD -- ':(glob)plans/<job>/reports/review-*.md'
```

`<L>` is the first command's hash, written into the second as the hash itself;
§3 reuses it. The second printing a hash — `review-skip.md` counts — means the
gate landed: go to §2. Empty → run the gate below. As for a phase boundary
(D-89), the key is the report path, never a commit subject. An empty `<L>` is
the fault step 1's `NO-BASE:` names, and either command failing leaves no
answer: STOP on both.

Read `../../fragments/review-requirement.md` and route changed files to the
appropriate reviewer by its routing table.

1. List changed files:

   ```bash
   plugin/skills/build/scripts/changed-files.sh <job>
   ```

   Exit 0 prints `BASE: <sha>`, the run's base, then one path per line: the
   committed diff from that base to `HEAD`, minus the paths `verify-step.sh`
   exempts and the pipeline's record: the job's own `plans/<job>/` and the
   triage log, `plans/reports/triage-feedback-log.md`. The `HEAD` form keeps
   uncommitted dirt out; a `/handoff` or memory-pointer commit can still land
   exempt paths during the run, and the script drops those by name. Exit 1
   (`NO-BASE:`, no committed item report) or exit 2 (`ERROR:`) → STOP; never
   substitute an empty base or a working-tree diff. `NO-BASE:` here is a fault,
   not an empty run: every run commits an item report, work with no `Item N.M`
   included, as Item 1.1 (`/build` §1, D-88). Exit 0 with no path after `BASE:`
   → there is nothing to review: take `/build` §5's `review-skip.md` branch,
   stating that the list came back empty, and go straight to the report commit
   below, which carries it.
2. Group by the four fixed rows of `references/dispatch-composition.md` §Naming
   and resumption — `review-code`, `review-skill`, `review-agent`,
   `review-design` — classing each file kind by the rule stated there, never
   into a new group. The row's slug is the group's dispatch name.
3. Look up the reviewer per group from the routing table
4. Read `references/review-dispatch-template.md` and dispatch each group to its
   reviewer, structuring the prompt by it

**Two dispatch patterns:**

- **Fix-capable reviewers** (`edify:corrector`, which takes every row but the
  skill row, and that row too without `plugin-dev`): delegate, read the report,
  grep UNFIXABLE. The agent applies its fixes and writes its own report.
- **Report-only reviewers** (`plugin-dev:skill-reviewer`): delegate, collect the
  findings it returns in parts as `dispatch-composition.md` §Prompt contents
  item 5 says, then write the report and apply the fixes in this session. That
  reviewer holds **Read, Grep and Glob only** — no Write, no Edit, no Bash, no
  Skill — so it can neither fix nor file. Use the template's §Report-only
  variant.

Scope per dispatch is that artifact group's share of step 1's list,
implementation only; the template's §Field Rules set every other field.

Planning artifacts do not route through this gate. They route by artifact, as
`docs/references/pipeline-contracts.md` D-26 records, each under its name from
`references/dispatch-composition.md` §Naming and resumption, `<source job>`
being the `plans/` directory the artifact sits in:

- `design.md` → `edify:design-corrector`, as `review-plan-<source job>-design`;
- `outline.md` → `edify:outline-corrector`, as
  `review-plan-<source job>-outline`;
- `runbook.md` → `edify:runbook-corrector`, as
  `review-plan-<source job>-runbook`.

The prompt assigns the report path from that name, as `dispatch-composition.md`
§Prompt contents item 5 does for every dispatch. `runbook-corrector` rejects
anything that is not `runbook.md`.

**Report-only second pass:** where this session applied a report-only reviewer's
fixes, resume that reviewer (`review-<group>`) once by `SendMessage`, naming the
fixes applied, over the same files: the gate's edits get an independent review,
and this session's would otherwise have none. Append its findings to the group's
report under a second-pass heading and apply them. There is no further pass; the
second pass's fixes go unreviewed by design.

**Structural proof (D+B anchor):** once review completes, Read each report path
this gate actually dispatched. The Read proves the report exists; without it, §2
cannot proceed. UNFIXABLE in any report → validate it by
`../../fragments/review-requirement.md` §UNFIXABLE Detection Protocol, then STOP
on each that holds and surface it to the user with the path. Where the protocol
resumes the corrector for reclassification, resume the group's own reviewer,
`review-<group>`, by `SendMessage`: for a report-only group that is the reviewer
that raised the finding, whose reply comes back in parts as on the first pass,
and this session rewrites the report from it. Do not proceed to §2 until every
issue is resolved or accepted.

A reviewer commits nothing, so make the report commit yourself: every group's
report, with the fixes applied where there are any, by the reviewer or by this
session — or, where review was skipped, `plans/<job>/reports/review-skip.md`.
Stage those paths by name and commit with `git commit -- <paths>`, subject
`<type>: <job> Review gate`. Then:

```bash
plugin/skills/build/scripts/verify-step.sh
```

Exit 0 (`CLEAN:` and the checks that passed) → §2. Anything else → Read
`references/escalation.md` §Post-item remediation and follow it; §2 waits for
exit 0.

## 2. Triage feedback

```bash
plugin/bin/triage-feedback.sh <job>
```

It takes no base: it runs `changed-files.sh <job>` itself and measures that
list, the set §1 reviewed (D-90). The script prepends `plans/` itself — pass the
bare job name, not the plan path. A non-zero exit writes no log row and gives no
verdict — 1 is a usage error; 2 is `ERROR:`, after a `NO-BASE:` or `ERROR:` from
`changed-files.sh` or on a failure of its own: STOP and report its output.

On exit 0, read the script output. On a divergence message → surface it inline.
On `WARNING: No corrector report` → surface it inline and investigate before §3:
§1 should have left a review report, or `/build` §5 a `review-skip.md`, and the
warning means neither exists — run §1, or write `/build` §5's `review-skip.md`
and commit it as §1's report commit does, then rerun §2. On
`unrecognised classification: <label>` → surface it inline:
`classification.md`'s label is none of `Simple`, `Moderate`, `Complex` or
`Defect`, so no row was logged. On match, or no-classification with neither line
→ proceed silently.

## 3. Completion

1. **Final review:** dispatch one `edify:corrector` over the whole diff,
   dispatch name `final-review` — **only where §1 did not already cover it**. §1
   normally reviews the run's entire diff, and a second corrector over the same
   changes is waste; the cases that still need this are a run whose review was
   skipped over a non-empty list, and one whose routing left a group of changed
   files unreviewed. An empty list has nothing to review here either. Not where
   it has landed: skip it when
   `git log -1 --no-show-signature --format=%H <L>..HEAD -- plans/<job>/reports/final-review.md`
   prints a hash, `<L>` being §1's. Its report gets §1's structural proof before
   the closing commit: Read `plans/<job>/reports/final-review.md`, and on
   UNFIXABLE validate each by `../../fragments/review-requirement.md` §UNFIXABLE
   Detection Protocol, resuming `final-review` by `SendMessage` where the
   protocol resumes the corrector, and STOP on each that holds, surfacing it to
   the user with the path.
2. **TDD audit:** if any tdd item ran, dispatch `edify:tdd-auditor`, dispatch
   name `tdd-audit` — skipped, as step 1 is, where the same query over
   `plans/<job>/reports/tdd-audit.md` prints a hash. Its inputs are the RED,
   GREEN and review reports of every slice, and the hosting file, which the
   prompt names: the file the tdd items came from (`/build` §1). git serves to
   resolve a report to its adding commit, to diff that commit, and to read the
   hosting file's list-revision commits. Where a report is missing, resume the
   agent named for that dispatch and get it
   (`references/dispatch-composition.md` §Naming and resumption).
3. **Closing commit:** one commit carrying what §2 and §3 left — the triage log
   line in `plans/reports/triage-feedback-log.md` where `triage-feedback.sh`
   wrote one, `final-review`'s report and its fixes, and
   `plans/<job>/reports/tdd-audit.md`, each where this pass changed it. Stage
   those paths by name and commit with `git commit -- <paths>`, subject
   `<type>: <job> Finish`; where none changed there is nothing to commit. Then
   run `plugin/skills/build/scripts/verify-step.sh`: exit 0 → the run summary;
   anything else → Read `references/escalation.md` §Post-item remediation and
   follow it, and the run summary waits for exit 0.
4. **Run summary:** close with the run summary in context — per item its
   dispatches (`item-N-M`, `item-N-M-s<k>-red`, …), each report path, each
   remediation RCA, the list revisions, and the follow-up
   `/deliverable-review plans/<job>` (opus, fresh session). Name the follow-up
   and stop there: `/build` never writes `.claude/handoff-task.md` itself.
