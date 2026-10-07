# Review: Item 2.3 slice 1 — test review

**Scope**: uncommitted changes in `tests/test_triage_feedback_failures.py` and
`tests/triage_feedback_helpers.py`, plus the RED report
`plans/review-fixes-3/reports/item-2-3-s1-red.md`. The SUT
`plugin/bin/triage-feedback.sh` was mutated in place only and restored each
time.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The slice's two tests pin the usage error (`no-args`, `stale-base`) and the
`changed-files.sh` exit-2 arm (m5). Each case's mutation proof reproduced with a
different mutation of the reviewer's choosing. Wrong-reason hunting found one
real gap: the `changed-files.sh` test stayed green when the guard printed both
lines but did not exit. The test now asserts the exact stdout, and the gap mutant
reds. Two smaller fixes followed: a docstring that described a failure mode the
SUT does not have, and the `no-args` case skipping the shared fixture's git
config insulation.

**Overall Assessment**: Ready

## Mechanical check: mutation proofs reproduced

Each case passes against the unchanged SUT, as the RED report records. Every
mutation below differs from the RED report's mutant. Each is an exact
replacement that occurs once in the file. Each was restored by applying the swap
inverted, and the restore was proven with `command grep -cF <mutant text>` = 0
and an empty `git diff -- plugin/bin/triage-feedback.sh`.

| Case | Reviewer mutation | Result (final tests) |
|------|-------------------|----------------------|
| `[no-args]` | A: `job_dir="${1:-}"` → `job_dir="${1:-j}"` (a missing argument defaults to `j`) | red: `assert 0 == 1`, verdict report on stdout; `[stale-base]` green |
| `[stale-base]` | B: `[[ $# -gt 1 ]]` → `[[ $# -gt 2 ]]` | red: `assert 0 == 1`, verdict report on stdout; `[no-args]` green |
| `test_changed_files_error_is_printed_then_exit_2` | C: `"$job_dir") \|\| status=$?` → `"$job_dir") \|\| status=0` (the guard never sees the failure) | red on the stdout equality: `['ERROR: git diff failed'] == [...]` |
| same | D: the guard's `printf` and `echo` swapped (cause printed before the output) | red on the stdout equality, index 0 diff |
| same | E: the guard's `exit 2` dropped (prints both lines, does not stop) | before the fix: **green**; after it: red, `Left contains one more item: 'ERROR: git diff failed'` |

