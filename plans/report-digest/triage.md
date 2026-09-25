# Report digest — triage of §Missing from frame, 2026-09-24

Every item in `summary.md` §Missing from frame and §Unclear, left open gets one
of: a new job, a rider on an existing frame job, a fix applied here, or a drop
with its reason. Evidence for each item is in the part files; this file only
records the call.

## New jobs

### build-defects — `/edify:design`

The 21 defects migrated from the retired inline/orchestrate skills. Fix text
is in `plans/skill-reviews/reports/verify-inline.md` and
`verify-orchestrate.md`; current line numbers in `skill-reviews.md` §Migrated
defects. Needs a design because two clusters are contract choices, not edits:

- **Changed-files reference point** (orchestrate C1, M8; inline M2, m10, m12).
  The phase-boundary halt and the finishing review both diff the working tree,
  which is empty after committed dispatches. The design picks the reference
  commit (the phase-start commit, or the `Base..HEAD` range
  `edify-review-range.sh` already computes) and adds the missing
  Requirements/Constraints blocks. The inherited copy at
  `plugin/fragments/review-requirement.md:125` changes with it.
- **Dispatch contracts** (inline M1, m15, m16 first half, m6, m11). Two
  report-path rules and two return contracts each claim to be the only one;
  the design names the surviving rule and the file that owns it, and adds the
  UNFIXABLE re-review step.
- **Triage script** (inline M3): `reports_count` and the unhandled
  `WARNING: No corrector report` line — a tdd item.
- **Tool availability** (orchestrate M1, m7, M7; inline m2): drop `TaskOutput`
  from `build/SKILL.md` allowed-tools and `escalation.md:33` (it does not
  resolve; harness-tracked work re-invokes the caller on completion), keep
  `TaskStop` as an unprobed option, resolve `escalation-acceptance.md:48-49`'s
  `git clean -fd` against `escalation.md`'s remediation, fix the `&&` at
  `delegation.md:112-113`.
- **`build/SKILL.md` body** (orchestrate M4, C2, m3, m4, m5; inline m9).
- **Rider — D-86 mechanical check.** No check that a report commit carries the
  work it reports; `verify-step.sh` catches the symptom one dispatch late. The
  design decides whether the phase-boundary rework gives it a home or it
  stays a known gap.

The fragments touched here (`review-requirement.md`, `delegation.md`,
`escalation-acceptance.md`) get their content fixed in this job; their
location stays with the repo-relative-paths job (frame R2).

### script-robustness — outline, then `/build`; tdd items, no design

- `plugin/bin/edify-review-range.sh`: a subject on each of the three bare
  `NO-PROVENANCE:` sites (`:94`, `:102`, `:185`); which artifact's base failed
  on `UNRESOLVED:` (`:121`, `:168`); `none,` with an attached comma (`:129`).
- `scripts/check_design_links.sh`: install the `EXIT` trap before the second
  `mktemp` (`:76-80`); sort the `find` output so violation order is stable
  (`:112`).
- `tests/line_limits_helpers.py:97-100`: refuse `second_root` with
  `omit_root=True`, or make the combination do what its name says.
- KD-7 attribution: `tests/test_line_limits_exit_codes.py:3` and
  `plans/provenance-enforcement-and-routing/outline.md:349-350` attribute
  "exit 2 outranks exit 1" to KD-7, which does not state it. The plan is
  frozen; repoint the docstring at the script that implements the precedence.
- `bash_prolog` duplication: the root `justfile:79` redeclares the prolog and
  defines its own `run-project-checks` (`:205`), so the repo is safe; a
  third-party consumer that overrides the prolog is not. Either dedupe via
  `import` if `just` shares the variable, or state the
  `run-project-checks` obligation next to `portable.just:90`.

### skill-leftovers — one sequential pass, no design

- `apply-review.md` §Accepted, not fixed: `runbook/SKILL.md` §1 substeps
  (`:50-70`) as a list; the three §-citations of bold labels
  (`design/SKILL.md:152`, `item-review.md:103`,
  `deliverable-review/SKILL.md:178`); `write-design.md:7-8` §C.1's own recall
  triggers; the two `not recorded` rows in
  `deliverable-review/references/example-report.md:18-19`.
- `runbook/SKILL.md:71` second `Skill(edify:recall)` call — apply the
  requirements m3 fix.
- Corrector pass on `plugin/skills/formalize/SKILL.md` and
  `plugin/skills/ground/references/grounding-criteria.md`: no review is on
  record after their concurrent edits, and `5f860e07` edited them again.

## Riders on frame jobs

- **Defect 21** (frame R6): the two over-80-column lines
  (`outline-corrector.md:61`, `design-corrector.md:105`), already assigned;
  plus brief C-x's "script" half — whether the M7 mutate-and-run guards on
  `corrector.md:418-422` become a script that refuses a dirty target and
  verifies an empty diff after restore, decided at the same site as M7.
- **Defect 21's report-shape item** (frame R6): deliverable-review C3 —
  `deliverable-review/SKILL.md:191` disclaims queueing follow-up work against
  D-58 and D-60; the routing half joins the report-head-and-finding-shape
  item so the skill and its design node agree.

## Fixed here

- `CLAUDE.md` scraper line now lists `edify list`, `edify extract <prefix>`
  and `edify collect` as three commands, matching `README.md:22-23` and
  `grounding-criteria.md:116`.

## Dropped

- **inline m16 `argument-hint` half.** No edify skill declares the key;
  absence is the convention. The dispute stands.
- **D-52/D-53/D-54 placement.** `quality-gates.md`'s stated scope includes
  "skill step and rule placement"; they are where the hub says they belong.
- **`design/SKILL.md` `Edit` rationale.** `write-outline.md:131` prescribes
  Edit; the use is the rationale. Added in `5594a753`.
- **`red.md:193` says 39 lines for a 38-line file.** Reports are frozen
  records; the reviews already marked it "no consequence".
- **Brief A's `claude-plugin-dev` citations** and **`release.just` against
  `release.sh`**: both in another repo, read-only; D-87 needs neither.
- **Just-recipe test harness** and **"multiple rounds" evidence scope**:
  already dropped or already consumed, per `summary.md` §Deliberately dropped.

## Waiting on my human partner

- **2026-08-04 publication reversal.** `docs/changelog/2026-08-04-publication-postponement-reversed.md:9`
  and `cli-and-package.md:73-75` say no source records why. Only my human
  partner can supply the reason; default if none comes is to leave the gap
  stated as it is.
