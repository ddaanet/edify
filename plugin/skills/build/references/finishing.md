# Finishing the Work

Reached once per job, in the session that completes the last item. Three steps
in order: review gate, triage feedback, completion. `/build` §5 owns the one
branch before this file — whether review is dispatched or skipped — and a
skipped review still runs §2 and §3 here.

## 1. Review gate

Read `../../fragments/review-requirement.md` and route changed files to the
appropriate reviewer by its routing table.

1. List changed files: `git diff --name-only "$(cat tmp/build-baseline)"`
2. Group by artifact type (code/tests/plans, skill definitions, agent
   definitions, design documents)
3. Look up the reviewer per group from the routing table
4. Read `references/review-dispatch-template.md` and dispatch each group to its
   reviewer, structuring the prompt by it

**Two dispatch patterns:**

- **Fix-capable reviewers** (`edify:corrector`, `edify:design-corrector`,
  `edify:outline-corrector`, `edify:runbook-corrector`): delegate, read the
  report, grep UNFIXABLE. The agent applies its fixes and writes its own report.
- **Report-only reviewers** (`plugin-dev:skill-reviewer`): delegate, read the
  findings it returns, then write the report and apply the fixes in this
  session. That reviewer holds **Read, Grep and Glob only** — no Write, no Edit,
  no Bash, no Skill — so it can neither fix nor file. Use the template's
  §Report-only variant.

Scope per dispatch is that artifact group's share of step 1's list,
implementation only; the template's §Field Rules set every other field.

Planning artifacts do not route through this gate. They route by artifact, as
`docs/references/pipeline-contracts.md` D-26 records: `design.md` →
`edify:design-corrector`, `outline.md` → `edify:outline-corrector`, `runbook.md`
→ `edify:runbook-corrector`. `runbook-corrector` rejects anything that is not
`runbook.md`.

**Report-only re-dispatch:** where this session applied a report-only reviewer's
fixes, re-dispatch that group to its reviewer once, over the same files — this
session does not review its own edits (`/build` §4.1). Add what it returns to
the group's report and apply it; there is no further pass.

**Structural proof (D+B anchor):** once review completes, Read each report path
this gate actually dispatched. The Read proves the report exists; without it, §2
cannot proceed. UNFIXABLE in any report → validate it by
`../../fragments/review-requirement.md` §UNFIXABLE Detection Protocol, then STOP
on each that holds and surface it to the user with the path. Do not proceed to
§2 until every issue is resolved or accepted.

A reviewer commits nothing, so commit each group's report yourself — with the
fixes applied where there are any, by the reviewer or by this session — staging
those paths by name and committing with `git commit -- <paths>`. Then:

```bash
plugin/skills/build/scripts/verify-step.sh
```

Exit 0 (`CLEAN:` and the checks that passed) → §2. Anything else → Read
`references/escalation.md` §Post-item remediation and follow it; §2 waits for
exit 0.

## 2. Triage feedback

```bash
plugin/bin/triage-feedback.sh <job> "$(cat tmp/build-baseline)"
```

The script prepends `plans/` itself — pass the bare job name, not the plan path.
It rejects an empty baseline with its usage line, so read the commit back from
the `/build` §2 file rather than from a variable.

Read the script output. On a divergence message → surface it inline. On
`WARNING: No corrector report` → surface it inline and investigate before §3: §1
should have left a review report, or `/build` §5 a `review-skip.md`, and the
warning means neither exists. On match or no-classification with no warning →
proceed silently.

## 3. Completion

1. **Final review:** dispatch one `edify:corrector` over the whole diff,
   dispatch name `final-review` — **only where §1 did not already cover it**. §1
   normally reviews the entire baseline diff, and a second corrector over the
   same changes is waste; the cases that still need this are a run whose review
   was skipped, and one whose routing left a group of changed files unreviewed.
2. **TDD audit:** if any tdd item ran, dispatch `edify:tdd-auditor`, dispatch
   name `tdd-audit`. Its inputs are the RED, GREEN and review reports of every
   slice; git serves only to resolve a report to its adding commit and to diff
   that commit. Where a report is missing, resume the agent named for that
   dispatch and get it (`references/dispatch-composition.md` §Naming and
   resumption).
3. **Run summary:** close with the run summary in context — per item its
   dispatches (`item-N-M`, `item-N-M-s<k>-red`, …), each report path, each
   remediation RCA, the list revisions, and the follow-up
   `/deliverable-review plans/<job>` (opus, fresh session). Name the follow-up
   and stop there: `/build` never writes `.claude/handoff-task.md` itself.