Mutant A is stronger than the RED report's: the mutant run reaches a verdict and
logs a row, so in `[no-args]` the exit code, the stdout and the no-row
assertions all discriminate.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The `changed-files.sh` test did not pin "stops"**
   - Location: `tests/test_triage_feedback_failures.py`,
     `test_changed_files_error_is_printed_then_exit_2`
   - Problem: under mutant E (the guard's `exit 2` dropped) the run printed
     `ERROR: git log failed`, `ERROR: changed-files.sh exited 2`, then
     `ERROR: git diff failed`. It exited 2 from the reports-count guard further
     down, not from the arm under test. All six assertions held: both lines
     present and in order, no `## Evidence`, exit 2, no row. The exit-2
     assertion was met by a different exit site.
   - Fix: the two `in` checks, the `index` ordering check and the
     `## Evidence` negative became one equality,
     `lines == ["ERROR: git log failed", "ERROR: changed-files.sh exited 2"]`.
     It pins "printed first", "then" and "stops" together, and subsumes the
     `## Evidence` negative.
   - **Status**: FIXED. Mutants C, D and E all red on it.

### Minor Issues

1. **The docstring claimed a failure mode the SUT does not have**
   - Location: the same test's docstring
   - Note: it said a status-1-only guard "lets exit 2 through to an evidence
     report built from the error text". Observed under the RED report's mutant
     and under mutant C, the error text becomes the base and the run dies at
     `ERROR: git diff failed`, exit 2, with no evidence report. The docstring
     was rewritten to the observed behaviour. It now also names the
     print-but-no-exit guard, which ends the same way. The summary line is
     unchanged (69 chars), and no prose was shaved.
   - **Status**: FIXED

2. **The `no-args` case bypassed the shared fixture's insulation**
   - Location: `test_usage_error_exits_1`, with `_run_triage` in
     `tests/triage_feedback_helpers.py`
   - Note: every other run in the module goes through `_run_triage`, which sets
     `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` to `/dev/null`. The `no-args`
     branch called `subprocess.run([SCRIPT])` with the inherited environment.
     Against the real SUT no git runs, but under a guard mutant the run reads
     the user's git config while `stale-base` does not. Fixed as follows:
     - `_run_triage` takes `job: str | None`, where `None` passes no job
       argument. Its docstring says so.
     - The test is parametrized on `(job, extra_args)`, `(None, ())` and
       `(JOB, ("HEAD",))`, and makes one `_run_triage` call.
     - The unused `subprocess` and `SCRIPT` imports were dropped from the test
       module.
     - The 14 existing callers pass a `str`, so none of them changed.
   - **Status**: FIXED

3. **Module docstring wrap**
   - Location: `tests/test_triage_feedback_failures.py` module docstring
   - Note: the RED edit left a short line ("printed first), a failing git call
     behind") mid-paragraph. The paragraph was reflowed and its text is
     unchanged. `docformatter -c` passes.
   - **Status**: FIXED

## Wrong-reason hunting (answers to the dispatch's questions)

- **Is "then" asserted?** Yes. Before the fix it was the `index` comparison
  (mutant D redded it, `assert 1 < 0`). After the fix it is the list equality
  (mutant D reds at index 0).
- **Does "no log row" discriminate?**
  - **Usage cases: yes.** The RED report's control shows `j` alone logs an
    `underclassified` row in this fixture. Mutants A and B both reach a verdict
    and write the row.
  - **`changed-files.sh` case: no, by construction.** Any mutant that lets the
    run pass this arm (the RED report's `-eq 1`, C, E) uses the error text as
    the base, so the run dies at `ERROR: git diff failed` before any row. No
    fixture changes that: whatever `changed-files.sh` prints on exit 2 is not a
    revision. The assertion stays as a pin of the interface's "no log row". The
    discrimination for "a `changed-files.sh` failure → no row" lives in
    `test_no_base_is_an_error_with_no_log_row`, whose fixture reaches a verdict
    when unguarded. Recorded, not a defect.
- **Is "empty stdout" asserted for the usage cases?** Yes,
  `result.stdout == ""`. Stderr is pinned exactly too:
  `result.stderr.strip() == "Usage: triage-feedback.sh <job>"`. So a usage exit
  1 from anywhere else, such as a `set -e` exit 1, would red.
- **Is the `changed-files.sh exited 2` assertion exact?** Yes. It is a
  whole-line match, now inside the list equality, so `exited 1` or any other
  status reds.
- **Does the unborn-repo fixture reach `git log failed` for the intended
  reason?** Yes. A direct probe of the fixture gave stdout
  `ERROR: git log failed\nERROR: changed-files.sh exited 2\n`, stderr
  `fatal: your current branch 'main' does not have any commits yet`, exit 2.
  `rev-parse --show-toplevel` succeeds in an unborn repo, so the run passes
  triage's `rev-parse` guard and fails at `changed-files.sh`'s first-commit
  `git log`, the only site that prints `ERROR: git log failed`. The test does
  not assert git's wording, which varies across git versions. The stdout
  equality turns any fixture drift into a red: a different first failure prints
  a different `ERROR:` line, or `NO-BASE:`.

## Fixes Applied

- `tests/test_triage_feedback_failures.py`, changed-files test: four
  stdout-line assertions replaced by one exact list equality. Docstring
  rewritten to the observed failure modes.
- `tests/test_triage_feedback_failures.py`, `test_usage_error_exits_1`:
  parametrized on `(job, extra_args)`, with one `_run_triage` call. Dropped the
  `subprocess`/`SCRIPT` imports.
- `tests/test_triage_feedback_failures.py`: module docstring reflowed.
- `tests/triage_feedback_helpers.py`, `_run_triage`: takes `job: str | None`.
  `None` passes no job argument. One docstring sentence added.

## Final verification

- `ruff check` and `ruff format --check` pass on both files.
  `uv run --frozen docformatter -c` passes on both, and so does
  `uv run --frozen mypy` (exit 0).
- Line counts: `test_triage_feedback_failures.py` 184 and
  `triage_feedback_helpers.py` 194, both under 400.
- The triage modules together (`test_triage_feedback.py`, `_failures`,
  `_location`, `_behavioral`, `_log`): 29 passed.
- Failures module, final run (`.venv/bin/pytest -p no:markdown_report -v`):

```
test_failing_reports_diff_is_an_error_not_none PASSED
test_no_base_is_an_error_with_no_log_row PASSED
test_outside_a_work_tree_is_one_error_line PASSED
test_usage_error_exits_1[no-args] PASSED
test_usage_error_exits_1[stale-base] PASSED
test_changed_files_error_is_printed_then_exit_2 PASSED
6 passed
```

  The cases pass against the unchanged SUT, as a mutation-proven slice should.
  Their red is the mutant table above.
- After the last restore, `git diff -- plugin/bin/triage-feedback.sh` is empty
  (0 bytes). `git status --short` shows only the two test files modified, plus
  the untracked inbox briefs and the RED report, then this report.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Exit 1, usage on stderr, for zero arguments | Satisfied | `test_usage_error_exits_1[no-args]`; mutant A reds |
| Exit 1, usage on stderr, for two or more arguments | Satisfied | `test_usage_error_exits_1[stale-base]`; mutant B reds |
| m5: `changed-files.sh` exit 2 → its output first, `ERROR:` cause, exit 2, no row | Satisfied | `test_changed_files_error_is_printed_then_exit_2`; mutants C, D, E red. The no-row clause is a contract pin here (see above). |

## Positive Observations

- The RED report ran a control (`j` alone logs a row) before relying on the
  `stale-base` fixture. That is what makes the usage cases' no-row assertion
  evidence.
- The RED report's mutant 3 took in the `changed-files.sh` call line to avoid
  the `rev-parse` guard's identical `if`, per the list revision.
- Returncode is asserted first in the usage test, so a red names the exit code
  rather than an incidental stderr difference.
