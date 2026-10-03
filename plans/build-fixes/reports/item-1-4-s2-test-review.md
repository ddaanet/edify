# Review: Item 1.4 slice 2 — test review

**Scope**: The uncommitted diff to `tests/test_changed_files.py`, which adds
`test_phase_base_is_latest_boundary_commit` and
`test_phase_flag_only_as_exact_second_argument`; the RED report
`plans/build-fixes/reports/item-1-4-s2-red.md`; the module layout. The SUT
(`changed-files.sh`) is out of scope and was not changed. It was mutated
twice in place and restored each time, as described below.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The main test fails on its `--phase` assertion against the current SUT, and
the guard test passes. A guard mutation of my own, different from the RED
report's, reds the guard test on its assertion. I hunted for wrong reasons
with 13 scratch SUT variants and by removing each decoy in turn. Two decoys
were weak. The subject decoy sat before the real base, so a
subject-or-path union implementation passed. The pre-run decoy guarded
nothing in this test, although the docstring said it did. I fixed both. The
module was split three ways to get it off its line cap.

**Overall Assessment**: Ready

## Files the split created or changed (stage these by name)

- `tests/changed_files_helpers.py` — new, 82 lines
- `tests/test_changed_files.py` — changed, 172 lines (was 368)
- `tests/test_changed_files_phase.py` — new, 144 lines

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Subject decoy did not red its own wrong implementation**
   - Location: `test_phase_base_is_latest_boundary_commit`, the
     "Phase 2 boundary" commit
   - Problem: The decoy came before the expected base (`tweak`). Two
     problems followed:
     - A union implementation, "latest commit in range whose subject
       matches or which touches the report", lands on `tweak` and passed
       (scratch variant `subject_or_path`).
     - A pure subject match redded with or without the decoy, because the
       real boundaries' subjects never match. So the decoy discriminated
       only "subject first, path fallback" (`subject_then_path`).

     Removing the decoy confirmed this: both subject variants depend on it,
     and the union variant passed even with it in place.
   - Fix: Move the decoy after the expected base. `d.txt` is now listed
     under `--phase`, which also adds evidence for "only later files". The
     expected `--phase` list is `d.txt`, `g.txt` and
     `plans/jj/reports/phase-2-corrector.md`.
   - **Status**: FIXED

2. **Module parked near its 400-line hard cap**
   - Location: `tests/test_changed_files.py` (368 lines, and slice 3 still
     adds a `--phase` test)
   - Problem: A file near its cap has stopped signalling (recall
     `line-caps`).
   - Fix: Split along the fixture/base/phase seam, following
     `tests/review_range_helpers.py`:
     - `_run_git`, `_init_repo`, `_run_script`, `_commit`, `REPO_ROOT` and
       `SCRIPT` go to `tests/changed_files_helpers.py`.
     - The three `--phase` tests go to `tests/test_changed_files_phase.py`.

     A script compared each function's source with `git show HEAD`: all
     four helpers, the three base/list tests and
     `test_phase_without_boundary_gives_run_base` are byte-identical. The
     guard test is byte-identical to its uncommitted RED version. No
     docstring was shortened.
   - **Status**: FIXED

### Minor Issues

1. **Pre-run decoy was dead weight, and the docstring misstated its role**
   - Location: `test_phase_base_is_latest_boundary_commit`, the
     "pre-run phase" commit and the docstring's decoy paragraph
   - Problem: The docstring said the pre-run report catches "a search
     outside `<run base>..HEAD`". It cannot: an in-run boundary is always
     later than any pre-run commit. So a whole-history `git log -1` lands on
     the right base and passed this test (`whole_history_latest`). Removing
     the decoy changed no variant's result. Slice 1's
     `test_phase_without_boundary_gives_run_base` pins the range, and it
     reds that variant.
   - Fix: Remove the pre-run commit. "fix review findings" now adds the
     report and `tweak` modifies it, which is KD-2's "modified rather than
     added" and "committed twice" shape. The docstring now names the slice-1
     test as the one pinning the range.
   - **Status**: FIXED

## Fixes Applied

- `tests/changed_files_helpers.py` — new. Shared fixtures moved here
  verbatim, with a module docstring.
- `tests/test_changed_files.py` — keeps the three base/list tests verbatim.
  The module docstring points to the phase module and the helpers. Imports
  come from `.changed_files_helpers`.
- `tests/test_changed_files_phase.py` — new. Holds the slice-1 phase test
  (verbatim), the revised main test (decoy moved, pre-run commit removed,
  docstring rewritten to match what each decoy catches) and the guard test
  (verbatim).

## Check 1 — mechanical

The current SUT ignores `--phase`. Results after the fixes:

| Module | Test | Result |
|---|---|---|
| `test_changed_files.py` | `test_base_is_parent_of_first_item_report_commit` | passed |
| `test_changed_files.py` | `test_exempt_paths_committed_in_the_run_are_dropped` | passed |
| `test_changed_files.py` | `test_no_item_report_exits_1` | passed |
| `test_changed_files_phase.py` | `test_phase_without_boundary_gives_run_base` | passed |
| `test_changed_files_phase.py` | `test_phase_base_is_latest_boundary_commit` | **FAILED** |
| `test_changed_files_phase.py` | `test_phase_flag_only_as_exact_second_argument` | passed |

The main test passes its bare-call assertion and fails the `--phase`
assertion at `test_changed_files_phase.py:115`:
`'BASE: <run base>' != 'BASE: <tweak>'`, with five extra items, the first
being `e.txt`. Summary: 5/6 passed, 1 failed. I saw the same split, with the
failure at the old `:340`, before the fixes.

