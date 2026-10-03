# Item 2.4 — `plugin/skills/build/references/finishing.md`

Requirements: Major 4, (c), m1, m4.

## Changes per bullet

- **§1 step 1 (KD-6, m1).** `git diff --name-only "$(cat tmp/build-baseline)"
  HEAD` became a `plugin/skills/build/scripts/changed-files.sh <job>` block. Its
  output: `BASE:`, then the committed diff to `HEAD` minus the exempt paths and
  `plans/<job>/`. "No commit carries those" is corrected: the `HEAD` form keeps
  uncommitted dirt out, but a `/handoff` or memory-pointer commit can land
  exempt paths during the run, and the script drops them. Exit 1 (`NO-BASE:`)
  or exit 2 (`ERROR:`) → STOP; never an empty base or a working-tree diff.
- **§1 step 2 (KD-5, (c)).** "Group by artifact type (code/tests/plans, …)"
  became a grouping by the four fixed rows — `review-code`, `review-skill`,
  `review-agent`, `review-design` — with the slug as the group's dispatch name
  and no new groups. The class rule itself is not restated here. KD-5 says "The
  rule is stated once, in `dispatch-composition.md` §Naming and resumption, and
  `finishing.md` §1 step 2 groups by it", so step 2 points there. "plans" left
  the code row: the script drops `plans/<job>/`, and planning artifacts route by
  artifact (D-26).
- **§1 report commit (KD-4, KD-8).** "Commit each group's report yourself"
  became one report commit. It carries every group's report and fixes, or
  `plans/<job>/reports/review-skip.md` where review was skipped, by
  `git commit -- <paths>`, subject `<type>: <job> Review gate`. The opening
  paragraph now says a skipped review still runs §1's report commit before §2
  and §3, so the skip path reaches that commit and the `verify-step.sh` run
  after it. This matches `SKILL.md` §5 ("`references/finishing.md` §1's report
  commit carries it"). §2's WARNING branch also has a late-written
  `review-skip.md` committed "as §1's report commit does", so it does not end
  the run dirty.
- **Structural proof (m4).** After the protocol pointer: where the protocol
  resumes "the corrector" for reclassification, resume the group's own
  reviewer, `review-<group>`, by `SendMessage`. For a report-only group that is
  the reviewer that raised the finding. Its reply comes back in parts, and this
  session rewrites the report from it.
- **§2 (KD-6, Item 1.3).** `"$(cat tmp/build-baseline)"` became `<base>`:
  `changed-files.sh <job>`'s `BASE:`, from §1 step 1, or from a fresh call where
  review was skipped (step 1 does not run then). It is written into the command
  as the hash, since no shell variable survives between calls and the script
  rejects an empty baseline. The "read the commit back from the `/build` §2
  file" sentence is gone with the file.
- **§3 (KD-4, Major 4).** New step 3, **Closing commit**. One commit carries
  whichever exist of: the triage log line in
  `plans/reports/triage-feedback-log.md`, `final-review`'s report and fixes, and
  `plans/<job>/reports/tdd-audit.md`. It uses `git commit -- <paths>`, subject
  `<type>: <job> Finish`. Then `verify-step.sh`: exit 0 → the run summary;
  anything else → `escalation.md` §Post-item remediation, and the summary waits
  for exit 0. The run summary is now step 4. §3.1's "entire baseline diff" is
  now "the run's entire diff".

## Judgement calls for review

- **One report commit, not one per group.** KD-4 says "the report commit of
  §1" and KD-8 gives the gate one subject, so the per-group wording became a
  single commit.
- **Nothing to commit at §3.** The triage script skips its log line on
  `no-classification`, `final-review` runs only on two conditions, and
  `tdd-audit` only after a tdd item. All three can be absent, so the step says
  that then there is nothing to commit, and `verify-step.sh` still runs.
- **`NO-BASE:` at §1 → STOP.** The case: work taken from the invocation
  (`SKILL.md` §1 option 3) whose execution left no `item-*` report. Then
  `changed-files.sh` exits 1 at finishing. KD-1 says every item leaves a
  report, so I treated `NO-BASE:` as a STOP, not a reason to skip review.
  Whether option-3 work always produces an `item-*` report is not settled by
  the outline. Flagged for the deliverable review.
- **Command path form.** New commands use the repo-root
  `plugin/skills/build/scripts/…` form this file already uses for
  `verify-step.sh`.
- "the user" is kept: it is this file's voice.

## Cross-references left for later items

- `references/dispatch-composition.md` §Naming and resumption does not yet
  carry KD-5's four slugs and the class rule that step 2 now points at: Item
  2.6. Its "`final-review` for a single-phase run's closing corrector" is also
  still out of step with §3.1's two triggers (m10): Item 2.6.
- `references/review-dispatch-template.md`:
  - §Field Rules, Baseline still reads `tmp/build-baseline`: Item 2.5.
  - §Report-only variant does not ask for the U-REQ/U-ARCH/U-DESIGN code or
    the three-gate summary that the validation this section now relies on
    checks (m4): Item 2.5.
- `../../fragments/review-requirement.md` routing table rows (skill row
  covering `references/` nodes, `review-design` row → `edify:corrector` with
  `craft:design-doc-writing`): Item 2.9.
  - Same file, §UNFIXABLE Detection Protocol step 4 still says reclassification
    is a fresh delegation with "no continuation mechanism available", against
    the resume by name here. No item names it; flagged as in `item-2-3.md`.
- `plugin/README.md` §Scripts: the review gate and §3's closing commit are
  `verify-step.sh` call sites, and `changed-files.sh` is new: Item 2.11.
- `plugin/agents/tdd-auditor.md` points at this file's §3, whose step
  numbering changed (run summary now step 4). Its pointer is to §3 as a whole,
  so it stays valid. Item 2.10 owns that file if anything else needs changing.

## Verification

- `just format`, then `just precommit` green (version consistency, cached
  tests, line limits — only the three allowlisted correctors reported — and
  design links).
- Self-review of the uncommitted diff against Item 2.4's six bullets, KD-4,
  KD-5, KD-6 and KD-8, and against `SKILL.md` §2 and §5, `escalation.md`
  §Post-item remediation and §Resuming, and `phase-boundary.md` as Item 2.3
  left it.
- 102 lines before, 134 after (`wc -l`, after `rumdl fmt`).
