# Item 1.4 slice 2 — RED report

Tests added to `tests/test_changed_files.py` (now 368 lines; 32 below the cap,
slice 3 still to add). The SUT was not edited (the one mutation below is
restored).

## Per-test output (against the current SUT, which ignores `--phase`)

- `test_phase_base_is_latest_boundary_commit` — FAILS on its assertion. The
  bare-call assertions pass (run base and full 8-line list). The `--phase`
  assertion fails: `BASE: 4e21bdbd…` (the run base) where `BASE: 3feaadd6…`
  (the re-committed `phase-1-corrector.md`) was expected, with six extra paths
  (`d.txt` first). `assert ['BASE: 4e21b... 'f.txt', ...] == ['BASE: 3feaa...corrector.md']`.
- `test_phase_flag_only_as_exact_second_argument` — passes, as designed
  (red-neutral). Guard from slice 1's code review: `j --phases`, `j extra`,
  `--phase j`, `--phase`, `--phase --phase` each exit 2 with `ERROR:`.
- The four earlier tests still pass. Result: 5 passed, 1 failed.

## Fixture of the main test

seed -> pre-run `phase-1-corrector.md` (j) -> `j planning` (run base) -> items
1.1, 1.2 -> "fix review findings" (adds `phase-1-corrector.md` + `fix.txt`;
subject names neither "boundary" nor "Phase") -> decoy "Phase 2 boundary"
(`d.txt` only) -> item 2.1 -> "tweak" (modifies `phase-1-corrector.md` again +
`f.txt`; the expected base) -> item 2.2 (`g.txt`) -> `plans/jj/reports/
phase-2-corrector.md`.

Expected `--phase`: `BASE: <tweak sha>`, `g.txt`, `plans/jj/reports/
phase-2-corrector.md`.

Choice on the re-committed report: the later modifying commit is the base
(KD-2's `-1`, "the one carrying the later fix"). It does not conflict with
"only later files": the list is the files after that later commit.

Discrimination: the pre-run report catches a search outside
`<run base>..HEAD`; the subject decoy catches a subject match; the first
boundary catches `--diff-filter=A` or oldest-first; the `jj` report is the
latest commit overall, so it catches a search ignoring the job (its path stays
in the list, since only `plans/j/` is filtered).

## Mutation proof

Test: `test_phase_flag_only_as_exact_second_argument` (its behaviour already
sits in the SUT).

- Replaced `if [[ $# -lt 1 || $# -gt 2 || ( $# -eq 2 && $2 != --phase ) ]]; then`
  with `if [[ $# -lt 1 || $# -gt 2 ]]; then`. The test reds on its assertion:
  `('j', '--phases'): NO-BASE: …` — `assert (1, 'NO-BAS') == (2, 'ERROR:')`.
  The main test stayed red alongside it, the other four passed.
- Restored by the swapped replacement. `grep -c` for the mutant line: 0;
  `git status --short plugin` clean; suite re-run: 1 failure, the main test
  only (the expected RED state).

## Fixtures tried and rejected

- Guard check folded into the main test as a paired pre-check: rejected. A
  failure there would mask the main test's red reason; a separate test names
  it.
- Boundary commit subject saying "Phase 1 boundary": rejected (KD-8; would let
  a subject match pass).
- `jj` report placed before the re-commit: rejected. It would not be the
  latest commit, so a job-ignoring search would still land on the right base.
- Excluding `jj`'s report from the expected list: not possible; only
  `plans/j/` and the exempt paths are filtered.

## Lint

`ruff check` clean, `ruff format --check` clean, `docformatter -c` exit 0.
