# Deliverable Review: review-fixes-2

**Date:** 2026-10-07
**Methodology:** docs/references/deliverable-review.md

## Inventory

**Baseline.** `plans/review-fixes-2/outline.md` (no `design.md`), KD-1 to
KD-9 and Items 1.1–1.6, 2.1–2.11 and 3.1–3.4, including the N-1 slice my human
partner added to Item 1.1. `edify-review-range.sh` returned
`RANGE: d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`. The outline inherits
that base from `plans/build-fixes/outline.md`, so the range covers
build-defects, build-fixes and review-fixes-2: 131 commits. review-fixes-2
itself starts after `79d0b687` (43 commits). The review judges the final state
at HEAD and checks that the round-2 findings
(`plans/build-fixes/reports/deliverable-review.md`) are resolved.

**Total.** 3,728 changed lines outside `plans/`, `tmp/` and the handoff files.
That is above 2,000, so Layer 1 ran three opus reviewers: code, tests, and
prose+config. The review-fixes-2 delta alone is 1,989 lines over 33 files.

| Type | File | Range +/− (review-fixes-2 delta) |
|---|---|---|
| Code | `plugin/bin/triage-feedback.sh` | +188/−25 (+188/−37) |
| Code | `plugin/skills/build/scripts/changed-files.sh` | +134 (+20/−14) |
| Code | `plugin/skills/build/scripts/exempt-paths.sh` | +15 (+1/−1) |
| Code | `plugin/skills/build/scripts/verify-step.sh` | +50/−6 (+5/−3) |
| Test | `tests/test_triage_feedback.py` (366 lines) | +366 (+312/−202) |
| Test | `tests/test_triage_feedback_behavioral.py`, `tests/test_triage_feedback_log.py`, `tests/triage_feedback_helpers.py` (new) | +579 |
| Test | `tests/test_changed_files.py` (391 lines), `tests/test_changed_files_phase.py`, `tests/changed_files_helpers.py` | +683 (+185/−24) |
| Test | `tests/test_verify_step.py`, `tests/test_verify_step_exemption.py`, `tests/verify_step_helpers.py` | +506 (+70/−7) |
| Test | `tests/test_line_limits_wc_padding.py` | +10/−10 |
| Agentic prose | `plugin/skills/build/SKILL.md` (199 lines) | +50/−39 (+11/−8) |
| Agentic prose | `plugin/skills/build/references/{finishing,escalation,phase-boundary,dispatch-composition,review-dispatch-template,tdd-slice}.md` | +477/−139 (+134/−62) |
| Agentic prose | `plugin/agents/{tdd-auditor,test-driver,refactor}.md` | +52/−37 (+25/−18) |
| Agentic prose | `plugin/fragments/{review-requirement,escalation-acceptance,delegation}.md` | +70/−33 (+22/−9) |
| Human docs | `docs/references/build-run-state.md` (249 lines) | +249 (+86/−25) |
| Human docs | `docs/decisions.md`, `docs/design.md`, `docs/references/pipeline-contracts.md` | +65/−28 (+20/−11) |
| Human docs | `docs/changelog.md` and the 2026-10-03 and 2026-10-06 entries | +72 (+40) |
| Human docs | `plugin/README.md` | +28/−4 (+20/−8) |
| Human docs | `plans/build-fixes/outline.md` (Item 3.4, after the fact) | in `plans/`, read directly |
| Configuration | `justfile`, `plugin/portable.just`, `CLAUDE.md`, `.claude/rules/workflow-work.md`, `.gitignore`, `.bin/claude` | +31/−14 (+2/−2) |
| Other | `inbox/brief-runbook-slice-enumerates-predicate-boundaries.md` | +21 |

**Conformance summary.** Every outline item has a matching deliverable.
Unspecified deliverables:

- `tests/test_triage_feedback_behavioral.py` and
  `tests/test_triage_feedback_log.py`: line-cap splits the outline did not
  name. Each module docstring states why it exists (see m7).
- `.claude/rules/workflow-work.md` landed in `888eda7a`. That commit is ahead
  of the run's first item report, so it falls outside the run's own list. It
  is the round-2 open item my human partner decided separately.
