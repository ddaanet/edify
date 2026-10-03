# Item 1.4 slice 1 — RED

Test: `tests/test_changed_files.py::test_phase_without_boundary_gives_run_base`
(file now 287 lines; `ruff check` clean, `docformatter -c` exit 0). SUT
untouched.

## Per-test output

- `test_base_is_parent_of_first_item_report_commit`: pass (existing)
- `test_exempt_paths_committed_in_the_run_are_dropped`: pass (existing)
- `test_no_item_report_exits_1`: pass (existing)
- `test_phase_without_boundary_gives_run_base`: FAILED on its assertion:
  `tests/test_changed_files.py:285: assert result.returncode == 0` ->
  `AssertionError: ERROR: usage: changed-files.sh <job>` (`assert 2 == 0`).
  The `--phase` call is rejected by the current SUT's one-argument check. The
  bare-call assertions above it (exit 0, exact `BASE:` and list) passed, so the
  fixture is valid and the red is on the `--phase` call alone. The
  `BASE: <run base>` first-line and exact-equality assertions below it have not
  yet run; they are born green or red in GREEN.

## Fixture

History: seed -> `plans/j/reports/phase-1-corrector.md` (pre-run) -> run base
-> item 1.1 (`a.txt`) -> `plans/jj/reports/phase-1-corrector.md` (in run, other
job) -> item 1.2 (`b.txt`). Bare output: `BASE: <run base>`, `a.txt`, `b.txt`,
`plans/jj/reports/phase-1-corrector.md` (only `plans/j/` is filtered, so the
other job's report is listed). Whole-history search would name the pre-run
commit; job-ignoring search would name the `jj` commit.

## Fixtures tried and rejected

- First draft expected the list `a.txt`, `b.txt` only: the bare run listed
  `plans/jj/reports/phase-1-corrector.md` too (KD-6 drops only the job's own
  `plans/<job>/`), so the expectation was wrong. Corrected the expected list
  rather than the decoy.
- Decoy only before the run, or only for another job: each discriminates one
  wrong implementation; both kept.
- Mutation proof: not applicable, the test reds against the unchanged SUT.

## Test review revision

The Fixture section's claim that a whole-history search would name the pre-run
commit was false: that commit was the run base itself, so such a search printed
the right `BASE:` and passed. Test review inserted a `j planning` commit as the
run base after the pre-run report, and dropped the redundant first-line
assertion; the file is now 282 lines and the test still fails on
`assert result.returncode == 0` (line 281). See `item-1-4-s1-test-review.md`.
