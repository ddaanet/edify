# Review: Item 2.1 slice 1 — test review

**Scope**: `tests/test_changed_files_errors.py`
(`test_late_diff_failure_prints_error_alone` and the module docstring
paragraph), `tests/changed_files_helpers.py` (`_run_script`'s
`path_prepend`), `plans/review-fixes-3/reports/item-2-1-s1-red.md`
**Date**: 2026-10-07
**Mode**: review + fix (TDD test review, `tdd-slice.md` §(b))

## Summary

The test fails genuinely, on its stdout assertion. The shim passes through
every call except `diff`, `b.txt` is a real modification, and the
exact-list assertion pins "no `BASE:`, no path". Two fixes went in. The new
docstring's summary line broke the docformatter gate (`docformatter -c` exit 3),
and the shim now embeds the real git path with `shlex.quote` rather than
double quotes.

**Overall Assessment**: Ready

## Mechanical first check

The test was run against the unchanged SUT, before and after the fixes. Both
runs FAILED on the assertion `result.stdout.splitlines() == ["ERROR: git diff
failed"]`. stdout held `BASE: <sha>`, `a.txt`, `b.txt` and then
`ERROR: git diff failed`. The exit-2 assertion passed, because the script
already exits 2. Nothing PASSED and nothing ERRORed. No mutation proof
applies, because the behaviour is absent from the SUT.

## Wrong-reason analysis

- **The state of the world that fails it after GREEN:** any implementation
  that writes `BASE:` or a path to stdout before it knows the diff's exit
  status. Today's script prints `BASE:` before the diff runs and streams
  paths from the `while read` loop. That is the red seen.
- **What else could produce exactly `["ERROR: git diff failed"]`:** nothing
  plausible. The other `ERROR:` arms (`git log failed`,
  `git rev-parse --show-toplevel failed`, the parent-resolution message, the
  `--phase` log message) carry different text. The exact equality rules them
  out. To reach the diff arm, the shim must pass `rev-parse` and `log` through
  to real git, so the run reaching that arm already proves pass-through.
- **Shim soundness:** `shutil.which("git")` is resolved in the test process
  before `PATH` is prepended. Its absolute path is baked into the shim, so the
  shim cannot resolve itself. Non-`diff` calls exit with the real git's
  status. Only a first argument of exactly `diff` turns the exit into 128, and
  that happens after the real command's output. The script calls
  `git diff --name-only …` with `diff` first.
- **`b.txt` is changed, not added:** `_init_repo` seeds `b.txt` as `base\n`,
  and the run commit writes `changed\n`. The RED output lists it.
  `item-1-1.md` is dropped by the `plans/j/` prefix filter, as expected.
- **Residual (recorded, not fixed):** after GREEN, the test's observable is
  `ERROR:` alone, and that observable would look the same if the shim's real
  `diff` printed nothing. The "late" part of the name is shown at RED time,
  where `a.txt` and `b.txt` appear above the error. The finished artifact
  does not show it. The `BASE:` line still discriminates, because every
  plausible ordering prints `BASE:` before any path. A pass-through control
  run was considered and not added: it is scope beyond the slice, and the
  unshimmed list tests in `tests/test_changed_files.py` cover the listing
  path.
- **Portability:** `#!/bin/sh`, `[ "$1" = diff ]`, `status=$?` and
  `exit $status` are all POSIX and run under macOS `/bin/sh` (bash 3.2 in sh
  mode). `chmod 0o755` and the `PATH` prepend are portable. A `tmp_path`
  holding spaces is safe both in `PATH` and in the shim. The shim's own path
  never appears in the shim text.
- **Helper:** `path_prepend` comes after `*args`, so it is keyword-only, and
  the existing callers (`_run_script(repo, …)` and `script=` by keyword) are
  unchanged. All 15 sibling tests pass. Using `env["PATH"]` rather than the
  siblings' `env.get("PATH", "")` avoids an empty `PATH` element, so it is
  not flagged.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Docstring summary line fails the docformatter gate**
   - Location: `tests/test_changed_files_errors.py:169`
   - Problem: the summary
     `A diff failing after the base is found prints ``ERROR:`` and nothing else.`
     is 74 characters, so the line is 81 columns. That exceeds the ≤70-char
     summary rule (`memory/edify-docformatter-d205.md`), and
     `docformatter -c tests/test_changed_files_errors.py` exited 3. The RED
     report's "ruff check / ruff format --check clean" is true, but it did not
     cover docformatter, which `just check` runs.
   - Fix: shorten the summary only, to
     `A diff failing once the base is known prints ``ERROR:`` alone.` (62
     characters). The description paragraph is untouched.
   - **Status**: FIXED

