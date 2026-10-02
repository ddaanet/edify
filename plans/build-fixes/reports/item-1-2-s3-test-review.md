# Review: Item 1.2 slice 3 — test review (`test_no_item_report_exits_1`)

**Scope**: `tests/test_changed_files.py::test_no_item_report_exits_1` (uncommitted diff), and the RED report `plans/build-fixes/reports/item-1-2-s3-red.md`. Out of scope: `changed-files.sh` (I mutated it temporarily for verification and restored it; `git diff --quiet` on it is clean). Also out: Item 1.3 onward.
**Date**: 2026-10-02
**Mode**: review + fix (TDD test review)

## Summary

The test reds on an assertion against the unchanged SUT. Three of its decoys work: the committed planning reports, the other job's committed report and the uncommitted on-disk report. Each one reds its own wrong derivation. The test did not separate `NO-BASE:` (exit 1) from a git-failure `ERROR:` (exit 2). The smallest plausible GREEN would have passed it: rewrite the SUT's existing parent-lookup failure branch to print `NO-BASE:` and exit 1. That branch is reached both when no report is committed and when the report sits in a root commit. I added a paired exit-2 check that runs first. The job-ignoring decoy also missed a prefix match on the job name. Both are fixed, and the test is still red on its main assertion.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Exit 1 not separated from a git failure**
   - Location: `tests/test_changed_files.py`, `test_no_item_report_exits_1`
   - Problem: The SUT has one failure branch, `git rev-parse --verify --quiet "${first_commit}^"`. Two cases reach it: an empty `first_commit` (no committed report) and a root commit that adds the report (a report exists but has no parent). The interface makes the second a git failure, exit 2 `ERROR:`. The SUT's comment says the same: "A root commit has no parent: an error, never a fallback base." A GREEN that edits that one branch to `echo "NO-BASE: …"; exit 1` passed every assertion in the original test, and it puts the root-commit case under the wrong exit code. In the dispatcher's words: yes, an implementation that exits 1 on every error passed.
   - Fix: Added a check that runs first. A second repo (`_init_repo(tmp_path / "root-item")`, with the seed commit amended to add `plans/j/reports/item-1-1.md`) must give exit 2 and stdout starting `ERROR:`. It differs from the main fixture in one way only: whether the parent lookup has a commit to work on. It sits ahead of the main assertions so it passes against today's SUT and the RED still lands on the main assertion (`non-vacuous-negatives.md` §Ordering under errexit). The docstring states the pairing.
   - Verified: the forbidden mutant reds the test at line 218, `assert (1, 'NO-BAS') == (2, 'ERROR:')`. Without the pair, that mutant leaves the test green.
   - **Status**: FIXED

### Minor Issues

1. **The other-job decoy did not catch a job-prefix match**
   - Location: same test, `plans/other/reports/item-1-1.md`
   - Problem: The decoy caught a derivation that ignores the job (`plans/*/…`) but not one that prefix-matches it (`plans/$job*/…`, or an unanchored `plans/j` grep), because `other` does not start with `j`. The SUT rejects glob characters in the job name for exactly this sibling-job hazard.
   - Fix: Renamed the decoy job to `jj` (`plans/jj/reports/item-1-1.md`). Both mutants now red it: `plans/*/reports/item-*` → `(0, 'BASE: …')`, and `plans/$job*/reports/item-*` → `(0, 'BASE: …')`.
   - **Status**: FIXED

2. **The prefix assertion was born green behind the exit-code assertion**
   - Location: same test, `assert result.returncode == 1` followed by `assert result.stdout.startswith("NO-BASE:")`
   - Problem: The RED landed on the exit code alone. The `NO-BASE:` prefix assertion never ran red, which is the exit-status-then-wording shape `genuine-red.md` measured. The RED report says as much.
   - Fix: Merged the two into one tuple assertion, `(result.returncode, result.stdout[: len("NO-BASE:")]) == (1, "NO-BASE:")`. Its red is now `assert (2, 'ERROR: c') == (1, 'NO-BASE:')`, which shows both parts. The paired check uses the same form.
   - **Status**: FIXED

3. **The docstring claimed every decoy finds a base**
   - Location: same test, docstring
   - Problem: It said the filesystem-glob derivation "would … find a base". It cannot. An implementation that takes the on-disk file as a run in progress has no history to derive from, and it fails by not printing `NO-BASE:` (the mutant gives `(2, 'ERROR: c')`).
   - Fix: Reworded so the docstring says how each decoy fails.
   - **Status**: FIXED

