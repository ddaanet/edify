# Item 3.3 — name the fresh remediation dispatch `<step name>-fix`

Requirement: C-1 (`review-skill` Minor 7, ruled into scope). Type: general.

## What changed

- `plugin/skills/build/references/dispatch-composition.md` §Naming and
  resumption: a new top-level entry after the slice-dispatch entry and before
  `phase-P-corrector`, shaped like Item 3.2's `review-plan-…` entry (name,
  definition, examples, one reason clause). It names `<step name>-fix` for the
  fresh dispatch of `escalation.md` §Post-item remediation step 2, defines
  `<step name>` as the dispatch whose dirt it finishes, gives `item-1-2-fix`
  and `item-1-1-s2-green-fix`, and states the reason: reusing the step's name
  would overwrite the report its commit already carries. It sits after the
  slice entry because `<step name>` is defined over the entries above it.
- `plugin/skills/build/references/escalation.md` §Post-item remediation step
  2: the fresh-dispatch sentence now names the dispatch `<step name>-fix`
  after the step whose dirt it finishes, with the same two examples. Every
  other word of step 2 is kept. Step 3 is unchanged. §Resuming and its
  `git log` commands are untouched.

The report-counting reasoning (contract bullet 3) is not written into either
file. It is evidence that the name is safe, not an act the reader performs
(`craft:directive-writing`, the five cuts).

## Contract

- **Step 2's fresh dispatch is named `<step name>-fix`.** Met in
  `escalation.md` step 2, with `item-1-2-fix` after a general item and
  `item-1-1-s2-green-fix` after a slice's GREEN.
- **§Naming lists the name, with the reason in one clause.** Met: "Reusing
  the step's name would overwrite the report its commit already carries."
- **The report path follows from §Prompt contents item 5**, which assigns
  `plans/<job>/reports/<dispatch name>.md` for every dispatch, so the fix
  dispatch's report is `item-N-M-fix.md` (or `item-N-M-s<k>-green-fix.md`).
  Verified against the code:
  - Base: `plugin/skills/build/scripts/changed-files.sh` takes the first line
    of `git log --no-show-signature --no-renames --diff-filter=A --reverse
    --format=%H -- ":(glob)plans/$job/reports/item-*"` and uses its parent.
    `item-N-M-fix.md` matches `item-*`, but step 2 fires only after a
    committed step (§Post-item remediation opens "after a step whose work is
    committed"), whose commit already added that step's own `item-*` report.
    The fix commit is therefore never the earliest `item-*` addition, and the
    base does not move. Phase-boundary, review-gate and closing commits go to
    step 3 with no fix dispatch, so no fix report precedes the first item.
  - Resume test: `plugin/skills/build/SKILL.md` §1 (line 46) tests for any
    `plans/<job>/reports/item-*.md` on disk. The step's own report is already
    there before the fix report exists, so the answer does not change.
  - Inventory: `escalation.md` §Resuming step 1 checks exact report paths
    (`item-N-M.md`, `-green.md`, `-code-review.md`, `-refactor.md`); a
    `-fix.md` path is none of them.
  - Triage: `plugin/bin/triage-feedback.sh` skips names matching
    `item_report_re='^item-[0-9]+-[0-9]+\.md$'` and the review-gate `case`
    (`review.md | review-*.md | final-review.md | tdd-audit.md`).
    `item-1-2-fix.md` matches neither, so it prints an `x` and counts as a
    report beyond the item's own. `item-1-1-s2-green-fix.md` likewise counts,
    as slice reports already do.
  - Also checked: `finishing.md` §1's `<L>` is the last commit touching
    `item-*`. A fix commit after the last item moves `<L>` later, but
    remediation finishes before the review gate runs, so `<L>` still precedes
    any `review-*.md` commit and the landed check is unaffected.
- **Step 3 escalates when that dispatch fails.** Already true as written:
  "That fails → escalate to the user with the listing and the dispatch's
  findings." Step 3 needed no edit, and no second `-fix` name exists.

## Open bound for the caller

Step 2 names four slice steps after which it can fire: GREEN, code-review,
refactor and list-revision commits. The first three are dispatches with
§Naming names (`-green`, `-code-review`, `-refactor`), so `<step name>-fix`
reaches them. The list-revision commit is the orchestrator's own commit
(`tdd-slice.md` step 3), with no dispatch and no report, so `<step name>` as
the contract defines it ("the dispatch whose dirt it finishes") names nothing
there. No slug was invented for it; the contract does not rule one.

## Precommit

The first `just precommit` failed at `rumdl`: the edited step 2 paragraph in
`escalation.md` was not reflowed. `just format` reflowed it, and the re-run
passed:

- version consistency: `Version consistent: 0.3.0`
- tests: `Tests cached (inputs unchanged)`
- rumdl: no findings
- line limits: only the three allowlisted corrector-family files reported
  (`corrector.md` 682, `outline-corrector.md` 450, `design-corrector.md`
  460), as before this item
- design links: 94 decisions indexed, defined once, conclusions match, 9
  nodes present
- `Precommit OK`

Because the tests were cached,
`.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py`
was run directly: 10 passed. `escalation.md` §Resuming is byte-identical.
