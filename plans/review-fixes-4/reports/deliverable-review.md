# Deliverable Review: review-fixes-4

**Date:** 2026-10-09
**Methodology:** deliverable-review skill, `references/axes.md`

## Inventory

**Baseline.** `plans/review-fixes-4/outline.md` (no `design.md`): Item 1.1
(F3, tdd) and Item 1.2 (F1, F2, F4–F7, verbatim prose edits), traceability
F1–F7 of round 4 (`plans/review-fixes-3/reports/deliverable-review.md`).

**Range.** `edify-review-range.sh plans/review-fixes-4/outline.md` printed
`NO-PROVENANCE:` and exited 1: the outline's `Derived from:` names the round-4
report without a `superseding` clause. Per the skill that verdict asks the user
for the range; my human partner's main session set it in the dispatch:
`8eb1c9629fea5e12361e906b1135b70fbc60b345..HEAD`, which equals the outline's own
`Base:`. That is 8 commits, this job alone, as round 4 reviewed `review-fixes-3`
alone. It includes the follow-up `02456e97`, which applies F2's wording to a
third site in `dispatch-composition.md`. The review judges the final state at
HEAD.

**Total.** 127 changed lines (+84/−43) over 8 files outside `plans/`, `tmp/`
and the handoff files. Under 500, so Layer 1 was skipped and Layer 2 ran the
full per-file and cross-cutting review.

| Type | File | Range +/− |
|---|---|---|
| Code | `plugin/bin/triage-feedback.sh` | +4/−3 |
| Test | `tests/test_triage_feedback_failures.py` | +30 |
| Agentic prose | `plugin/skills/build/references/finishing.md` | +4/−4 |
| Agentic prose | `plugin/skills/build/references/dispatch-composition.md` | +2/−2 |
| Agentic prose | `plugin/skills/design/references/triage.md` | +14/−11 |
| Agentic prose | `agents/learnings.md` | +1/−1 |
| Human docs | `docs/references/build-run-state.md` | +26/−21 |
| Human docs | `plugin/README.md` | +3/−1 |

**Conformance summary.** Every F1–F7 edit is present at its site and matches
the outline's text verbatim after rewrap. Changed lines respect the 80-column
wrap (the `awk` overages in these files are pre-existing lines or a two-byte
`§`). `docs/decisions.md`'s D-93 line ("Review-gate groups are four fixed rows,
with fixed slugs.") paraphrases neither changed sentence, and `just precommit`
is green: design-links reports 94 decisions, conclusions match. No
`plugin/fragments/` file is in range, so the fragment-convention check is N/A.

Two edits go beyond the outline's verbatim list; each states why it exists:

- `triage.md` §Classification Gate, the sentence before the block template. The
  review gate's `review-skill` reviewer found its "first line" and "opens with"
  wording barred what F5 permits, and the session reworded it twice
  (`reports/review-skill.md`). The build leg noted the last rewording went
  unreviewed by design; this review now covers it (R1).
- `dispatch-composition.md` §Naming and resumption, commit `02456e97`: F2's
  wording at the third site the `review-design` reviewer flagged as
  OUT-OF-SCOPE (`reports/review-design.md`, `build-leg1.md` open question 1).

**Residual pre-fix wording.** No tracked file outside `plans/` still carries
"routes implementation files only", "route through this gate", "first line is
the job-level line" or "Open the file with one" (`git grep`).
`review-dispatch-template.md` §Field Rules' "Implementation only: planning
artifacts route as `finishing.md` §1 says, not through this template" is not
the pre-F2 sentence. It speaks of the template, and `finishing.md` §1 step 4
applies the template to the group rows only, so it is accurate.

**F3 mutation red, reproduced.** On HEAD,
`just test tests/test_triage_feedback_failures.py -k root_cd` passed 1/1. With
the `if ! cd "$repo_root"; then … fi` block replaced by a bare
`cd "$repo_root"`, the test failed on its stdout assertion
(`assert '' == 'ERROR: canno...issing root\n'`). A direct run under the same
mutation, with the same shim shape, measured the exit code that neither the RED
dispatch nor the test review read: exit 1 with empty stdout. That confirms the
docstring's "A bare `cd` under `set -e` exits 1 with empty stdout". Unmutated,
the same direct run exits 2 with `ERROR: cannot change to <path>` on stdout.
The script was restored from a saved copy, and
`git diff --stat -- plugin/bin/triage-feedback.sh` came back empty. The test
review's `exit 3` mutation already showed the exit-code assertion
discriminates. The red is genuine: the asserted line is unique to the root `cd`
guard, and the shim makes `rev-parse` succeed, so the earlier guard cannot
produce it.

**F7 accuracy, probed.** In a throwaway repo,
`triage-feedback.sh plans/x` printed `changed-files.sh`'s `not a job name`
refusal plus `ERROR: changed-files.sh exited 2` and exited 2. A two-argument
call printed `Usage: triage-feedback.sh <job>` and exited 1. The new bullet's
claims hold.

**F4 accuracy.** `plugin-dev:*` skills are named for loading in
`requirements/references/formats-and-exit.md`,
`design/references/write-outline.md` and `design-content-rules.md`, and
`build/SKILL.md` §3.3. That matches the README's "`/requirements`, `/design`
and `/build` steps". The `craft` entry needs no parallel sentence: `craft:*` is
named only by the review gate's design-graph row and its template field.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

Round-5 findings are R1–R2, kept apart from round 4's F1–F7, which the Gap
Analysis cites as requirements.

**Constraint precision**

