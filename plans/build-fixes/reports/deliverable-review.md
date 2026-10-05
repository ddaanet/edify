# Deliverable Review: build-fixes

**Date:** 2026-10-04
**Methodology:** docs/references/deliverable-review.md

## Inventory

**Baseline.** The design baseline is `plans/build-fixes/outline.md`; the job has
no `design.md`. `edify-review-range.sh` returned
`RANGE: d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`. The outline supersedes
`plans/build-defects/outline.md` and shares its base, so the range covers both
jobs, 87 commits. The review judges the final state at HEAD. The superseded
outline is the baseline only for `plugin/fragments/delegation.md`
(build-defects Item 2.9).

**Total.** 2,925 changed lines outside `plans/`, `tmp/` and the handoff
files. That is above 2,000, so Layer 1 ran three opus reviewers: code, tests,
and prose+config.

| Type | File | +/− |
|---|---|---|
| Code | `plugin/skills/build/scripts/changed-files.sh` (new) | +128 |
| Code | `plugin/skills/build/scripts/exempt-paths.sh` (new) | +15 |
| Code | `plugin/skills/build/scripts/verify-step.sh` | +48/−6 |
| Code | `plugin/bin/triage-feedback.sh` | +24/−12 |
| Test | `tests/test_changed_files.py` (new) | +236 |
| Test | `tests/test_changed_files_phase.py` (new) | +204 |
| Test | `tests/changed_files_helpers.py` (new) | +82 |
| Test | `tests/test_verify_step.py` | +94 |
| Test | `tests/test_verify_step_exemption.py` (new) | +240 |
| Test | `tests/verify_step_helpers.py` (new) | +109 |
| Test | `tests/test_triage_feedback.py` | +256 |
| Agentic prose | `plugin/skills/build/SKILL.md` (196 lines) | +46/−38 |
| Agentic prose | `plugin/skills/build/references/escalation.md` | +101/−14 |
| Agentic prose | `plugin/skills/build/references/finishing.md` | +85/−29 |
| Agentic prose | `plugin/skills/build/references/phase-boundary.md` | +70/−20 |
| Agentic prose | `plugin/skills/build/references/dispatch-composition.md` | +65/−30 |
| Agentic prose | `plugin/skills/build/references/review-dispatch-template.md` | +60/−25 |
| Agentic prose | `plugin/skills/build/references/tdd-slice.md` | +12/−9 |
| Agentic prose | `plugin/agents/{tdd-auditor,test-driver,refactor}.md` | +30/−22 |
| Agentic prose | `plugin/fragments/{review-requirement,escalation-acceptance,delegation}.md` | +56/−32 |
| Human docs | `docs/references/build-run-state.md` (new) | +188 |
| Human docs | `docs/decisions.md`, `docs/design.md`, `docs/references/pipeline-contracts.md` | +50/−22 |
| Human docs | `docs/changelog.md` and the 2026-10-03 entry | +32 |
| Human docs | `plugin/README.md` | +16/−4 |
| Configuration | `justfile`, `plugin/portable.just` | +7/−4 |
| Configuration | `CLAUDE.md` (the `build-run-state.md` routing bullet) | +4/−1 |

**Commits in the range that are not job deliverables.** None is counted as
excess:

- `18890cfc`: `.bin/claude`, `.gitignore`, the `memory` pointer and the
  `justfile` `clean` recipe;
- `f44ddbbf`: an inbox brief;
- `836ac12d`: the `CLAUDE.md` scraper line.

**Conformance summary.** Every item, 1.1–1.4 and 2.1–2.15, has a matching
deliverable. Item 2.14 went to a new node, `build-run-state.md`, by my human
partner's ruling.

Two commits landed after the run's §3 Finish commit and outside its review
gate:

- `35992c24`, the `CLAUDE.md` routing bullet, which closes leg 4's open item 1;
- `c458a726`, a `review-requirement.md` change (see m10).

## Critical Findings

**C1. `plugin/bin/triage-feedback.sh`, `reports_count` and the verdict block:
every Simple `/build` run is logged `underclassified`, and the Complex →
`overclassified` branch can no longer be reached.**

- Requirement: KD-1 and Item 2.1 (every item leaves an `item-*` report),
  interacting with the Item 1.3 script.
- Cause: `reports_count` counts `item-*.md`. KD-1 made an item report universal,
  including §4.1's in-session self-review, which wrote no report at the base.
  As a result:
  - Simple with `reports_count > 0` always reads `underclassified`;
  - Complex `overclassified` needs `reports_count -eq 0`, which can no longer
    happen.
