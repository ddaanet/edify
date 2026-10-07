# Item 1.2 report

Collected count over `tests/test_triage_feedback*.py`: before 23, after 23.

## wc -l

```
  306 tests/test_triage_feedback.py
  179 tests/test_triage_feedback_behavioral.py
   89 tests/test_triage_feedback_failures.py
  246 tests/test_triage_feedback_log.py
  157 tests/triage_feedback_helpers.py
  113 tests/verify_step_helpers.py
```

## KD- grep

```
tests/test_triage_feedback.py:264:    ``colon-label``: ``Moderate (note: see *KD-3*)``, on a bare
tests/test_triage_feedback.py:276:        "colon-label": "Moderate (note: see *KD-3*)",
```

Both hits are the fixture's classification label value (test input, a
string with a colon and asterisks), not a citation of an outline KD. Left
unchanged: the test asserts the label verbatim.

## Docstrings as now read

m7 (hub, `tests/test_triage_feedback.py`, added paragraph):

> This module holds the files-changed, reports and classification tests. It was
> split to keep each module under its line cap, and three sibling modules hold
> the rest. `tests/test_triage_feedback_behavioral.py` holds the
> behavioural-code tests. `tests/test_triage_feedback_log.py` holds the log
> tests: the one-row-per-evidence append and its idempotence.
> `tests/test_triage_feedback_failures.py` holds the failure arms of the
> entry, the reports count and the classification parse.

m8 (`tests/verify_step_helpers.py`):

> Each test builds a throwaway git repo under `tmp_path` and runs the script
> by absolute path with CWD at the repo root, following the subprocess-run
> pattern in `tests/triage_feedback_helpers.py`.

m9 (`tests/test_triage_feedback_log.py`):

> The log, `plans/reports/triage-feedback-log.md`, holds one row per
> evidence: the append is skipped when the log already holds a row equal to the
> new one in every column but the date, and a re-run on new evidence still
> appends. The run itself is not skipped: it still prints its evidence and
> verdict.

Also: new `tests/test_triage_feedback_failures.py` docstring says the module
is for the failure arms (entry stop with ERROR and exit 2 and no log row,
failing git call behind the reports count, classification parse failure);
behavioural-code and log failures stay in their own modules. The behavioral
module's split-from line said the hub keeps "failure tests"; it now says
"classification tests" and names the failures module. The `shutil` import
moved with the shim test.

`just precommit`: green (410/411 passed, 1 xfail; allowlisted
oversized agent prose files reported as before).