- **R1.** `plugin/skills/design/references/triage.md` §Classification Gate, the
  sentence before the block template (the review gate's reword). Axes:
  consistency and constraint precision.
  - It reads: "A single-item job's block is the whole file, and its block opens
    with the job-level line."
  - Taken together, the two clauses still make the job-level line the file's
    first line. That is the pre-F5 sense, which the persistence paragraph
    loosened with "a heading or prose may come before it".
  - The composite sentence ("puts one job-level … line ahead of its blocks")
    does agree with F5.
  - This job's own `classification.md` opens with the label line, followed by
    a heading and prose. It parses either way, so the effect is only that an
    agent reading the template sentence could take a heading to be forbidden.
  - Dropping "is the whole file" (e.g. "A single-item job writes one block,
    opening with the job-level line") would remove the tension.

**Determinism of the composite rule**

- **R2.** `triage.md` §Classification Gate, persistence paragraph, F6's
  sentence. Axes: determinism, consistency.
  - The sentence is "in a mixed job a Defect item does not raise the label,
    which is the most demanding non-Defect item's class".
  - It conforms to KD-3 (`plans/review-fixes-3/outline.md`). KD-3's order is
    Simple < Moderate < Complex, with Defect outside it and "the job-level
    label only when every item is a Defect". F6's sentence is the only reading
    consistent with both, so it states what KD-3 left implicit. It does not
    change the rule, and its "ungrounded" clause is correct.
  - Made explicit, the rule has a predictable effect on the triage log. Take a
    job of {Defect, Simple}: it is labelled `Simple`. Yet the Defect item's
    work counts as evidence against that label.
  - `triage-feedback.sh`'s Simple arm returns `underclassified` when
    `behavioral_code` is `yes` or `reports_count` > 0. `reports_count` counts
    non-item, non-review reports, which slice reports are.
  - So a Defect item run as tdd slices, or one that adds a definition, logs
    that job as `underclassified`. D-38's concern is exactly this: a
    behavioural change masked by non-behavioural siblings.
  - This is inferred from the script's verdict arms, not probed on a fixture.
  - The rule was accepted at the round-4 outline gate (KD-3), so this is input
    for that decision rather than a defect in F6's edit. The triage log rows
    the "ungrounded" clause defers to are what would settle it.

**Observed, not raised.**

- `dist/plugin/` still carries every pre-F2 and pre-F5 sentence, in
  `finishing.md`, `dispatch-composition.md` and `triage.md`, as well as the
  old `triage-feedback.sh` comment. It is gitignored build output, not a
  deliverable. The skill loaded for this review ran from it, so the shipped
  fixes only take effect in sessions once it is rebuilt.
- `docs/references/build-run-state.md` D-89's finishing-stage paragraph ("the
  review gate on a `review-*.md` report") has no pointer to D-93's new
  one-commit invariant. F1 named both paragraphs, and the outline scoped the
  fix to D-93. The harm F1 stated, that a later edit splitting the gate commit
  "would find nothing in D-89 or D-93", is resolved by D-93 alone.
- D-93's first two sentences both open on "a planning artifact on its / the
  gate's list". This is outline-verbatim wording, and the redundancy is stylistic.
- On HEAD, the root `cd` failure also leaves bash's own `cd:` message on
  stderr. The test asserts stdout only, consistent with the `rev-parse` guard,
  whose comment documents the same stderr passthrough. The new comment above
  the `cd` guard does not say so.
- `plans/review-fixes-4/classification.md` calls the job composite but holds
  only the job-level line, with no per-item blocks. That falls short of
  `triage.md`'s "per-item if composite". It is a planning artifact, not a
  deliverable.

**Out of scope, noted once.** These were ruled out and are not findings:

- the bash 3.2 `source` defect in `changed-files.sh` when `exempt-paths.sh` is
  absent, and the absent bash-3.2 suite run;
- test D's output-side `printf '%b'` gap;
- final-review fixes landing after triage;
- `tdd-slice.md` naming opus for test and code reviewers, while this job ran
  them on sonnet by ruling.

## Gap Analysis

| Requirement | Site | Status |
|---|---|---|
| F1 — one-commit invariant and report location in D-93 | `build-run-state.md` D-93 | Covered (verbatim, after "read its report as a review report.") |
| F2 — "four group rows" wording | `finishing.md` §1 planning-artifact paragraph; D-93 opening; `dispatch-composition.md` §Naming and resumption (`02456e97`) | Covered at all three sites; no other tracked site |
| F3 — root `cd` guard tested, comment narrowed | `test_triage_feedback_failures.py::test_root_cd_failure_is_one_error_line`; `triage-feedback.sh` residual-bound comment | Covered; mutation red reproduced (exit 1, empty stdout) |
| F4 — `plugin-dev` entry names the skill-loading steps | `plugin/README.md` §Optional plugins | Covered; claim checked against the three skills |
| F5 — heading or prose may precede the job-level line | `triage.md` persistence paragraph | Covered; template sentence above it retains the pre-F5 sense (R1) |
| F6 — Defect in a mixed job; bare "ungrounded" | `triage.md` persistence paragraph | Covered; conforms to KD-3; triage interaction unaddressed (R2) |
| F7 — Anti-pattern bullet shortened | `agents/learnings.md` §"When calling triage-feedback.sh" | Covered; one physical line; claims probed |

## Summary

0 critical, 0 major, 2 minor (R1 constraint precision, R2 determinism of the
composite rule). All seven round-4 findings are resolved at their sites. The
F3 test's mutation red is genuine. `just precommit` is green at HEAD.
