# Item 1.1/2 RED — review-fixes-2

Mode RED. SUT `plugin/bin/triage-feedback.sh` untouched. Files:
`tests/test_triage_feedback.py` (184 -> 238 lines), `tests/triage_feedback_helpers.py`
(106 -> 112; adds `_verdict`, the line after `## Verdict`). No commit.

## Per-test output

Module run: 6 passed, 1 failed (the new test).

- `test_reports_exclude_the_per_item_report`: fails on its first assertion,
  `assert '- Reports: 0' in [...]`; stdout read `- Files changed: 1`,
  `- Reports: 3`, `- Behavioral code: no`, verdict `underclassified`. The 3 are
  today's on-disk `find` count: `runbook-review.md`, `explore-x.md` (planning
  reports, outside the `<base> HEAD` range) and `item-1-1.md` (the per-item
  report). `review-code.md` is already excluded by name. Not an ERROR.

Assertions after the first were not reached against today's script. By reading
the script and the output above: `- Behavioral code: no` already holds (no
definition committed), as does `- Files changed: 1`; the `match` verdict does
not (reads `underclassified` because of the count). The later `Complex` and
`item-1-1-s1-code-review.md` assertions are unexercised until GREEN. No
mutation proof is needed: the test reds on its own assertion.

## classification.md: committed

Committed with the planning reports, before the base, as a plan leaves it. The
Complex and Simple relabels are on-disk edits only. Triage reads the file from
disk, so an uncommitted edit changes the label without touching the
`<base> HEAD` range, and each of the three runs reads its own label.

## Fixtures tried and rejected

- Committing each relabel: rejected, adds commits after the base that no
  assertion needs; the path is outside `plans/j/reports/`, so it would not
  move Reports, but it would add to Files changed and obscure the `<= 2` bound
  for `overclassified`.
- `classification.md` only on disk, never committed: rejected, an uncommitted
  planning file is not how a run leaves it, and a later `git status`-based
  helper would see dirt.
- The red a fixture reaching only the `Reports: 0` assertion shares with the
  item's own mutation (counting on-disk reports): that is the intended red;
  the old exclusion-by-name list also fails here because `runbook-review.md`
  and `explore-x.md` were chosen as names it never covered.