- `.bin/claude`, `.gitignore`, `justfile` `clean`, `CLAUDE.md` scraper line,
  `memory` pointer and the inbox brief are earlier rounds' non-job commits, as
  round 2 recorded. None is counted as excess.

**Probe on the real job.** On a throwaway clone of HEAD,
`triage-feedback.sh review-fixes-2` gave `Files changed: 33`, `Reports: 46`,
`Behavioral code: yes`, verdict `match`, and appended a second row. The
logged row says 45 reports. The difference is `build-leg4.md`, committed after
Finish (see m3).

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**Code robustness and error signaling**

- m1. `plugin/bin/triage-feedback.sh`, top level (the evidence and
  classification sections). Run from a subdirectory, the script prints wrong
  evidence and exits 0. `changed-files.sh` changes to the repo root, but
  triage then resolves the root-relative list as `:(literal)` pathspecs, plus
  the reports pathspec, `classification.md` and `reports_dir`, against the
  CWD. Probe: from the root, `Files 1, Reports 1, Behavioral yes,
  underclassified`. From a subdirectory, `Files 1, Reports 0, Behavioral no,
  no-classification`, exit 0. `finishing.md` §2 runs it from the root, so
  `/build` does not hit this. Source: code m1.
- m2. `plugin/skills/build/scripts/changed-files.sh`, the final
  `git diff … | while read` pipeline. A diff failing late prints `ERROR:` after
  `BASE:` and the paths already emitted. Item 1.5 says "an exit 2 prints
  `ERROR:` first". The exit code is right, and both consumers key on it.
  Probed with a `git` shim. Source: code m2.
- m3. `plugin/bin/triage-feedback.sh`, the report count, with D-90's
  re-run sentence and the 2026-10-06 changelog entry. D-90 says "Both drops
  keep a re-run on the set the first run measured". Reports committed under
  `plans/<job>/reports/` after Finish still count, and a re-run then logs a
  second row. For a Simple job that row can flip from `match` to
  `underclassified`. The pipeline's own named follow-up does this:
  `/deliverable-review plans/<job>` (`finishing.md` §3.4) writes
  `deliverable-review*.md` there. The probe above shows the effect on this
  job: Reports went from 45 to 46 after `build-leg4.md`, and a second row was
  logged. The prose reviewer adds that `final-review`'s fixes in the closing
  commit break the same sentence, and D-90 does not state that bound. Leg-4
  open item 2 rules that case acceptable, but the design text still claims
  the opposite. A fix is either a bound stated in D-90 or a wider exclusion.
  Source: Layer 2, and prose (refinement of leg-4 open item 2).

**Tests: coverage of interface failure clauses** (leg-4 open items 3–4,
confirmed and refined)

- m4. `plugin/bin/triage-feedback.sh` failure arms with no test. Every arm
  behaves correctly when probed.
  - The behavioural-code grep exit ≥ 2 arm. The outline exempts it (m5).
  - The classification grep exit ≥ 2 arm. `chmod 000` on `classification.md`
    reaches it without a shim, the way `test_unreadable_log_is_…` pins the
    log read.
  - The classification `sed` failure arm.
  - The `mkdir -p plans/reports` failure arm, which leg 4 does not list.
  Mutants dropping the `sed failed` arm or the classification `grep failed`
  arm stay green. Source: code m3, and tests (open item 4).
- m5. `tests/test_triage_feedback.py`,
  `test_no_base_is_an_error_with_no_log_row`. Only the `NO-BASE:` (exit 1)
  pass-through is tested. The mutant `[[ $status -eq 1 ]]` stays green. On an
  unborn repo it loses the cause line, and the `ERROR:` text goes to git as a
  revision. It still fails closed. Source: tests m1.
- m6. Triage's usage exit (exit 1, `Usage: triage-feedback.sh <job>`) has no
  test, including the retired `<job> <base>` call that a stale caller would
  make. The no-test claim comes from `rg`; the mutant was not run. Source:
  tests m2.

**Tests: placement and docstrings**

- m7. `tests/test_triage_feedback.py` module docstring. The triage tests are
  split across three modules. The hub names only the behavioural one and
  gives no reason for the split. `test_triage_feedback_log.py`, which the
  outline does not name, is not mentioned. Source: tests m3.