4. **The last assertion was not `ruff format`-clean**
   - Location: the `assert not any(line.startswith("BASE: ") …)` line, from the RED dispatch
   - Problem: `ruff format --check` flagged the file, though the dispatch's `ruff check` and `docformatter -c` had passed. HEAD's version is format-clean.
   - Fix: Ran `ruff format tests/test_changed_files.py`.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_changed_files.py` `test_no_item_report_exits_1`: a paired root-commit check, exit 2 and `ERROR:`, ahead of the main fixture (Major 1).
- `tests/test_changed_files.py`: the decoy job `other` renamed to `jj` (Minor 1).
- `tests/test_changed_files.py`: the exit code and prefix merged into one tuple assertion, in both checks, with the message carrying stdout and stderr like the module's other exit-code assertions (Minor 2).
- `tests/test_changed_files.py`: docstring rewritten to give each decoy's actual failure mode and the exit-1/exit-2 pairing (Minor 3, Major 1).
- `tests/test_changed_files.py`: `ruff format` (Minor 4).

## Check results

**1. Mechanical.** Before the fixes, the test FAILED at `assert result.returncode == 1`: `assert 2 == 1`, stdout `ERROR: cannot resolve the parent of first item report commit ""`. That is an assertion, not an ERROR, and it matches the RED report. After the fixes it FAILED at line 238: `assert (2, 'ERROR: c') == (1, 'NO-BASE:')`. The paired check at line 218 passed against today's SUT, which is correct. The other two tests in the module PASSED.

**2. Wrong-reason hunting.** The state that fails the test once it is implemented: any `BASE:` output or any exit other than 1 for this fixture, or anything other than exit 2 `ERROR:` for the root-commit repo. Each mutant below was an in-place edit to `changed-files.sh`, reverted by the inverse replacement. Each landing was confirmed by grep, and so was the restore (`git diff --quiet`, plus a grep for the mutation marker that came back 0).

| SUT variant | `test_no_item_report_exits_1` |
|---|---|
| Correct shape: `[[ -z $first_commit ]]` → `NO-BASE:` exit 1 | PASSED (all 3 tests pass, so the test can go green) |
| + unscoped job, `plans/*/reports/item-*` | FAILED `(0, 'BASE: f9') == (1, 'NO-BASE:')` |
| + job prefix, `plans/$job*/reports/item-*` | FAILED `(0, 'BASE: e7') == (1, 'NO-BASE:')` |
| + any report, `plans/$job/reports/*` | FAILED `(0, 'BASE: b8') == (1, 'NO-BASE:')` |
| `NO-BASE:` keyed on a filesystem glob (`compgen -G`) | FAILED `(2, 'ERROR: c') == (1, 'NO-BASE:')` |
| Parent-lookup failure → `NO-BASE:` exit 1, no empty check | FAILED at line 218, `(1, 'NO-BAS') == (2, 'ERROR:')` |

The trailing `assert not any(line.startswith("BASE: ") …)` is a negative. The `BASE: ` line it rules out is pinned positively by slice 1's test, and it uses `"BASE: "` with the trailing space, so a `NO-BASE:` line does not satisfy it. I kept it.

**3. Lint.** `ruff check`: all checks passed. `docformatter -c`: exit 0. `ruff format --check`: clean after the fix.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Slice 3: with no committed `item-*` report, exit 1 and stdout starting `NO-BASE:` | Satisfied | main assertion, line 238 |
| Interface: exit 1 is `NO-BASE:`, exit 2 is `ERROR:` on git failure | Satisfied for the parent-lookup site | paired check, line 218 |
| KD-1: `item-*` scope, job scope, committed history only | Satisfied | the four decoy mutants in the table |

## Positive Observations

- The RED report rejected `"BASE:" not in stdout` as a substring trap and kept the anchored `startswith("BASE: ")`.
- The RED report declined to pin the exact `NO-BASE:` output beyond what the interface promises.
- All three original decoys discriminate. Each reds its own mutant.

## Recommendations

- The interface's exit-2 contract is pinned only at the parent-lookup site, by this test's pair. Usage errors (no argument, or a job name with glob characters) and a failure at `git rev-parse --show-toplevel` or `git log` are pinned by no slice of Item 1.2. An `ERROR:`-path regression there would go unnoticed. This belongs to the orchestrator as a possible added slice. Applying it is outside this test's scope.
