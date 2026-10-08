# Deliverable Review: review-fixes-3

**Date:** 2026-10-08
**Methodology:** docs/references/deliverable-review.md (axes as shipped in
`plugin/skills/deliverable-review/references/axes.md`)

## Inventory

**Baseline.** `plans/review-fixes-3/outline.md` (no `design.md`): KD-1 to KD-7,
Items 1.1–1.2, 2.1–2.4, 3.1–3.6 and 4.1, traceability m1–m18 of round 3
(`plans/review-fixes-2/reports/deliverable-review.md`) plus C-1 and C-2.

**Range.** `edify-review-range.sh plans/review-fixes-3/outline.md` returned
`UNRESOLVED: this`. The outline's `Base:` is not a sha but a rule: "this job's
own run base, from its first item report (D-88)". That rule is deterministic:
`changed-files.sh review-fixes-3` prints `BASE: daad4769…`, and the first
item-report commit `4a154234` has `daad4769` as its parent. The review used
`daad4769..HEAD`: 36 commits, this job only, unlike round 3's three-job range.
The review judges the final state at HEAD.

**Total.** 1,626 changed lines (+1,252/−374) over 27 files outside `plans/`,
`tmp/` and the handoff files. That falls in the 500–2,000 band, so Layer 1 ran
two opus reviewers: code+tests, and prose+docs.

| Type | File | Range +/− |
|---|---|---|
| Code | `plugin/bin/triage-feedback.sh` | +34/−1 |
| Code | `plugin/skills/build/scripts/changed-files.sh` | +21/−12 |
| Test | `tests/test_changed_files.py`, `tests/test_changed_files_errors.py` (new), `tests/test_changed_files_phase.py`, `tests/changed_files_helpers.py` | +249/−167 |
| Test | `tests/test_triage_feedback.py`, `_failures.py` (new), `_location.py` (new), `_behavioral.py`, `_log.py`, `tests/triage_feedback_helpers.py` | +490/−82 |
| Test | `tests/test_build_prose_git_log.py` (new) | +262 |
| Test | `tests/verify_step_helpers.py` | +1/−1 |
| Agentic prose | `plugin/skills/build/references/{finishing,escalation,dispatch-composition,phase-boundary,tdd-slice}.md` | +69/−36 |
| Agentic prose | `plugin/skills/design/references/triage.md` | +17/−5 |
| Agentic prose | `plugin/agents/{refactor,tdd-auditor}.md`, `agents/learnings.md` | +7/−5 |
| Human docs | `docs/references/build-run-state.md` (273 lines) | +85/−61 |
| Human docs | `docs/decisions.md`, `docs/references/pipeline-contracts.md` | +4/−4 |
| Human docs | `plugin/README.md` | +13 |

**Conformance summary.** Every outline item has its deliverable, and every
round-3 finding m1–m18, plus C-1 and C-2, is resolved as its item contracts
(Gap Analysis). Unspecified deliverables, each stating why it exists:

- `tests/test_triage_feedback_location.py`: a line-cap split recorded in the
  outline's list revision after 2.2/2.
- The D-86 `--no-show-signature` site in `docs/references/pipeline-contracts.md`.
  It is beyond KD-7's list, and the outline's list revision after 2.4/1
  records it. The diff is the flag alone, the file is in the test's `SCANNED`
  set, and stripping the flag fails `pipeline-contracts.md:1` (code+tests
  sub-report). Explained excess, consistent with D-88 stating the reason once.
  Not a finding.
- The review gate's skill-review fixes in `finishing.md` §1 (one gate commit
  carrying `review-plan-*` reports and planning-corrector plan edits; step 2
  setting planning artifacts aside) and the `-list-revision-fix` name in
  `dispatch-composition.md` and `escalation.md`. These go beyond Item 3.2's and
  3.3's contracts, and `build-leg4.md` §Open questions 3 records them.
  Reviewed below against the design graph (attention item 1).

