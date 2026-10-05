# Item 1.1/2 GREEN — reports exclude the per-item report

## Tests

Order made to pass (one test in the batch):

1. `tests/test_triage_feedback.py::test_reports_exclude_the_per_item_report`
   — red before, green after. Implementation: replaced the on-disk `find`
   count in `plugin/bin/triage-feedback.sh` with KD-1's rule: `git diff
   --name-only --no-renames --diff-filter=A <base> HEAD -- ":(glob)plans/<job>/reports/*"`,
   captured first (failure -> `ERROR: git diff failed` on stdout, exit 2),
   then a loop dropping `^item-[0-9]+-[0-9]+\.md$`, `review.md`,
   `review-*.md`, `final-review.md`. The stale `KD-3` comment is replaced by
   a D-90 citation; the newline residual bound is stated in a comment.
   `review_artifact` detection is unchanged.

Module: 7 passed. Full suite: 385/386 passed, 1 xfail (pre-existing).
`shellcheck plugin/bin/triage-feedback.sh`: clean. `just lint`: OK.

## Gate

`just precommit`: `Precommit OK` (version consistent, tests cached, line
limits, design links: 94 decisions indexed, defined once, conclusions
match, 9 nodes present).
`tmp/.test-sentinel`: `474898992 624778`

## Precommit warnings (not acted on)

- `oversized-file: plugin/agents/corrector.md: 682 lines > 400`
- `oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400`
- `oversized-file: plugin/agents/design-corrector.md: 460 lines > 400`

All three are files this slice does not touch.

## Portability

Uses `[[ =~ ]]` with the regex in a variable, here-string, `case`, and
`$((...))`; all bash 3.2 safe. No GNU-only flags. Non-ASCII names rely on
`core.quotepath=off`.
