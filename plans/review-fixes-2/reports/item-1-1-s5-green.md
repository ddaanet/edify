# Item 1.1 slice 5 GREEN

## Order made to pass

1. `test_odd_names_and_labels_do_not_derail_triage[apostrophe-label]` (the
   only red). First attempt (`sed 's/.*:[[:space:]]*//;s/\*//g'`) left a
   leading space, because `xargs` had been trimming it; the full suite
   showed `test_reports_exclude_the_per_item_report` and
   `test_unrecognised_label_is_no_classification` red from it. Second
   attempt strips `*` first, then the prefix, then trailing space: green.
2. `[head-file]`, `[no-label-line]`: stayed green throughout.

## Change

`plugin/bin/triage-feedback.sh`: the classification parse has no `xargs`,
no `head` and no `|| true`. grep's status is captured (`|| grep_status=$?`):
0 takes the first line by parameter expansion and trims with
`sed -E 's/\*//g;s/.*:[[:space:]]*//;s/[[:space:]]+$//'`; 1 is no
classification; above 1 prints `ERROR: grep failed` and exits 2. A failing
`sed` prints `ERROR: sed failed` and exits 2. Portable to bash 3.2 and BSD
`sed -E`.

## Results

- Full suite: 393/394 passed, 1 xfail (pre-existing).
- `just lint`: Lint OK.
- `just precommit`: `Precommit OK`; run reported "Tests cached (inputs
  unchanged)". `tmp/.test-sentinel`: `1916317145 639075`.

## Precommit warnings

- oversized-file: plugin/agents/corrector.md: 682 lines > 400
- oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
- oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