- Pinned by the suite: `tests/test_triage_feedback.py::test_simple_with_review_reports_matches`
  builds a "reviewed Simple run" that has no item report, a state KD-1 rules
  out.
- Probe (both Layer 2 and the code reviewer ran it): one Simple item, its
  `item-1-1.md` and a `review-code.md` gave `Reports: 1`,
  `Behavioral code: no`, verdict `underclassified`.
- Impact: every Simple job routed to `/build` (by `/design` §Routing) appends
  a wrong row to `plans/reports/triage-feedback-log.md`. That log is the data
  `execution-routing.md` says the classification thresholds wait on.
- Source: Layer 2, and code C1.

## Major Findings

**M1. `plugin/bin/triage-feedback.sh`, `files_changed` and `committed_diff`:
the evidence counts the job's own record and the exempt paths.**

- Requirement: KD-6 / D-90 define the run's changes as `<base> HEAD` minus
  `plans/<job>/` and the exempt paths. Triage takes only `BASE:` and runs a raw
  `git diff`.
- Measured on this run's own base, `d415f22d`: 103 files in the raw diff, 69
  of them under `plans/build-fixes/`, against 34 from `changed-files.sh`.
- `Behavioral code` also greps report prose. The code reviewer found 4 prose
  `+` lines under `plans/` that match the definition regex.
- This conforms to D-90's letter ("two diffs take the same `<base> HEAD`
  form"), so the fix runs through the design. Fixing C1 does not fix this.
- Source: code M1, and Layer 2.

**M2. `plugin/fragments/escalation-acceptance.md` §Rollback protocol: a
committed failed fix is reverted by default.**

- Requirement: KD-3 / D-92 ("nothing reverts by default"; the rejected
  alternative "discards work the run already paid for") and Item 2.8.
- "Fix committed: revert every commit since the last clean commit before the
  failed item" runs without any decision, and its scope reaches back to the
  item's own commits.
- The 2026-10-03 changelog entry states the opposite policy as fact: "A revert
  happens only by my human partner's decision, path by path."
- This is open policy: leg 4 open item 3 and `review-skill.md` m6.
- Source: prose M1, and Layer 2.

**M3. `plugin/fragments/review-requirement.md` routing table design row, with
`dispatch-composition.md` §Naming and resumption and D-93: the `review-design`
row routes to an agent that refuses it.**

- Requirement: KD-5.
- `plugin/agents/corrector.md` §0 "Validate Task Scope" rejects a single-file
  scope that is `design.md` or sits in a `design` path, and redirects to
  `design-corrector`, which KD-5 explicitly rejects for this row.
- Affected: a `review-design` group holding only `docs/design.md`, and a §4.1
  `item-N-M` corrector over an item that edits only that file.
- `corrector.md` is owned by defect 21. Leg 4 open item 2 records the
  conflict. No text `/build` ships warns the orchestrator.
- Source: prose M2, and Layer 2.

**M4. `plugin/skills/build/SKILL.md` §1 option 3 and §4.1, with
`finishing.md` §1 step 1: work without `Item N.M` ids has no report name.**

- Requirement: KD-1. The `item-*` report is the only resume key and the only
  source of the run base.
- "Neither — take the task from the invocation" and a design with no item
  structure give no `N.M` for `item-N-M.md`. As a result:
  - an improvised name reads as a fresh run after a kill;
  - a run with no committed `item-*` report hits `NO-BASE:` → STOP at the
    review gate.
- This is open: leg 4 open item 4.
- Source: prose M3, and Layer 2.

**M5. `plugin/skills/build/references/tdd-slice.md` §After the slice step 3,
and `plugin/agents/tdd-auditor.md`: list revisions for tdd items hosted in an
outline or design are undefined.**

- `tdd-slice.md` accepts slices from an outline or design, but the
  list-revision step names only `runbook.md`.
- The auditor accounts only for "a `runbook.md`-only list revision".
- This job's own run shows the gap: `tdd-audit.md` Violations 3–4 record list
  changes riding a code-review commit or never reaching the outline.
- Source: prose M4.

**M6. `tests/test_changed_files.py` and `tests/test_changed_files_phase.py`:
no test pins Item 1.2's NUL-delimited read.**

- Requirement: Item 1.2 Interfaces, "never split on whitespace".
- No fixture path holds a space or a non-ASCII byte. Two mutants stayed
  green across all 18 changed-files and verify-step tests:
  - `for path in $(git diff --name-only …)`, which splits `my file.txt`;
  - a newline `read` without `-z`, which C-quotes `café.txt` and fails to drop
    an exempt `inbox/é.md`.
