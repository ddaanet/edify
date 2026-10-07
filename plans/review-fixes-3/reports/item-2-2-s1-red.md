# Item 2.2 slice 1 RED

Written (uncommitted):
- `tests/test_triage_feedback.py`: `test_subdirectory_run_measures_the_repository_root` (module 352 lines), plus the `_run_triage_relative` import.
- `tests/triage_feedback_helpers.py`: `_run_triage_relative(job, cwd)`, which runs `os.path.relpath(SCRIPT, cwd)` with CWD `cwd`, so the script sees a relative `BASH_SOURCE`.

SUT untouched (`plugin/bin/triage-feedback.sh`); no stub needed.

Assertion order: Files changed, Reports, Behavioral code, verdict, exit 0, one log row at the root, no `repo/sub/plans`.

## Per-test output

`tests/test_triage_feedback.py::test_subdirectory_run_measures_the_repository_root` FAILED on its assertion:

```
tests/test_triage_feedback.py:346: in test_subdirectory_run_measures_the_repository_root
    assert "- Reports: 1" in lines, output
E   AssertionError: ## Evidence
E     - Files changed: 1
E     - Reports: 0
E     - Behavioral code: no
E     - Review artifact: none
E
E     ## Verdict
E     no-classification
E
E     WARNING: No corrector report — review gate may have been bypassed
```

Files changed: 1 already holds from `repo/sub` (the first assertion passes); the red is the evidence assertion `Reports: 1`, with `Reports: 0`, `Behavioral code: no` and `no-classification` as the slice predicted. The rest of `tests/test_triage_feedback.py` is 10 passed, 1 failed. `ruff check` and `ruff format --check` clean on both files.

## Mutation proof

None: the test is red against the unchanged script.

## Fixtures tried and rejected

None. The `sub/keep.txt` file is committed with `classification.md` in the planning commit, before the run base, so it stays outside the run's diff and Files changed stays 1.
