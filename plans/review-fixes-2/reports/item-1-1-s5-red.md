# Item 1.1 slice 5 RED

Test: `tests/test_triage_feedback.py::test_odd_names_and_labels_do_not_derail_triage`,
parametrised `head-file`, `apostrophe-label`, `no-label-line`. File is 343
lines. Only `HEAD` is named in the `head-file` fixture; the others commit
`a.txt`. SUT untouched at the end (`git diff -- plugin/` empty).

## Per-test output (unmutated SUT)

- `[head-file]` PASS (behaviour already present: slice 3 and
  `changed-files.sh`'s `--`).
- `[apostrophe-label]` FAIL on its assertion: stdout reads
  `unrecognised classification: Moderate (my human` and stderr carries
  `xargs: unmatched single quote ...`;
  `assert "unrecognised classification: Moderate (my human partner's call)" in [...]`.
- `[no-label-line]` PASS (empty value reads `no-classification` today).

Suite after restore: 14 passed, 1 failed (the apostrophe red above).

## Mutation proof

Replacements in `plugin/bin/triage-feedback.sh`, each restored by the inverse.

- `[no-label-line]`: ` | xargs || true)` -> ` | xargs)`. Under `pipefail`
  grep's exit 1 aborts the script. Reds `[no-label-line]` on
  `assert '' == 'no-classification'`; `[apostrophe-label]` also red (xargs
  text on stderr); `[head-file]` stays green. Restored: grep for
  ` | xargs)` finds none.
- `[head-file]`, one mutation of two edits (both needed, since the
  `:(literal)` prefix alone already disambiguates):
  `list_pathspecs+=(":(literal)${list_rest%%$'\n'*}")` ->
  `list_pathspecs+=("${list_rest%%$'\n'*}")` and
  `"$baseline_commit" HEAD -- "${list_pathspecs[@]}"); then` ->
  `"$baseline_commit" HEAD "${list_pathspecs[@]}"); then`. Reds
  `[head-file]` on `assert '- Files changed: 1' in ['ERROR: git diff failed']`
  (`fatal: ambiguous argument 'HEAD': both revision and filename`).
  `[no-label-line]` stays green; `[apostrophe-label]` stays red (as today).
  Restored: `git diff --stat -- plugin/` empty; grep for `HEAD "${list`
  finds none; suite as above.

Not done: a mutation of `changed-files.sh`'s own `HEAD -- |` (line 116),
which is where the `HEAD` name is first handled. The auto-mode classifier
denied that edit as out of the dispatch's SUT; it was not retried. The
`HEAD` red above is through `triage-feedback.sh`'s own `--` and `:(literal)`.

## Fixtures tried and rejected

- One sequential test with three cases: the apostrophe red stops the test
  before the missing-line case runs, so that case could not be proved by
  mutation on its own. Parametrised instead.
- `HEAD` file in every parametrised fixture: the `HEAD` mutation then reds
  all three cases, hiding which case it proves. `HEAD` kept to `head-file`.