- The property was only ever checked by a hand-run probe
  (`item-1-2-s1-code-review.md`).
- Source: tests M-1.

## Minor Findings

**Code robustness and error signaling** (source: code review)

- m1. `changed-files.sh`, top-level `exec 2>&1`: git warnings print among the
  paths on exit 0. On exit 2, git's `fatal:` precedes `ERROR:`. Exit codes stay
  correct.
- m2. `changed-files.sh`, base and diff: with merge-shaped history, a merge of
  `main` into the job branch lists unrelated files as the run's work. An item
  report added only in a merge commit is invisible, giving `NO-BASE:`. This
  follows from KD-1 and KD-6. How often it happens is unmeasured.
- m3. `changed-files.sh`, unborn HEAD: it exits 2, while the Item 1.2
  interface's exit-1 wording literally applies. The test pins exit 2, and
  `/build` cannot reach this state.
- m4. `triage-feedback.sh`, both `git diff "$baseline_commit" HEAD` calls have
  no `--`, so a file named `HEAD` gives `fatal: ambiguous argument`.
  `changed-files.sh` guards the same form.
- m5. `triage-feedback.sh`, behavioural-code test: `grep … <<<` sits inside
  `if`, so a here-string or grep failure reads as "no". `verify-step.sh`'s own
  comment rejects this form. Reasoned, not probed.
- m6. `triage-feedback.sh`, `classification=$(… | xargs || true)`: an
  apostrophe makes `xargs` fail, and the error is masked. Pre-existing, on a
  line edited in the range.
- m7. Idempotency of §5. `triage-feedback.sh` appends a row on every run. KD-1
  sends a finished job that is re-invoked back through §5, and
  `escalation.md` §Resuming takes inventory of items and boundaries only. A
  re-invocation, or a resume after a kill mid-§5, therefore re-runs the whole
  review gate and logs a duplicate row (probed: two identical rows), although
  the `review-*.md` and `tdd-audit.md` report history would show that §5 had
  landed. Source: code m7, and Layer 2.
- m8. The script comments in `triage-feedback.sh` and `verify-step.sh` cite
  `KD-N` from two different outlines. The plugin ships to repos where neither
  outline exists; the durable IDs are D-88 to D-94.

**Agentic prose determinism and completeness** (source: prose review, except
where noted)

- m9. `SKILL.md` §2, `escalation.md` §Post-item remediation and D-91 rely on
  the `sandbox-lies` hook. That hook ships in a separate plugin, which is
  neither named as a dependency nor installed in this repo's `plugin/hooks/`.
  With the hook absent, the mask branch never fires. Source: Layer 2.
