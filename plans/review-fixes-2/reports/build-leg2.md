# /build leg 2 — review-fixes-2

## Run

- Job: `plans/review-fixes-2`, work = `outline.md` (no runbook, no phases).
- Run base (`changed-files.sh review-fixes-2`): `888eda7a312e962a28ba59c2695eecd5f34c6e14`.
- Mode: resumed. Leg 1 was interrupted mid-run (not a failure of the work);
  `build-leg1.md` records only its earlier entry-gate stop, since resolved by
  `888eda7a`. Resume per `escalation.md` §Resuming: inventory from report
  history; the gate's dirt (Item 1.3 slice 1's test and its RED and
  test-review reports) was relevant to the first remaining slice and went into
  its GREEN.
- Dispatches were spawned unnamed, per my human partner's override; each
  dispatch name was used as its report filename only, resumes went to agent ids.

## Items completed (commit subjects)

Leg 1 (interrupted):

- Item 1.1/1–1.1/5 — `triage counts the review gate's list`, `reports exclude
  the per-item report`, `behavioural code reads the list's paths only`, `an
  unrecognised label is no classification`, `odd names and labels do not
  derail triage`, each with its `code-review fixes` commit.
- Item 1.2/1 — `a re-run appends no duplicate row`, with `code-review fixes`.

Leg 2:

- Item 1.3/1 — `paths with a space or non-ASCII byte are listed whole`;
  `code-review fixes`. RED by mutation (both named mutants).
- Item 1.4/1 — `an unloadable exempt-paths.sh is an error, not NO-BASE`;
  `code-review fixes`. Item 1.4/2 — `… not DIRTY`; `code-review fixes`.
  RED by mutation.
- Item 1.5 — `script hygiene`. Item 1.6 — `test hygiene`.
- Item 2.1 — `build hub names Item 1.1, verifies refactor and list-revision
  commits, skips a landed gate` (SKILL.md 199 lines).
- Item 2.2 — `finishing skips landed stages, triage takes no base, an empty
  list is a skip`. Item 2.3 — `escalation names the mask dependency, slice
  remediation agents and resume verdicts`. Item 2.4 — `list revision in the
  hosting file, refactor and list revision verified`. Item 2.5 — `tdd-auditor
  reads list revisions from the hosting file`. Item 2.6 — `dispatch-composition
  resumes by agent id, the skill row covers the prose a skill loads`. Item 2.7 —
  `review-requirement skill row covers the prose a skill loads`. Item 2.8 —
  `delegation resumes by name, or by agent id when spawned unnamed`. Item 2.9 —
  `a committed failed fix escalates, verify re-runs once`. Item 2.10 — `the
  review example asks for UNFIXABLE with its code and three-gate summary`.
  Item 2.11 — `README names sandbox-lies, the verified slice commits, triage's
  list`.
- Item 3.1 — `D-90 records triage measuring the review gate's list`. Item 3.2 —
  `L-2 names the triage log's fields as the review gate's set`. Item 3.3 —
  `changelog records triage measuring the review gate's set`. Item 3.4 —
  `build-fixes outline names the exit codes and the test modules as landed`.

Post-item verification (`verify-step.sh`) came back `CLEAN:` after every
committed step. List revision: none for every slice (no slice revealed a change
to the remaining lists; no hosting-file commit).

## Finishing — where the run stands

