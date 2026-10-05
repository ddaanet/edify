# Review: Item 1.1 slice 5 test review

**Scope**: uncommitted change to `tests/test_triage_feedback.py`
(`test_odd_names_and_labels_do_not_derail_triage`) and
`reports/item-1-1-s5-red.md`; SUT `plugin/bin/triage-feedback.sh` touched
only for mutation reproductions, each restored.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The three named cases are present and parametrised. `[apostrophe-label]`
reds on its assertion; `[head-file]` and `[no-label-line]` pass and each
reds under an independent mutation. One surviving GREEN (a parse that trims
the leading side only) was killed by putting trailing whitespace on the
apostrophe line. Docstring drift fixed; one over-long line wrapped.

**Overall Assessment**: Ready

## Mechanical check

Unmutated SUT, `tests/test_triage_feedback.py` +
`tests/test_triage_feedback_behavioral.py`: 14 passed, 1 failed.

- `[head-file]` PASS.
- `[apostrophe-label]` FAIL on
  `assert "unrecognised classification: Moderate (my human partner's call)" in [...]`;
  stdout carries `unrecognised classification: Moderate (my human`, stderr
  `xargs: unmatched single quote; ...`. No ERROR.
- `[no-label-line]` PASS.

## Mutation reproductions (my own, distinct from the RED report's)

Each applied with Edit, restored by the inverse Edit.

1. **`[head-file]`** — dropped `--` from the *Reports* diff
   (`"$baseline_commit" HEAD -- ":(glob)$reports_dir/*"` ->
   `"$baseline_commit" HEAD ":(glob)$reports_dir/*"`), a different git call
   from the RED report's behavioural-code diff. `[head-file]` reds on
   `assert '- Files changed: 1' in ['ERROR: git diff failed']`
   (`fatal: ambiguous argument 'HEAD': both revision and filename`).
   `[no-label-line]` green; `[apostrophe-label]` red as before. Restored:
   grep for `HEAD ":(glob)` 0 hits, `git diff -- plugin/` empty.
2. **`[no-label-line]`** — grep's exit 1 made an error:
   `| xargs || true)` -> `| xargs || exit 2)`. `[no-label-line]` reds on
   `assert '' == 'no-classification'` (script exits 2 before output).
   `[head-file]` green. Restored: grep for `exit 2)` 0 hits, SUT diff empty.

## Wrong-reason hunting

- `[apostrophe-label]` asserts the whole line by list membership
  (`f"unrecognised classification: {label}" in lines`), not a prefix, and
  `"xargs" not in result.stderr`. Stripping the apostrophe reds (line
  differs). `xargs -0` reds: probed, the existing fixture leaves a leading
  space after the sed (`** Moderate` minus `*`), which `xargs -0` keeps.
- `[no-label-line]` asserts verdict, absence of the unrecognised line, and
  `not log.exists()`; the bare negative on the log is paired by slice 4's
  positive over the same path (`rows[-1]` carries `| j | Moderate |`).
  A parse treating grep exit 1 as an error reds it (mutation 2).
- `[head-file]` asserts `- Files changed: 1`; the only non-report path the
  run commits is `HEAD`, so dropping it gives 0, and an ambiguity failure
  gives `ERROR:` (mutation 1).

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Leading-only trim survived `[apostrophe-label]`**
   - Location: `tests/test_triage_feedback.py:321`
   - Problem: m6 requires the value trimmed. Probe mutant
     `| xargs || true)` -> `| sed -E 's/^[[:space:]]+//' || true)` passed all
     three cases: the fixture had no trailing whitespace to keep.
   - Fix: the apostrophe line is now
     `f"- **Classification:** {label} \t\n"`. Under the same probe mutant
     the case reds, the line printing `... partner's call) \t`. A correct
     both-sides trim (`sed -E 's/^[[:space:]]+//;s/[[:space:]]+$//'`) was
     probed too and passes the whole module (15/15), so the case is
     satisfiable. Both probes restored; SUT diff empty.
   - **Status**: FIXED

### Minor Issues

1. **Docstring claimed "nothing on stderr"; the assertion is no `xargs`**
   - Location: `tests/test_triage_feedback.py:307-312`
   - Note: the slice specifies no `xargs` text; the docstring now says so.
     It also described the current `xargs`/`|| true` code in present tense,
     which goes stale at GREEN; reworded to the failure mode.
   - **Status**: FIXED
2. **Wrong decision citation**
   - Location: same docstring, `(D-90)` on the literal-parse sentence
   - Note: D-90 is the changed-files list contract, not the classification
     parse; m6 has no D-number. Citation removed.
   - **Status**: FIXED
3. **`head-file` docstring misstated git's behaviour**
   - Location: `tests/test_triage_feedback.py:303-305`
   - Note: said a bare `HEAD` argument "would read as the revision"; git
     refuses it as ambiguous (mutation 1 output). Reworded.
   - **Status**: FIXED
4. **Over-long line (E501, 89 > 88)**
   - Location: the `not any(line.startswith(...))` assertion in
     `[no-label-line]`
   - Note: wrapped as slice 4's identical assertion is, with `output` as
     its message.
   - **Status**: FIXED

## Residual (for the code review, not fixable in this slice's cases)

- **`|| true` and form-only `xargs` are not pinned behaviourally.** Both probe
  GREENs above kept `|| true` and passed `[no-label-line]`: the named cases
  only reach grep's exit 1, and m6's "exit ≥ 2 is an error" arm needs a grep
  failure, which no named case provokes (fault injection via
  `_run_triage`'s `path_prepend` shim would be a new case, outside the
  slice). Likewise a GREEN keeping `xargs` with the apostrophe pre-escaped
  passes this label. As with m5, the code review checks the form: no
  `xargs`, no `|| true`, grep exit ≥ 2 -> error.
- `changed-files.sh`'s own `HEAD --` (RED report's "Not done") stays
  unproven by mutation; out of this dispatch's SUT.

## Fixes Applied

- `tests/test_triage_feedback.py` apostrophe fixture — trailing ` \t` on the
  classification line (pins the trailing trim).
- `tests/test_triage_feedback.py` docstring — `head-file` wording, stderr
  claim, stale present-tense `xargs` description, `(D-90)` removed.
- `tests/test_triage_feedback.py` `[no-label-line]` — wrapped the E501 line,
  added `output` message.

## Post-fix state

- Module + behavioural module: 14 passed, 1 failed —
  `[apostrophe-label]` on
  `assert "unrecognised classification: Moderate (my human partner's call)" in [...]`.
- `ruff check` and `ruff format --check` clean on the test file.
- `tests/test_triage_feedback.py`: 346 lines (cap 400).
- `git diff -- plugin/` empty.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m4 (`HEAD` file) | Satisfied (test) | `[head-file]`, mutation 1 |
| m6 (literal parse, trimmed) | Satisfied (test), form residual above | `[apostrophe-label]` red; trailing-trim probe |
| m6 (no line is a result) | Satisfied (test) | `[no-label-line]`, mutation 2 |
| N-1 (no row for unrecognised) | Satisfied (test) | `not log.exists()` in `[apostrophe-label]` |