- m10. `dispatch-composition.md` §Naming and resumption ("an unnamed agent
  cannot be resumed") and `delegation.md` §Delegate Resume contradict
  `review-requirement.md` §UNFIXABLE Detection Protocol step 4, which resumes
  by agent id. This run resumed by agent id throughout. The step-4 change is
  `c458a726`, committed after Finish and unreviewed. Source: prose m1, and
  Layer 2.
- m11. The KD-5 skill row is worded two ways. `review-requirement.md` covers
  "shared instruction files kept outside a skill"; `dispatch-composition.md`
  and D-93 cover only the prose skills load. A `.claude/rules/*.md` file
  therefore routes differently depending on which text the reader follows.
- m12. `escalation.md` §Resuming step 2: "every other verdict is taken as §2
  takes it" collides with §2's DIRTY STOP. A dirty resume also never reaches
  `just precommit`.
- m13. `SKILL.md` §4.4 has no post-step verification for the refactor commit
  or the list-revision commit. `README.md` and `design.md` §5.3 ("after every
  step whose work is committed") overclaim. A refactor returning `error` after
  leaving dirt flows into the next RED.
- m14. `escalation-acceptance.md` §Verification sequence step 3: its commit
  takes no KD-8 subject, and "re-run until it exits 0" has no bound and no
  `PRECOMMIT:` branch.
- m15. `finishing.md` §3: `final-review`'s report is committed with no
  UNFIXABLE check, which §1 does run.
- m16. `finishing.md` §1 step 1: an exit 0 with an empty list is not routed.
  It leads to §2's `No corrector report` warning, not to the `review-skip.md`
  branch.
- m17. `escalation.md` §Post-item remediation step 2 does not name the agent
  type for a fresh dispatch after a slice step.
- m18. `review-dispatch-template.md` §Example: its return line asks for a bare
  `UNFIXABLE: [description]`, without the subcategory code and three-gate
  summary the protocol validates.
- m19. `build-run-state.md` D-92: the revert recipe's operand is `<paths>`,
  where `escalation.md` writes `<tracked or indexed paths>`.

**Tests** (source: tests review)

- m20. Placement. Item 1.1's tests live in `test_verify_step_exemption.py` and
  Item 1.4 slices 1–3 in `test_changed_files_phase.py`, both line-cap splits.
  The phase module's docstring says why; the verify-step split is explained only
  in `item-1-4-s4-red.md`. The outline was not revised for either move.
- m21. The `test_verify_step_exemption.py` module docstring still states the
  `` M memory``-only exemption from before KD-7.
- m22. `test_no_item_report_exits_1` also pins two exit-2 branches, and runs
  them first. A regression in either fails under a name that says "exits 1".
- m23. The fail-closed `exempt-paths.sh` load guard
  (`ERROR: cannot load EXEMPT_PATHS_ALTERNATION`) is untested in both scripts.

## Gap Analysis

| Design requirement | Status |
|---|---|
| Item 1.1 — porcelain states and single-level globs pinned | covered (placement m20) |
| Item 1.2 — `changed-files.sh`, `exempt-paths.sh`, KD-1 base, KD-6 filters | covered; NUL read unpinned M6; m1–m3 |
| Item 1.3 — triage diffs on `<base> HEAD` | covered; interaction with KD-1 is C1, M1 |
| Item 1.4 — `--phase` and the quotePath test | covered |
| Item 2.1 — `SKILL.md` resume test, §4.1 order, §5, §6, under 200 lines | covered (196 lines); option-3 naming M4 |
| Item 2.2 — `escalation.md` remediation, revert, never-returns, §Resuming | covered; m12, m17, m7 |
| Item 2.3 — `phase-boundary.md` `--phase`, UNFIXABLE, commit | covered |
| Item 2.4 — `finishing.md` changed files, KD-5 groups, commits | covered; m15, m16 |
| Item 2.5 — review template base, report-only UNFIXABLE and `blocked:`, example | covered; m18 |
| Item 2.6 — `dispatch-composition.md` slugs, `final-review`, labels, truncation | covered; m10, m11 |
| Item 2.7 — `tdd-slice.md` by-path commits, §4.5 pointer | covered; M5 |
| Item 2.8 — `escalation-acceptance.md` clean tree, rollback, recovery pointer | partial — committed-fix revert M2; m14 |
| Item 2.9 — `review-requirement.md` changed-files form, routing rows | covered; routing target conflict M3 |
| Item 2.10 — `tdd-auditor.md` phase boundaries, job label | covered; M5 |
| Item 2.11 — `plugin/README.md` §Scripts | covered; overclaim m13 |
| Item 2.12 — D-86 in the past tense | covered |
| Item 2.13 — KD-8 subjects in `test-driver.md` and `refactor.md` | covered |
| Item 2.14 — D-88 to D-94 recorded, with rejected alternatives | covered (new node, by ruling); m19 |
| Item 2.15 — `PLR0913` removed from both `run-lint-checks` copies | covered |
| KD-4 — every orchestrator commit uses `git commit -- <paths>` | covered; m14 |
| KD-8 — job-named subjects in shipped text | covered (the run's own commits used the pre-job text) |
| build-defects Item 2.9 — `delegation.md` | covered; m10 |

## Summary

| Severity | Count |
|---|---|
| Critical | 1 |
| Major | 6 |
| Minor | 23 |

**Root causes.** C1 and M1 come from one cause: `triage-feedback.sh`'s evidence
model predates KD-1 and KD-6. M2, M3 and M4 are leg 4's open items 3, 2 and 4,
still unresolved in the shipped text. M2 and M4 need my human partner's
decision before a fix. M3 is owned by defect 21.

**Test run.** The targeted suite run by the tests reviewer gave 23/23 passed.

**Working tree at review time.** `git status --porcelain` is not clean:

- staged: `.claude/handoff-task.md`, `.claude/handoff-todo.md`;
- modified and uncommitted: `.claude/rules/workflow-work.md`, which adds
  `build-run-state.md` to the workflow routing and is leg 4 open item 1's
  separate call;
- untracked: `inbox/brief-corrector-reads-surfaces-against-each-other.md`.

## Sub-reports

- `plans/build-fixes/reports/deliverable-review-code.md`
- `plans/build-fixes/reports/deliverable-review-tests.md`
- `plans/build-fixes/reports/deliverable-review-prose-config.md`
