# Item 1.1 slice 4 RED: unrecognised label is no-classification

Test added to `tests/test_triage_feedback.py` (now 269 lines; helpers
unchanged). SUT `plugin/bin/triage-feedback.sh` untouched.

## Per-test output

- `tests/test_triage_feedback.py::test_unrecognised_label_is_no_classification`
  FAILED on its first assertion, at `tests/test_triage_feedback.py:266`:
  `assert 'match' == 'no-classification'`. Stdout was Files changed 1,
  Reports 0, Behavioral code yes, Review artifact none, verdict `match`.
  The label falls through to `match`, as the slice predicted.
- The other 11 tests in `test_triage_feedback.py` and
  `test_triage_feedback_behavioral.py` pass (11/12 passed).

The stdout-line, exit-0 and no-log-row assertions follow the verdict
assertion and are unreached today. The reds are therefore on the verdict
only; the later assertions are exercised in GREEN.

## Mutation proof

None. The new test reds on its assertion against the unchanged SUT.

## Fixtures tried and rejected

None. The `classification.md` is committed with a planning commit before the
item report, as `test_reports_exclude_the_per_item_report` does, so the file
sits on disk and outside the run range. A `Simple / Moderate ...` label
reads `underclassified` under a prefix match; the observed `match` shows
the current parse matches neither `Simple` nor `Complex`, so a fixture
distinguishing the two failure modes is not needed.
