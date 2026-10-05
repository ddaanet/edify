# Item 1.1/1 GREEN — review-fixes-2

Mode GREEN. Edited only `plugin/bin/triage-feedback.sh`; no test file touched.

## Growth order (one test at a time)

1. `test_files_changed_is_the_review_gates_list`: `<job>`-only usage, run
   `changed-files.sh` found at `../skills/build/scripts/` from the script's own
   path, read `BASE:` and the list, count list lines.
2. `test_files_changed_counts_committed_changes_only`,
   `test_uncommitted_definition_is_not_behavioral`,
   `test_forced_color_does_not_hide_definitions`: green from step 1 (base from
   `changed-files.sh` feeds the unchanged `<base> HEAD` diff).
3. `test_failing_diff_is_an_error_not_no`: the diff capture became
   `if ! committed_diff=$(git diff ...)` printing `ERROR: git diff failed`,
   exit 2; git's own stderr is left visible.

Also implemented per the interface, untested in this slice: `changed-files.sh`
exit 1/2 prints its output, then `ERROR: changed-files.sh exited <n>`, exit 2,
no log row (`|| status=$?` keeps `set -e` from exiting silently).

## Results

- `tests/test_triage_feedback.py`: 5/5 passed.
- Full suite: 383/384 passed, 1 xfail.
- `just lint`: Lint OK.

## Gate verdict

- `just precommit` recap: version consistency, tests cached, line limits,
  design links (94 decisions indexed, 9 nodes present) — Precommit OK.
- `tmp/.test-sentinel`: `1218342445 619471`

## Precommit warnings (not acted on)

- `oversized-file: plugin/agents/corrector.md: 682 lines > 400`
- `oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400`
- `oversized-file: plugin/agents/design-corrector.md: 460 lines > 400`

## Notes

- Shell audit: no new bashisms beyond bash 3.2 (`${var%%$'\n'*}`, `[[ ]]`,
  `$(...) || status=$?`); `wc -l | tr -d ' '` kept for BSD padding.
- Left for later slices: reports `find` count, the stale `KD-3` comment on the
  reports exclusions, classification parse (`xargs || true`), here-string.