- m8. `tests/verify_step_helpers.py` module docstring. It points at "the
  subprocess-run pattern in `tests/test_triage_feedback.py`", which moved to
  `triage_feedback_helpers.py`. Source: tests m4.
- m9. `tests/test_triage_feedback_log.py` module docstring. It says "a run is
  skipped" where KD-2 and the script skip the append only. Source: tests m5.
- m10. `tests/test_changed_files.py`. The module is at 391 lines against the
  400 gate, after growing by 197 in this job. Its docstrings cite both
  build-fixes `KD-N` and `D-N`. The Item 1.3 test opens "Item 1.2 reads the
  diff NUL-delimited", which means build-fixes' Item 1.2 but reads as this
  job's. Source: tests m6.

**Cross-surface consistency**

- m11. `agents/learnings.md` §"When calling triage-feedback.sh". The
  "Correct pattern" still gives `triage-feedback.sh outline-proofing baseline`,
  which now exits 1 with `Usage:`. The file is live: `/ground`'s
  `grounding-criteria.md` and `/proof` read it. Verified with `rg`. Source:
  code m4.
- m12. `plugin/skills/build/references/finishing.md` §1 (the
  planning-artifact paragraph), with `dispatch-composition.md` §Naming and
  resumption. A planning artifact on the list routes "by artifact", but no
  surface gives that dispatch a name or report path. The report name carries
  mechanism: KD-4's landed check, triage's report exclusions and its
  `Review artifact` probe all key on `review-*.md`. This job's gate committed
  an invented `review-outline.md` for `plans/build-fixes/outline.md`, and it
  works only because the slug matches. The outline-corrector's own default,
  `outline-review.md`, would:
  - overwrite the job's planning report;
  - never read as landed;
  - draw `No corrector report`.
  Source: prose m1, verified against `94c0f6c4`'s file list.
- m13. `plugin/agents/refactor.md` §Step 5. The prohibition covers every plan
  source, but the reason still names `runbook.md` alone as "the
  orchestrator's artifact". This is a residual of M5 under KD-7. Source: prose
  m3, verified.
- m14. `plugin/skills/build/references/phase-boundary.md` §Base and changed
  files, D-89, and `tdd-auditor.md` check 2. Their `git log` queries lack
  `--no-show-signature`, which `changed-files.sh` and `finishing.md`'s landed
  checks pass for the stated reason. A user's `log.showSignature` would turn
  P>1's hash comparison into a spurious STOP. Reasoned, not probed. Source:
  prose m4.
- m15. `plugin/skills/design/references/triage.md` §Classification Gate
  (outside scope; a seam with N-1). The producer template still renders
  `[Simple / Moderate / Complex / Defect]` "per-item if composite" and does
  not require one bare label. Composite labels keep being produced, and N-1
  now drops them to `no-classification`, so the rows are lost to calibration.
  Proposed only. Source: prose m6, verified.

**Design record**

- m16. `docs/references/build-run-state.md`. The KD-4 landed checks for the
  finishing stages, and KD-2's one row per evidence as a decision, are in no
  decision. KD-2 appears only as a clause inside D-90. The Rejected entry "A
  landed check on triage keyed on the triage log" therefore stands against a
  positive decision the node never states. This is leg-4 open item 6, not
  ruled. Source: Layer 2, and prose.
- m17. `build-run-state.md` §Rejected alternatives and the `decisions.md`
  *Rejected:* line. "Triage dropping its own log path from the list", read as
  a one-line conclusion, contradicts D-90, where the list does drop it. What
  was rejected is triage filtering it on its own side. Source: prose m2.

**Style**

- m18. `plugin/skills/build/scripts/changed-files.sh` header comment: one line
  of the D-90 paragraph was not reflowed (89 columns). Source: code m5.

**Not counted.** The prose reviewer noted that the baseline's KD-1 Reports
bullet ("added at the review gate") reads as if `tdd-audit.md` were written at
the gate. That wording is in the outline, a planning artifact, not a
deliverable.

**Leg-4 open items.**

- 1–2 (ruled unchanged): no reviewer found either worse than stated. m3 is a
  related but separate path: reports committed after Finish, as opposed to
  `final-review`'s fixes.