**Probe on the real job.** On a throwaway clone of HEAD at a path containing a
space, `bash ../plugin/bin/triage-feedback.sh review-fixes-3`, run from `docs/`,
printed `Files changed: 27`, `Reports: 34`, `Behavioral code: yes`,
`Review artifact: review` and verdict `match`. It exited 0, appended a row to
the root's log and created nothing under `docs/`. KD-6 and whitespace safety
hold on real data. `Reports: 34` against the logged 33 is
`build-leg4.md`, committed after Finish, so a second row was logged. That is
D-90's stated m3 bound at work ("such as" covers a leg report). Not a finding.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

Round-4 findings are F1–F7, kept apart from round 3's m1–m18, which the
Gap Analysis cites as requirements.

**Design record lags the gate's late fixes (attention item 1)**

- **F1.** `docs/references/build-run-state.md` D-93 and D-89's finishing-stage
  paragraph. Axes: completeness and consistency.
  - D-93 presents the `review-*.md` match of `review-plan-*` reports only as a
    benefit ("so the gate's landed check (D-89) … read its report as a review
    report").
  - `finishing.md` §1, since `b4e1cf11`, names the hazard: "A `review-plan-*`
    report committed on its own, ahead of the group reports, would read as the
    gate landed". It answers the hazard with one commit for the whole gate,
    which includes a planning corrector's edits to the source job's plan file.
    It also places the reports under the running job's `reports/`.
  - No `docs/` node records that invariant or the report location. D-89's
    widened check is correct only because of it, and a later edit that splits
    the gate commit would find nothing in D-89 or D-93 against it.
  - This is an omission, not a contradiction: D-86, D-90, D-92 and D-94 and
    `pipeline-contracts.md` all still agree with both late fixes.
  - The `-list-revision-fix` name has no docs counterpart to disagree with,
    because D-92 does not name the remediation dispatch.
  - Found independently in Layer 2 and by the prose sub-report (P1).
- **F2.** `finishing.md` §1, the planning-artifact paragraph, and D-93's
  opening. Axes: constraint precision and consistency.
  - "Planning artifacts do not route through this gate" and "The `/build`
    review gate routes implementation files only" now sit beside text in which
    the gate sets planning artifacts aside, dispatches them, Reads their
    reports and commits them.
  - "Not through the four group rows" is what both sentences mean, and neither
    says it. Prose sub-report P6.

**Untested exit-2 arm (attention item 2)**

- **F3.** `plugin/bin/triage-feedback.sh`, the `if ! cd "$repo_root"` guard and
  the residual-bound comment above it. Axes: coverage, testability.
  - The comment says neither `cd` arm can be tested because "no input provokes
    either without fault injection". For the repository-root `cd` that is
    false, by three independent routes:
    - a `git` shim through `_write_shim` and `path_prepend`, the suite's
      existing mechanism, answering `rev-parse --show-toplevel` with a missing
      directory (code+tests sub-report);
    - a repository root whose name ends in a newline, which `$(…)` strips
      (code+tests sub-report);
    - `GIT_DIR=<repo>/.git GIT_WORK_TREE=<mode-000 dir>`. `rev-parse` exits 0
      and prints the directory, and the script then printed
      `ERROR: cannot change to …` and exited 2 (Layer 2 probe). This is the
      suite's existing permission-fixture style, with no shim at all.
  - Dropping both `cd` guards leaves all 33 triage tests green. Without the
    root guard, `set -e` exits 1, the usage code, with empty stdout.
  - KD-5 reversed round 2's exemption on exactly this ground: the mechanism
    already existed.
  - **Judgement on the bound:** acceptable for the script-directory `cd` only.
    It is a builtin fed by `BASH_SOURCE`, and nothing in the suite reaches it.
    The one reach found, an exported `BASH_FUNC_cd%%`, would be new,
    bash-version-dependent infrastructure.
  - Not acceptable for the root `cd`. It needs one test in
    `test_triage_feedback_failures.py`, and the comment should then narrow to
    the script-directory arm.
  - Rated Minor, as round 3 rated untested triage arms (m4–m6). The outline's
    Interfaces pre-accepted the bound on the same false premise.

**Prose precision and excess**

- **F4.** `plugin/README.md` §Optional plugins. Axis: completeness.
  - It opens "Each entry says what is lost without it". The `plugin-dev` entry
    then lists only the review gate's consequences.
  - The edify skills that name `plugin-dev:*` skills to load go unmentioned:
    `design/references/write-outline.md`,
    `requirements/references/formats-and-exit.md` and `build/SKILL.md` §3.3.
  - Item 3.6's two review-gate clauses do conform. Prose sub-report P2.
- **F5.** `plugin/skills/design/references/triage.md` §Classification Gate,
  persistence paragraph. Axis: constraint precision.
  - "Open the file with one job-level … line" competes with the purpose clause
    ("so that no other `Classification:` line … can precede it").
  - This job's own `classification.md` opens with a heading and a prose
    paragraph. It still parses `Moderate`.
  - The text does not say whether a heading may precede the line. Prose
    sub-report P3.
- **F6.** Same paragraph. Axes: determinism, actionability.
  - Defect's place in a mixed composite is left to inference.
  - The closing sentence carries forward-looking state ("yet", "will come
    from", "once composite jobs have logged rows") where a bare "ungrounded"
    clause would carry the flag.
  - Both conform to KD-3's wording. Prose sub-report P4.
- **F7.** `agents/learnings.md` §"When calling triage-feedback.sh",
  Anti-pattern bullet. Axis: excess.
  - It quotes `changed-files.sh`'s full error message verbatim, and narrates
    triage's two output lines.
  - A prose copy of a script message drifts when the message changes, and the
    line is the file's longest at 654 characters.
  - The content is accurate. Prose sub-report P5.

**Observed, not raised.** `tests/triage_feedback_helpers.py`'s module docstring
says `_run_triage_relative` runs "from a subdirectory". The `CDPATH` test calls
it from the root, and the function's own docstring is accurate (code+tests
sub-report).

**Out of scope, noted once.** These were ruled out and are not findings:

- the bash 3.2 `source` defect in `changed-files.sh` when `exempt-paths.sh` is
  absent, and the absent bash-3.2 suite run;
- test D's output-side `printf '%b'` gap;
- final-review fixes landing after triage.

`edify-review-range.sh` cannot parse a D-88-style rule `Base:`, and returns
`UNRESOLVED:`. That is another job's script and an input to its owner, not a
finding here.

## Gap Analysis

| Requirement | Item | Status |
|---|---|---|
| m1 triage measures from the root (KD-6) | 2.2 | covered; the residual bound is F3 |
| m2 `ERROR:` alone (KD-4) | 2.1 | covered (genuine red against `daad4769`) |
| m3 re-run bound in D-90 | 4.1 | covered |
| m4–m6 triage failure arms (KD-5) | 2.3 | covered, each mutant killed on its assertion; new root-`cd` arm: F3 |
| m7–m9 triage split and docstrings | 1.2 | covered |
| m10 changed-files split, no KD-N | 1.1 | covered |
| m11 learnings call pattern | 3.1 | covered; excess: F7 |
| m12 `review-plan-<source job>-<stem>` (KD-1) | 3.2, 4.1 | covered on all four surfaces; seams: F1, F2 |
| m13 refactor plan-sources reason | 3.4 | covered |
| m14 `--no-show-signature` (KD-7) | 2.4, 4.1 | covered, D-86 site included |
| m15 job-level classification line (KD-3) | 3.5 | covered; precision: F5, F6 |
| m16 D-89 finishing stages, D-90 row rule (KD-2) | 4.1 | covered; invariant gap: F1 |
| m17 Rejected entry relabelled | 4.1 | covered |
| m18 header reflow | 2.1 | covered |
| C-1 `<step name>-fix` | 3.3 | covered, `-list-revision-fix` consistent in both files |
| C-2 README optional plugins | 3.6 | covered; completeness: F4 |

## Summary

0 critical, 0 major, 7 minor.

- Design-record seams from the gate's late fixes: F1, F2.
- Untested root-`cd` arm, whose stated bound is false: F3.
- Prose precision and excess: F4–F7.

All of round 3's m1–m18, and C-1 and C-2, are resolved at HEAD. The code and
tests verified by mutation, a bash 3.2.57 parse and a spaced-path dogfood run.

## Sub-reports

- `plans/review-fixes-3/reports/deliverable-review-code-tests.md` (code and
  tests: 0/0/1)
- `plans/review-fixes-3/reports/deliverable-review-prose-config.md` (prose and
  docs: 0/0/6)
