# Review: Item 2.2 slice 1 test review

**Scope**: uncommitted `tests/test_triage_feedback.py`
(`test_subdirectory_run_measures_the_repository_root`),
`tests/triage_feedback_helpers.py` (`_run_triage_relative`), and the RED report
`plans/review-fixes-3/reports/item-2-2-s1-red.md`. The SUT
`plugin/bin/triage-feedback.sh` is OUT and was not edited.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The mechanical check holds: the test FAILED on an assertion (`- Reports: 1`),
neither ERROR nor PASSED. The evidence, verdict and log assertions all
discriminate a root-relative run from today's CWD-relative one. The relative
invocation did not, though. The helper ran the real script by
`os.path.relpath(SCRIPT, cwd)`, and that path climbs to `/`, where surplus `..`
are absorbed. So it resolved from the repository root as well as from `sub`,
and a GREEN that ran `cd "$(git rev-parse --show-toplevel)"` before resolving
`script_dir` would have passed every assertion. The fix runs the script through
a `plugin` symlink beside `repo`. The test is still red on the same assertion.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The relative invocation does not catch a cd before path resolution**
   - Location: `tests/triage_feedback_helpers.py` `_run_triage_relative`
   - Problem: `os.path.relpath(SCRIPT, repo/sub)` gives
     `../../../../../Users/david/code/edify/plugin/bin/triage-feedback.sh`. It
     climbs to `/`, and from `repo` it resolves to the same file because the
     extra `..` stops at `/`. The probe ran `ls` on that path from both
     `repo/sub` and `repo`, and both found the script. I made a scratch copy of
     the SUT with `cd "$(git rev-parse --show-toplevel)"` inserted before
     `script_dir` is computed. I put it under the project's `tmp/`, so its
     relpath climbs to `/` as the real script's does, and ran it with this
     fixture by its relpath from `repo/sub`. It exited 0 and printed
     `Files changed: 1`, `Reports: 1`, `Behavioral code: yes` and
     `underclassified`. It wrote one root log row and no `repo/sub/plans`. That
     plausible but wrong GREEN passes every assertion, and the helper's
     docstring claim ("which a change of directory would break") was false
     under test.
   - Fix: the helper now takes `link_dir`, makes `link_dir/plugin` a symlink
     to the real `plugin` directory and runs `../../plugin/bin/triage-feedback.sh`
     from `repo/sub`. It links the whole directory so that
     `$script_dir/../skills/build/scripts/changed-files.sh` still resolves
     through the link. From `repo` that path names `tmp_path/../plugin`, which
     does not exist. The test passes `tmp_path`. Both docstrings now state the
     mechanism, and the module docstring names the helper's different
     invocation.
   - Verification: I put the cd-first scratch copy and an unmutated copy in a
     directory separate from the fixture and ran the test body against each,
     with `SCRIPT` patched. The control reds on `- Reports: 1`. The mutant reds
     with `ERROR: changed-files.sh exited 127` (`../../plugin/bin/../skills/...:
     No such file or directory`).
   - **Status**: FIXED

### Minor Issues

1. **A missing log fails as a bare `FileNotFoundError`**
   - Location: `tests/test_triage_feedback.py`, the row-count line
   - Note: `len(log.read_text(...).splitlines()[2:]) == 1` had no message, and
     a GREEN that wrote the log elsewhere would fail on an exception that does
     not carry the script output. It now asserts `log.is_file(), output` first,
     then `len(rows) == 1, "\n".join(rows)`, following the pattern at line 243.
   - **Status**: FIXED

## Assertions checked, no change needed

- `- Reports: 1`: from `sub`, the `:(glob)plans/j/reports/*` pathspec is
  CWD-relative and reads 0. From the root only `item-1-1-s1-red.md` counts,
  because `item-1-1.md` is excluded. Discriminates.
- `- Behavioral code: yes`: from `sub`, `:(literal)a.py` names `sub/a.py` and
  the diff is empty. Discriminates.
- Verdict `underclassified`: from `sub`, `plans/j/classification.md` is missing
  and the verdict is `no-classification`. Discriminates.
- One root log row: today no log is written. Discriminates.
- `- Files changed: 1` and exit 0 already hold today, because
  `changed-files.sh` cds to the toplevel itself. They are not vacuous: a GREEN
  that loses `changed-files.sh` exits 2 and fails both. The count is 1 for the
  intended reason. `sub/keep.txt` is in the planning commit before the base,
  and both reports sit under the exempt `plans/j/reports/`, so `a.py` alone
  counts.
- `not (repo/sub/plans).exists()` passes trivially today. Over the same fixture
  it is paired with the positive root-row assertion, so a fix that measures
  from the root but writes the log CWD-relative reds on it.

## Fixes Applied

- `tests/triage_feedback_helpers.py` `_run_triage_relative`: new `link_dir`
  parameter, `plugin` symlink, short relative path, docstring explains why.
- `tests/triage_feedback_helpers.py` module docstring: names the helper's
  relative invocation.
- `tests/test_triage_feedback.py` test docstring: states the symlink and the
  exit-2 outcome of a cd-first resolution.
- `tests/test_triage_feedback.py` call site: passes `tmp_path`. The log
  assertion is now `is_file` plus a row count with a message.

## Final run

`.venv/bin/pytest -p no:markdown_report tests/test_triage_feedback.py::test_subdirectory_run_measures_the_repository_root`
gives FAILED on an assertion:

```
tests/test_triage_feedback.py:348: in test_subdirectory_run_measures_the_repository_root
    assert "- Reports: 1" in lines, output
E   AssertionError: ## Evidence
E     - Files changed: 1
E     - Reports: 0
E     - Behavioral code: no
E     - Review artifact: none
E
E     ## Verdict
E     no-classification
```

- Whole module: 1 failed (this test), 10 passed.
- `ruff check` reports all checks passed and `ruff format --check` reports both
  files already formatted.
- Sizes: `test_triage_feedback.py` 356 lines, `triage_feedback_helpers.py` 184.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m1 slice 1 (the run from `sub` measures the root, logs at the root, nothing under `sub`) | Pinned | every Expect line from the slice is asserted; the relative invocation now discriminates |

## Notes for GREEN

The script must resolve `BASH_SOURCE` to `script_dir` before any change to the
root, or call `changed-files.sh` before the change. Under this test, a cd that
comes first exits 2 with `changed-files.sh exited 127`.
