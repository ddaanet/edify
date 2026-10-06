# /build leg 3 — review-fixes-2

## Run

- Job: `plans/review-fixes-2`, work = `outline.md` (no runbook, no phases).
  Resumed inside `finishing.md` §1, the review gate, after leg 2's stop on
  `review-code.md` Major 1 (U-DESIGN). All 25 outline items landed in legs
  1–2. The five review groups' reports and fixes were left uncommitted, and
  nothing here discarded, stashed or re-ran them.
- §3 pre-work ran: no `brief.md`; recall read the plan's recall artifact and
  loaded `craft:design-doc-writing` for the D-90 edit.
- Dispatches were spawned unnamed, per my human partner's override. Each
  dispatch name was used only as its report filename, and resumes went to
  agent ids.

## Landed in this leg (all uncommitted, inside the review gate)

My human partner ruled on leg 2's gate. Decision 1 was fix (b): fix the
evidence so a re-run measures the same set. Decision 3 added `back\slash.txt`
to Item 1.3's fixture. Both were executed as one TDD slice that, by
decision 2, rides the review-gate commit:

- `gate-fix-red` (test-driver, sonnet) wrote the following tests:
  - A, `test_pipeline_record_under_plans_reports_is_dropped`, in
    `test_changed_files.py`;
  - B, `test_reports_exclude_the_tdd_audit_report`, in
    `test_triage_feedback.py`;
  - C, `test_rerun_after_the_closing_commit_appends_no_row`, in
    `test_triage_feedback_log.py`, the end-to-end scenario of Major 1;
  - D, an amendment to Item 1.3's
    `test_paths_with_space_and_non_ascii_bytes_are_listed_whole`, adding
    `back\slash.txt`.

  A, B and C red on their assertions. D is proven by mutation under the two
  new mutants and the outline's original two.
- `gate-fix-test-review` (corrector, opus) reproduced D's red with its own
  mutation, an output-side backslash strip. It made two fixes: C now pins
  the first run's evidence, and the module docstring cites D-numbers.
- `gate-fix-green` (test-driver, sonnet) made two changes, with no commit by
  override:
  - `changed-files.sh` drops `plans/reports/*` in the same `case` as
    `plans/<job>/`, not in `exempt-paths.sh`, so D-91 is unchanged;
  - `triage-feedback.sh` excludes `tdd-audit.md` from Reports.

  The full suite gave 410/411 with 1 xfail, and `just precommit` was green.
- Prose was edited in session. D-90 has a new heading, "… minus the exempt
  paths and the pipeline's record …", body text, and two new Rejected
  entries: a landed check on triage keyed on the log, and triage dropping
  its own log path. Further edits:
  - `docs/decisions.md`: the D-90 line and the *Rejected:* line;
  - the list descriptions in `finishing.md` §1, `phase-boundary.md`,
    `review-requirement.md` and `plugin/README.md`, the last also covering
    the count's exclusions;
  - this job's 2026-10-06 changelog entry;
  - `outline.md`: KD-1's Reports bullet, and Item 1.3's mutant list and
    pinned fixture.
- `gate-fix-code-review` (corrector, opus) made two minor fixes: it reflowed
  the triage comment and made the changelog sentence conditional. It found
  **one UNFIXABLE (U-DESIGN)**, below. `just precommit` was green after its
  fixes.

## Deviations

- The fix's four reports are named `gate-fix-*`, not `item-*`, since the fix
  is not an outline item, and not `review-*`, which would collide with the
  four fixed review-gate slugs. Triage counts them as Reports, as it counts
  slice reports.
- `gate-fix-green`'s first precommit failed on ruff D205, a two-line
  docstring summary in test A. I fixed the docstring in session, as a
  form-only edit, and resumed the agent, whose re-run passed.
- `just lint` and `just format` reflowed the markdown edits in place. This
  is the recipe's own behaviour.
- `phase-boundary.md` and `review-requirement.md` were edited although
  decision 1 named only `finishing.md` and the README. Both also describe
  the list, and a stale copy would contradict D-90.

## Open items (not gates)

1. `gate-fix-test-review` recommendation: D does not catch an output-side
   `printf '%b'` or `echo -e`, because `\s` is no escape in bash. A name
   such as `back\tslash.txt` would catch them. This was left unchanged,
   since the outline pins the name.
2. `gate-fix-code-review` note: a final review's fixes land in the closing
   commit after triage, so a re-invocation measures them and may log a
   second row. That row reflects real new evidence, which KD-2 permits.

## Where the run stands — STOP

`finishing.md` §1 stops on the validated UNFIXABLE, before the review-gate
commit. The UNFIXABLE has a code, a three-gate investigation, no scope-OUT
overlap, and its claims verified against `plugin/skills/design/references/triage.md:52,66`
and `docs/references/execution-routing.md:72`. These files are uncommitted:

- every review-gate fix from leg 2;
- this fix, across the scripts, tests, prose and outline;
- `review-{code,skill,agent,design,outline}.md`;
- `gate-fix-{red,test-review,green,code-review}.md`.

This leg report is the only file committed.

**Resume:** apply the ruling below. Under (i) or (ii), do a RED/GREEN
amendment of test A and the script, then remove the stated-bound sentence
from D-90 (`build-run-state.md`, "It is also where an Investigation's
deliverable goes …"), then a corrector pass over that delta. Then make the
single `<type>: review-fixes-2 Review gate` commit by path: the gate's
fixes, the five review reports, this fix and its four reports. Run
`verify-step.sh`, then §2 triage and §3. Do not run `/deliverable-review`.

## Gate question

1. **`plans/reports/` is also where an Investigation's deliverable goes**
   (`gate-fix-code-review.md` Major 1, U-DESIGN). `/design`'s triage table
   names `plans/reports/` as the Investigation destination, and D-82 routes
   Investigation to `/build`. Dropping all of `plans/reports/` therefore
   takes such a deliverable off the list, with three effects: the review
   gate sees an empty list and writes `review-skip.md`, §3 skips the final
   review, and triage counts 0 files. The options:
   - (i) narrow the drop to the triage log by name,
     `plans/reports/triage-feedback-log.md`, which is the only
     `plans/reports/` path a closing commit lands. Test A then lists
     `explore-x.md` and `sub/x.md`, D-90's prose narrows, and the
     stated-bound sentence goes.
   - (ii) keep the drop and move the Investigation destination to
     `plans/<job>/`. That is also dropped, so the deliverable stays
     unreviewed.
   - (iii) keep the drop as decided and accept the bound. D-90 already
     states it.

   **Default: (i)**. It closes the measured defect, the re-run's +1, with
   the narrowest change, and keeps Investigation deliverables under review.
