# Review: Item 1.4 slice (a) — test review

**Scope**: `tests/test_changed_files.py::test_phase_without_boundary_gives_run_base`
(uncommitted diff; no helper was added) and
`plans/build-fixes/reports/item-1-4-s1-red.md`. `changed-files.sh` and slices
(b)–(d) are out of scope.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The test reds on an assertion against the current SUT, and the in-run `jj`
decoy does its job. The pre-run decoy did not: it was committed *as* the run
base, so a whole-history search returned the run base and passed. A
mutated-SUT run confirmed this. The fix inserts a commit between that decoy and
the run base. After the fix the test is still red on its assertion, and both
decoys red their wrong implementation.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The pre-run decoy was the run base, so it could not catch a whole-history
   search**
   - Location: `tests/test_changed_files.py`, fixture of
     `test_phase_without_boundary_gives_run_base`
   - Problem: `base_sha` was `rev-parse HEAD` taken right after the commit
     adding `plans/j/reports/phase-1-corrector.md`. A boundary search over the
     whole history (`git log -1 -- plans/j/reports/phase-*-corrector.md`, no
     range) finds exactly that commit, which is `base_sha`, so it prints the
     right `BASE:`. The docstring and the RED report both said this decoy
     "catches a search over the whole history". It caught nothing. Measured
     with temp copies of the SUT, extended to accept `--phase` (see below): the
     whole-history variant passed against the original fixture.
   - Fix: commit `plans/j/runbook.md` ("j planning") after the pre-run report.
     That commit is the run base, taken from `_commit`'s return value. The
     docstring now states that the decoy sits one commit before the base.
   - **Status**: FIXED

### Minor Issues

1. **Redundant first-line assertion**
   - Location: `tests/test_changed_files.py`, the `--phase` call's
     `splitlines()[0] == f"BASE: {base_sha}"`
   - Note: `result.stdout == plain.stdout` already covers it, because the line
     above pins `plain.stdout`'s first line to `BASE: {base_sha}`. Removed.
   - **Status**: FIXED

2. **RED report's Fixture section carried the false decoy claim**
   - Location: `plans/build-fixes/reports/item-1-4-s1-red.md`
   - Note: the RED observations are left as they were recorded. A "Test review
     revision" section was appended that names the false claim, the fixture
     change, the new line count and the new failing line.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_changed_files.py`: a `j planning` commit now sits between the
  pre-run phase report and item 1.1 and is the run base
  (`base_sha = _commit(...)`). The two decoy `_commit` calls use shorter
  subjects, so each fits on one line. Subjects are labels only (KD-8), and the
  docstring carries what they used to say. The docstring's history and decoy
  paragraph were rewritten to match. The redundant first-line assertion was
  dropped. The file went from 287 to 282 lines.
- `plans/build-fixes/reports/item-1-4-s1-red.md`: appended the "Test review
  revision" section.

## Checks

1. **Mechanical**: FAILED on an assertion, at
   `tests/test_changed_files.py:281: assert result.returncode == 0`, which
   reports `ERROR: usage: changed-files.sh <job>` (`assert 2 == 0`). The
   bare-call assertions above it passed, so the fixture is valid. The other 3
   tests in the file pass. Result: 3/4 passed, 1 failed.
2. **Wrong-reason hunting**: I ran the test function against temp copies of
   `changed-files.sh` plus `exempt-paths.sh` in `$TMPDIR`. Each copy accepts
   `j --phase` and rebinds `base_sha` after the KD-1 derivation. The real SUT
   and the test were not touched for this.

   | Variant | Original fixture | Fixed fixture |
   |---|---|---|
   | accept and ignore `--phase` (minimal GREEN) | pass | pass |
   | correct: `git log -1 <base>..HEAD -- plans/j/reports/phase-*-corrector.md` | pass | pass |
   | whole history (no range) | **pass (decoy decorative)** | red |
   | ignores the job (`plans/*/reports/...`, in range) | red | red |
   | inclusive range (`<base>^..HEAD`) | pass | pass |

   - The minimal GREEN passes slice (a). That is accepted as briefed: slice (b)
     pins the boundary.
   - The inclusive-range variant can never be caught, by any fixture. If the
     base commit touches a phase report, it names the base. Otherwise it
     matches the correct search. Either way it never prints a different base.
   - Once (b) lands, both decoys stay load-bearing. Any search lacking the
     range reds on the pre-run report, and any search lacking the job scope
     (including a `plans/j*` prefix match) reds on the `jj` report.
   - Subject-keyed searches (forbidden by KD-8) are not caught here, because
     no subject in range names a boundary. That belongs to (b).
3. **Line budget**: 282 lines. There is no real repetition left to factor.
   `_init_repo`, `_commit` and `_run_script` already carry the setup, and the
   new test's only duplication with existing tests is one `item 1.1` commit
   line. A fixture helper with one caller would be premature, so none was
   added. No docstring was shaved.
4. **Lint**: `ruff check` passed, `ruff format --check` passed, and
   `docformatter -c` exited 0.

## Positive Observations

- The bare call is pinned exactly before `--phase` output is compared to it.
  This means the equality cannot pass on two empty or both-wrong outputs.
- The expected list includes the other job's phase report. The RED dispatch
  corrected its expectation rather than removing the decoy.

## Recommendations

- **Slice (b)**: start from this test's fixture and add a `j` boundary
  commit (`plans/j/reports/phase-1-corrector.md`) inside the run, followed by
  a later item. Slice (a) is the negative and slice (b) is its positive over
  the same fixture, differing only in the trigger. Extract the shared fixture
  into a helper at that point, when it has a second caller. Give the real
  boundary a subject that does not follow KD-8's `Phase P boundary` form, so
  a subject-keyed search reds. Have the run's `jj` decoy commit come after the
  `j` boundary, so a job-ignoring `-1` search names the wrong commit.
- **Design observation, not a finding**: under KD-1 the run base is the parent
  of the earliest `item-*` addition ever made for the job, so pipeline history
  cannot contain a `j` phase report before it. Only a hand-authored fixture
  like this one can falsify the `<base>..HEAD` range clause. KD-2 still names
  that clause, so pinning it is correct.