### Guard mutation proof (a different mutation from the RED report's)

- **Mutation:** in the job-name `case`, replace
  `'' | . | .. | --phase | */* | *[*?[\\]*)` with
  `'' | . | .. | */* | *[*?[\\]*)`. The `--phase` alternative is the one
  dropped. The RED report instead dropped the `$2 != --phase` clause of the
  argument-count guard.
- **Landed:** `grep -c` for the mutant line returned 1.
- **Result:** the guard reds on its assertion:
  `('--phase',): NO-BASE: no committed plans/--phase/reports/item-* report`,
  `assert (1, 'NO-BAS') == (2, 'ERROR:')`. The main test stayed red and the
  other four passed.
- **Restore:** applied the inverse replacement. `grep -c` returned 0 for the
  mutant line and 1 for the original. The suite went back to 5 passed, 1
  failed (the main test).

I ran the mutation once before the split and once after, against the new
module, with the same result each time. `git status` shows nothing under
`plugin/`.

## Check 2 — wrong-reason hunting

Scratch variants live under `/tmp/claude/build-fixes/variants/`. Each is a
copy of the SUT, plus `exempt-paths.sh`, with a `--phase` block inserted
before the `BASE:` print. A driver rebinds `changed_files_helpers.SCRIPT`
and runs the module's tests directly. The tracked script was never used for
this.

Results against the final modules (RED means the test caught the variant):

| Variant | Latest-boundary test (main) | Slice-1 test | Guard |
|---|---|---|---|
| `correct` (`git log -1 <run base>..HEAD -- plans/$job/reports/phase-*-corrector.md`) | ok | ok | ok |
| `added_only` (`--diff-filter=A`) | RED | ok | ok |
| `oldest_in_range` | RED | ok | ok |
| `whole_history_oldest` | RED | RED | ok |
| `whole_history_latest` | ok | RED | ok |
| `subject_match` (`Phase N boundary`) | RED | ok | ok |
| `subject_boundary` (`--grep=boundary`) | RED | RED | ok |
| `subject_then_path` | RED | ok | ok |
| `subject_or_path` (union, latest) | RED | ok | ok |
| `job_ignored` (`plans/*/`) | RED | RED | ok |
| `job_prefix` (`plans/$job*/`) | RED | RED | ok |
| `parent_of_boundary` (off by one) | RED | ok | ok |
| `phase1_literal` | ok | ok | ok |

Removing each decoy of the revised fixture in turn, these variants turn
green:

- **First boundary:** `added_only`, `oldest_in_range` and
  `whole_history_oldest`.
- **Subject decoy:** `subject_then_path` and `subject_or_path`.
- **Other job's report:** `job_ignored` and `job_prefix`.

So every decoy now catches its own wrong implementation. The re-committed
report is load-bearing for the first group. `f.txt` in the base commit is
what catches `parent_of_boundary`.

The four decoys the brief names:

- **Subject-only "Phase 2 boundary" commit:** it was weak, as Major 1
  describes, and is fixed.
- **Re-committed corrector report:** it catches `added_only` and both
  oldest-first variants.
- **Another job's phase report:** it catches `job_ignored` and
  `job_prefix`.
- **Pre-run phase report:** it caught nothing here and was removed (Minor 1).
  The range is pinned by the slice-1 test, where the same decoy is
  load-bearing.

## Check 3 — line cap

`ruff check`, `ruff format --check` and `docformatter -c` pass on all three
files. `scripts/check_line_limits.sh` exits 0, and no `tests/` file is
flagged. The three files hold 82, 172 and 144 lines, all inside the
200–300-line sweet stop or below it. The phase module has room for slice 3.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Item 1.4/2: one boundary landed, so the base is that boundary commit and only later files are listed | Satisfied (test red, awaiting GREEN) | `test_changed_files_phase.py::test_phase_base_is_latest_boundary_commit` |
| KD-2/KD-8: keyed on path, never on subject | Pinned | the subject variants red |
| KD-2: `-1` takes the latest commit, and a modified report counts | Pinned | `added_only` and `oldest_in_range` red |
| Without `--phase` nothing changes | Pinned | bare-call assertion in the same repo |

## Positive Observations

- The exact-list assertions leave a mutation nowhere to hide. Each wrong
  variant reds on the first mismatching line.
- The bare call and the `--phase` call share one repo, so an implementation
  that leaks `--phase` into the default path is caught.
- The RED report's decision to keep the guard as its own red-neutral test
  holds up: folded into the main test, it would have masked the main test's
  red.

## Recommendations

- **The `phase-*` glob is pinned nowhere in the suite.** `phase1_literal`,
  which hard-codes `phase-1-corrector.md`, passes every test. That is
  because every boundary report of `j` in the fixtures is phase 1, the
  "parallel values all equal" shape. Pinning the glob needs boundaries for
  two phase numbers, which is outside slice 2's "one boundary landed"
  scenario. A `j` `phase-2-corrector.md` commit as the latest boundary in
  slice 3's fixture would pin it. This is the orchestrator's call.
- **Two planning texts now point at the wrong module.** Outline Item 1.4
  says the tests go in `tests/test_changed_files.py`, but the `--phase`
  tests now live in `tests/test_changed_files_phase.py`, and slice 3's test
  belongs there. The RED report describes the pre-fix fixture: the pre-run
  decoy, the decoy before the base, and 368 lines. Both are planning
  artifacts outside this review, so I left them unedited.
- **Tree state observed:** `.claude/handoff-todo.md` is staged (`M `). It
  was not in the session's starting status, and I did not touch it.