### Minor Issues

1. **Shim embeds the git path in double quotes**
   - Location: `tests/test_changed_files_errors.py:185`
   - Note: `f'"{real_git}" "$@"\n'` is safe for spaces but not for `"`, `$`,
     a backtick or `\` in the git install path, which `sh` would expand or
     split. Replaced with `f'{shlex.quote(real_git)} "$@"\n'` and added
     `import shlex`.
   - **Status**: FIXED

2. **D-90's text says "exits 2 with `ERROR:`", not "alone"**
   - Location: `docs/references/build-run-state.md` D-90, which is cited by
     the new docstring ("D-90 keeps stdout to ``ERROR:`` alone on exit 2")
     and by the module-docstring paragraph
   - Note: the test pins the stricter KD-4 contract. D-90's text only says a
     git failure "exits 2 with `ERROR:`", and Item 4.1's D-90 amendments
     (m3, m16) do not add "alone". The citation is the right decision. The
     decision text is looser than what the test pins.
   - **Status**: OUT-OF-SCOPE. The design record is not in this review's
     scope. The orchestrator may want Item 4.1 to give D-90 KD-4's "nothing
     but `ERROR:` on exit 2" clause.

3. **Sibling shim uses the same double-quote form**
   - Location: `tests/test_triage_feedback_failures.py:46`
     (`exec "{real_git}" "$@"`)
   - **Status**: OUT-OF-SCOPE. It belongs to Items 2.2–2.4, which are out of
     scope. Recorded so that Item 2.3's shims can use `shlex.quote` the same
     way.

## Fixes Applied

- `tests/test_changed_files_errors.py:169`: shortened the docstring summary
  to 62 characters, so that docformatter passes. The description is
  unchanged.
- `tests/test_changed_files_errors.py:185`: the shim embeds
  `shlex.quote(real_git)`.
- `tests/test_changed_files_errors.py:16`: added `import shlex`.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m2 / KD-4: late `git diff` failure → stdout `ERROR: git diff failed` alone, exit 2 | Satisfied (test pins it; red today) | `test_late_diff_failure_prints_error_alone`: `returncode == 2` and `stdout.splitlines() == ["ERROR: git diff failed"]` |
| Docstrings cite D-numbers, never an outline KD | Satisfied | Test and module docstrings cite D-90 only |
| Docstring summary ≤70 chars, no docstring shaved | Satisfied after fix | Summary is 62 characters, description is intact, `docformatter -c` exits 0 |

## Gates after fixes

`ruff check` (exit 0), `ruff format --check` (exit 0), `docformatter -c`
(exit 0) and `mypy` (exit 0) were run on both touched files. Line counts are
201 for `tests/test_changed_files_errors.py` and 94 for
`tests/changed_files_helpers.py`.

## Final red run (verbatim)

`.venv/bin/pytest -p no:markdown_report tests/test_changed_files.py tests/test_changed_files_errors.py tests/test_changed_files_phase.py -q`

```
...........F....                                                         [100%]
=================================== FAILURES ===================================
__________________ test_late_diff_failure_prints_error_alone ___________________
tests/test_changed_files_errors.py:201: in test_late_diff_failure_prints_error_alone
    assert result.stdout.splitlines() == ["ERROR: git diff failed"], result.stdout
E   AssertionError: BASE: b1cd0d09ef77971da751e9c992830ee583c4f545
E     a.txt
E     b.txt
E     ERROR: git diff failed
E
E   assert ['BASE: b1cd0... diff failed'] == ['ERROR: git diff failed']
E
E     At index 0 diff: 'BASE: b1cd0d09ef77971da751e9c992830ee583c4f545' != 'ERROR: git diff failed'
E     Left contains 3 more items, first extra item: 'a.txt'
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_changed_files_errors.py::test_late_diff_failure_prints_error_alone
1 failed, 15 passed in 9.31s
```

Per-test result: `test_late_diff_failure_prints_error_alone` FAILED on its
stdout assertion, and the 15 sibling tests PASSED.

## Positive Observations

- The exact-list equality pins "no `BASE:`" and "no path" in one positive
  assertion instead of using bare negatives.
- The fixture makes the failure genuinely late: a changed `b.txt` and an added
  `a.txt` sit beside the excluded report, so the red shows streamed paths.
- `path_prepend` follows the `line_limits_helpers.py` and
  `triage_feedback_helpers.py` precedent, and it is keyword-only.

## Recommendations

- Item 4.1 could give D-90 KD-4's "exit 2 prints `ERROR:` and nothing else"
  clause, so that the decision text matches what this test pins (minor 2).