`finishing.md` (the job's own revised text) §1 review gate: all five groups
dispatched and every report Read (structural proof).

| Dispatch | Report | Result |
|---|---|---|
| `review-code` (corrector) | `review-code.md` | 1 major **UNFIXABLE (U-DESIGN)**, 4 minor fixed, 1 routed |
| `review-skill` (skill-reviewer, report-only) | `review-skill.md` | 3 major + 6 minor fixed in session; 2 deferred; second pass: 1 fixed, 1 routed |
| `review-agent` (corrector) | `review-agent.md` | 2 major fixed |
| `review-design` (corrector) | `review-design.md` | 2 major + 5 minor fixed |
| `review-outline` (outline-corrector, planning artifact) | `review-outline.md` | 2 minor fixed |

The UNFIXABLE validates (code, three-gate summary, no Scope-OUT overlap), so
§1 STOPs before its report commit. **The review gate's fixes and its five
reports are uncommitted in the tree** (`just precommit` green over them); this
leg report is the only file committed at the stop. §2 triage and §3 have not
run.

## Deviations

- The loaded skill copy (`dist/plugin`, gitignored) predates this job's edits;
  finishing followed the revised `plugin/skills/build/references/finishing.md`,
  since the old text passes a `<base>` the new `triage-feedback.sh` rejects.
- Items 2.6–2.8, 2.9–2.11 and 3.1–3.4 were batched into three dispatches, one
  commit and one report per item.
- `plans/build-fixes/outline.md` (a planning artifact in the changed list) was
  routed to `edify:outline-corrector`, scoped to Item 3.4's revised spots.
- Item 3.3's changelog entry is dated 2026-10-06 (the day it was written).
- Item 1.4/1's code review had a pytest call denied by the auto-mode
  classifier while the script was mutated; it restored the script and did not
  retry. The slice's red evidence stands on RED and test review.

## Open items (not gates; for my human partner)

1. Item 1.3's fixture does not red two further NUL-discipline mutants
   (`git -c core.quotepath=off` with a newline read; `read` without `-r`); a
   `back\slash.txt` path closes both. Left unchanged: the outline pins the
   fixture. (Test review minor 2; code review concurs it should be added.)
2. `review-skill` Minors 7 and 8, deferred: a fresh remediation dispatch has no
   name (suggested `<step name>-fix`); the resume inventory does not track an
   owed list revision. Both predate this job.
3. `review-design`: the landed checks for the finishing stages are in no design
   node; one sentence in D-88 or D-89 once Q1 is settled.
4. `plugin/README.md` names neither `plugin-dev` nor `craft` as optional.
5. The `sandbox-lies` `phantom-untracked` detector fires only on at least two
   masked names (Item 2.3's executor), so a single masked name reads as dirt
   even with the plugin installed.

## Where to resume

Resume at `finishing.md` §1 once Q1–Q2 are answered: apply the chosen fix,
then the review gate's report commit (all five reports and every fix,
`<type>: review-fixes-2 Review gate`), `verify-step.sh`, then §2 triage and §3.
Do not run `/deliverable-review` — a separate agent does.

## Gate questions

1. **Re-invoking a finished job logs a second triage row** (`review-code.md`
   Major 1, U-DESIGN). `finishing.md` §2 has no landed check, and by then the
   closing commit has put `plans/reports/triage-feedback-log.md` into D-90's
   list (Files changed +1) and `tdd-audit.md` into the report count
   (Reports +1); the evidence differs, KD-2's dedupe passes, and the verdict
   can flip (probed). Options: (a) a landed check on §2 keyed on the triage
   log after `<L>` — but the log is shared across jobs, so another job's
   Finish on the branch would wrongly skip §2; (b) fix the evidence — drop
   `plans/reports/` from D-90's list as pipeline record (as `plans/<job>/` is)
   and add `tdd-audit.md` to the review-report exclusions, so a re-run measures
   the same set and KD-2 dedupes as designed; (c) triage drops its own log path
   — a second copy of D-90's filters, which KD-1 rejects. **Default: (b)**,
   which keeps D-89's key-on-own-report principle and touches
   `changed-files.sh`, `triage-feedback.sh`, D-90 and `finishing.md`'s/README's
   descriptions of the list.
2. **How the fix lands.** Default: inside the review gate — a test-driver RED
   and GREEN pair (uncommitted, alongside the gate's fixes) with a corrector
   review, then the single review-gate commit. Alternative: commit the gate as
   it stands and land the fix as a new Item 1.7 with slices; the gate's landed
   check then reads unlanded and the whole gate re-runs at finishing.
