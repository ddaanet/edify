# Item 1.1 slice 3 GREEN: behavioural code reads the list's paths only

## Tests

Order made to pass (one failing test in the batch):

1. `test_behavioral_code_reads_the_lists_paths_only` — red before; green after
   the behavioural-code computation was limited to the list's paths.

Implementation growth, in one step: the diff runs only when the changed-files
list is non-empty, with `--no-renames` and each list path as a `:(literal)`
pathspec after `--`; an empty list reads `no` and runs no diff. The here-string
is gone (list split by parameter expansion; grep fed by a pipe). grep exit 1
is "no", any other non-zero exits 2 with `ERROR: grep failed`, following
`verify-step.sh`. A comment states the newline-path residual bound.

Results: `tests/test_triage_feedback.py` 10/10; full suite 388/389 passed,
1 xfail (pre-existing); `just lint` OK; shellcheck clean.

## Gate

- `just precommit` recap: `Precommit OK` (version consistency, tests cached,
  line limits, design links).
- `tmp/.test-sentinel`: `4036406035 631118`

## Precommit warnings

- `oversized-file: plugin/agents/corrector.md: 682 lines > 400`
- `oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400`
- `oversized-file: plugin/agents/design-corrector.md: 460 lines > 400`

None touch this slice.