- 3–5: confirmed open, and refined in m4–m7.
- 5: also confirmed. An `echo -e` mutant of the unrecognised-label line stays
  green, because no test label carries a backslash.
- 6: the parts not covered by m16 stand. `plugin/README.md` names neither
  `plugin-dev` nor `craft` as optional, and no surface states the
  `phantom-untracked` two-name threshold.
- 7: outside this job's files.

## Gap Analysis

| Design requirement | Status |
|---|---|
| Item 1.1: triage takes `<job>`, KD-1 evidence model, m4–m6, N-1 (C1, M1) | covered: C1, M1, m4, m5, m6, N-1 resolved and probed; m1, m3, m4–m6 |
| Item 1.2: KD-2 idempotent append (m7) | covered: probed, one row per evidence; re-run bound m3 |
| Item 1.3: NUL read pinned (M6) | covered: four mutants each red the test |
| Item 1.4: `exempt-paths.sh` load guard (m23) | covered in both scripts, with an inherited-variable case |
| Item 1.5: no `exec 2>&1`, D-IDs in comments (m1, m8) | covered; late-failure order m2; reflow m18 |
| Item 1.6: test hygiene (m20–m22, wc-padding docstring) | covered; docstring drift m7–m9 |
| Item 2.1: `SKILL.md` Item 1.1, §4.4, §5, under 200 (M4, m13) | covered (199 lines) |
| Item 2.2: `finishing.md` KD-4, `NO-BASE:` fault, empty list, no base, m15 | covered; planning-artifact report name m12 |
| Item 2.3: `escalation.md` m9, m12, m17 | covered |
| Item 2.4: `tdd-slice.md` KD-7, KD-6 (M5, m13) | covered; `refactor.md` residual m13 |
| Item 2.5: `tdd-auditor.md` hosting file (M5) | covered; `--no-show-signature` m14 |
| Item 2.6: `dispatch-composition.md` m10, m11 | covered |
| Item 2.7: `review-requirement.md` skill row (m11) | covered |
| Item 2.8: `delegation.md` resume by id (m10) | covered |
| Item 2.9: `escalation-acceptance.md` KD-5, m14 (M2) | covered |
| Item 2.10: template example UNFIXABLE (m18) | covered |
| Item 2.11: `plugin/README.md` (C1, M1, m9, m13) | covered |
| Item 3.1: D-90, D-91, D-92, D-93, `decisions.md` (m2, m3, m9, m11, m19) | covered; re-run claim m3, KD-4 record m16, Rejected label m17 |
| Item 3.2: `design.md` L-2 | covered |
| Item 3.3: changelog entry and index | covered; re-run claim m3 |
| Item 3.4: `plans/build-fixes/outline.md` revision (m3, m20) | covered |
| M3 (out of scope, defect 21) | not reviewed |

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| Major | 0 |
| Minor | 18 |

Every round-2 finding in scope is resolved: C1, M1, M2, M4, M5, M6 and
m1–m23, plus N-1. M3 is excluded. m2 is resolved as a documented D-90
limitation. The resolution of C1, M1, m3–m7, m23 and N-1 was probed, not only
read.

No regression rose above Minor. The new findings cluster in three places:

- the re-run claim around the report count (m3);
- untested failure clauses of the new interfaces (m4–m6, which extend leg-4
  open items 3–4);
- small cross-surface and documentation drift (m7–m18).

**Test run.** Targeted triage, changed-files, verify-step and wc-padding
modules: 51/51 passed (tests reviewer) and 50/50 without the wc-padding module
(code reviewer), in the foreground. The full `just precommit` was not run in
this review.

**Working tree at review time.** `git status --porcelain` was not clean:

- staged: `.claude/handoff-task.md`, `.claude/handoff-todo.md`;
- untracked: `inbox/brief-corrector-reads-surfaces-against-each-other.md`;
- untracked: the review's own `plans/review-fixes-2/reports/deliverable-review*.md`.

## Sub-reports

- `plans/review-fixes-2/reports/deliverable-review-code.md`
- `plans/review-fixes-2/reports/deliverable-review-tests.md`
- `plans/review-fixes-2/reports/deliverable-review-prose-config.md`
