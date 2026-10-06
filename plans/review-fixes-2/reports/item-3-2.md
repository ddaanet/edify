# Item 3.2 — design.md §8 L-2: the log's fields are the review gate's set

Target: `docs/design.md` §8 Limitations, L-2. Requirements: C1, M1. Depends
on: Item 1.1 (landed).

## Edit — §8, L-2, last sentence

Was: "`plans/reports/triage-feedback-log.md` collects per-execution evidence —
files changed, agent count, behavioral code, classification verdict — for
eventual calibration."

Now:

> `plans/reports/triage-feedback-log.md` collects per-execution evidence for
> eventual calibration: the files changed in the set the review gate
> reviewed, the reports committed beyond the one every item leaves,
> behavioural code in those files, and the classification verdict (D-90).
> The reports column keeps its `Reports` header; rows logged before
> `plans/review-fixes-2/` counted the reports on disk, the one every item
> leaves included.

"Agent count" is gone. Checked against `plugin/bin/triage-feedback.sh`: the log
header is `| Date | Job | Predicted | Files Changed | Reports | Behavioral Code |
Verdict |`, unchanged, and the fields are `files_changed` (list length),
`reports_count` (reports beyond the per-item and review reports) and
`behavioral_code` (the list's paths only).

## Deviation from the item text

The item says rows before this job "counted every report". The script at the
review's HEAD (`git show 79d0b687:plugin/bin/triage-feedback.sh`) counted the
files on disk in `plans/<job>/reports/` minus `design-review*`,
`outline-review*`, `recall-*`, `review.md`, `review-*.md` and
`final-review.md`, so "every report" is not literally true. The sentence says
what does hold for the change: the old rows counted on-disk reports, the
per-item one included.

## Verification

- `just format`; `docs/design.md` is 342 lines.
- `just precommit`: Precommit OK — version consistency, tests cached (inputs
  unchanged), line limits, design links (94 decisions indexed, defined once,
  conclusions match, 9 nodes present). The three `oversized-file` lines are
  files this item does not touch.
