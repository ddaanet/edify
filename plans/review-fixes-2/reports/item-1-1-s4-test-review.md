# Review: Item 1.1 slice 4 test review — unrecognised label

**Scope**: uncommitted `tests/test_triage_feedback.py` change
(`test_unrecognised_label_is_no_classification`) and
`reports/item-1-1-s4-red.md`; SUT `plugin/bin/triage-feedback.sh` read-only.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The RED test reds on its verdict assertion, as reported. The assertions after
it were sound in shape but left three mutants alive: a last-match or
any-recognised parse, a doubled unrecognised line, and an implementation that
recognises only `Simple` and `Complex`. All three are now caught. The test
still reds on the verdict assertion against the unchanged SUT.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The single-line fixture leaves "first value" unpinned**
   - Location: `tests/test_triage_feedback.py` fixture `classification.md`
   - Problem: with one `Classification:` line, a parse taking the last match,
     or any recognised match, gives the same answer as one taking the first.
     The interface specifies the *first* value.
   - Fix: a second line, an exact `- **Classification:** Simple`, follows the
     label. A last-match or any-recognised parse reads `Simple` and gives
     `underclassified`.
   - **Status**: FIXED

2. **`Moderate` and `Defect` are never exercised as recognised classes**
   - Location: whole suite (`grep` finds neither label in
     `test_triage_feedback.py` or `test_triage_feedback_behavioral.py`)
   - Problem: an exact-match allowlist that left out `Moderate` or `Defect`
     would turn every such run into `no-classification` with an unrecognised
     line and no row, and no test would red.
   - Fix: a positive leg on the same fixture, relabelled on disk to
     `Moderate` and then `Defect`, as `test_reports_exclude_the_per_item_report`
     relabels. Each run exits 0, reaches a verdict other than
     `no-classification`, prints no `unrecognised classification:` line, and
     appends exactly one row whose Predicted column is the label. The
     negative assertions come first, so they report on their own; the
     positive leg pairs them over a fixture differing only in the label.
   - **Status**: FIXED

### Minor Issues

1. **The unrecognised line was checked for presence, not count**
   - Location: `tests/test_triage_feedback.py`, the stdout-line assertion
   - Note: `in lines` allows the line to be printed twice. It is now
     `lines.count(...) == 1`. It was already an exact-line match, so a
     mangled or truncated label, a prefixed line or a line on stderr all
     red it.
   - **Status**: FIXED

## Points checked, no change needed

- **No row, not just no file.** `assert not log.exists()` is stronger than
  "no row": if the file does not exist, no row was written. It would also red
  an implementation that writes only the header on `no-classification`. That
  red goes beyond the contract's wording, but in the SUT the header and the
  row come from one block, so no plausible implementation produces it. The
  positive leg's row count (`splitlines()[2:]`) checks the append itself.
- **Prefix and first-word parses.** The `def` in `a.py` makes a `Simple`
  reading give `underclassified`. The verdict assertion catches both.

## Fixes Applied

- `tests/test_triage_feedback.py` — `classification.md` gains a trailing
  exact `Simple` line. The unrecognised-line assertion counts exactly one.
  `log` and `classification` are named once. A `Moderate`/`Defect` loop
  asserts a verdict, no unrecognised line and one new row per label. The
  docstring states both discriminations. The file is now 294 lines (cap
  400). `ruff format --check` and `ruff check` are clean.

## Mechanical check

`.venv/bin/pytest tests/test_triage_feedback.py tests/test_triage_feedback_behavioral.py`: 11/12 passed, 1 failed.

- `test_unrecognised_label_is_no_classification` FAILED on its assertion,
  `tests/test_triage_feedback.py:278`:
  `assert 'match' == 'no-classification'`. It did not ERROR.
- The other 11 tests pass.

## Mutation run (scratch copies, SUT untouched)

The SUT and `plugin/skills/build/scripts/` were copied to `$TMPDIR`. A
candidate implementation was inserted before the `-z "$classification"`
check: a `case` that passes `""|Simple|Moderate|Complex|Defect`, and
otherwise prints `unrecognised classification: $classification` and clears
the class. The test was then run with `triage_feedback_helpers.SCRIPT`
patched to each copy. The scratch copies have been deleted.

| Variant | Result | Failing line |
|---|---|---|
| correct candidate | pass | — |
| prefix `Simple*` | red | 278 verdict |
| first word | red | 278 verdict |
| last match (`tail -1`) | red | 278 verdict |
| logs a row anyway | red | 281 no log |
| line to stderr | red | 279 stdout line |
| label truncated at ` (` | red | 279 stdout line |
| line printed twice | red | 279 stdout line |
| only Simple/Complex recognised | red | 288 verdict (Moderate) |
| Defect not recognised | red | 288 verdict (Defect) |

Every mutant reds on the assertion meant to catch it, and the correct
candidate passes.

## Positive Observations

- The verdict, stdout-line and exit-code assertions each carry stdout (and
  stderr where relevant) as the failure message.
- The fixture puts `classification.md` before the base, as slice 2 does, so
  only `a.py` is in the run's list.
