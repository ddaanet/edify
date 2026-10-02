# Review: Item 1.3 slice 1 — test review

**Scope**: `tests/test_triage_feedback.py`, the new
`test_files_changed_counts_committed_changes_only` (uncommitted diff), and the
RED report `plans/build-fixes/reports/item-1-3-s1-red.md`. The SUT
`plugin/bin/triage-feedback.sh`, slice 2 and every other item are out of scope.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The RED report shows a real red: the test failed on its content assertion
(`- Files changed: 3` came back where 1 was expected), not on an error. But with
only one commit after the baseline, the fixture could not tell the KD-6 range
apart from two wrong implementations. Both `git diff --name-only HEAD~1 HEAD`
and plain `git diff --cached --name-only` (index against HEAD) also returned 1.
So did a hardcoded 1. I rebuilt the fixture with two commits after the baseline.
The correct answer is now 3, and no nearby wrong range or constant produces 3.
The test is still red on its assertion.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The fixture cannot tell the baseline range from the last commit or from
   the index**
   - Location: `tests/test_triage_feedback.py`, the new test (fixture and the
     `- Files changed: 1` assertion)
   - Problem: Only one commit followed the baseline, so `HEAD~1..HEAD` is the
     same as `<base>..HEAD`. A GREEN that counted only the last commit would
     pass. The staged-only `c.txt` caused a second problem: `git diff --cached`
     with no ref (index against HEAD) lists exactly one file, so an
     index-based count also gave 1. A hardcoded 1 passed too. Three wrong
     implementations all matched the one expected value.
   - Fix: Added a second commit after the baseline that changes `d.txt` and
     `e.txt`, which are also tracked at the baseline. The expected value is
     now `- Files changed: 3`. I checked each candidate count on a replica of
     the fixture, using `git diff --name-only <range> | wc -l`:

     | Range | Count |
     |---|---|
     | `<base> HEAD` (KD-6, the fix) | 3 |
     | `HEAD~1 HEAD` (last commit only) | 2 |
     | `--cached` (index vs HEAD) | 1 |
     | `HEAD` (working tree vs HEAD) | 2 |
     | `--cached <base>` (baseline vs index) | 4 |
     | `<base>` (current SUT: baseline vs working tree) | 5 |
     | `HEAD~1` (working tree vs last commit's parent) | 4 |

     The correct answer, 3, differs from every other row and from a hardcoded 1.
     Two uncommitted files are needed, not one: with one, the working tree
     against HEAD would equal the committed count.
   - **Status**: FIXED

### Minor Issues

1. **The docstring described the current SUT's bug**
   - Location: the new test's docstring
   - Note: It said "The current script's single-ref ``git diff
     "$baseline_commit"`` … counts all three; the fix diffs baseline against
     HEAD". That stops being true once GREEN lands, and it said nothing about
     why the fixture rules out the other ranges. I rewrote it to say what the
     fixture discriminates: every file is tracked at the baseline (an untracked
     path would drop out for the wrong reason), and the committed answer
     differs from each neighbouring range's count.
   - **Status**: FIXED

## Checks

1. **Mechanical**: the RED report's run shows FAILED on
   `assert "- Files changed: 1" in lines` with the SUT reporting
   `- Files changed: 3`. That is an assertion failure, and `_triage_lines`'s
   exit-0 assert passed first. After the fix, the re-run shows FAILED on
   `assert "- Files changed: 3" in lines`, with the SUT reporting
   `- Files changed: 5`. The pre-existing `test_simple_with_review_reports_matches`
   PASSED.
2. **Wrong-reason hunting**: the test now fails whenever the count is anything
   other than the committed changes from `<base>` to `HEAD`. That covers the
   unfixed SUT (5), last-commit-only (2), index-based (1, 4), working-tree vs
   HEAD (2) and a hardcoded 1. The assertion is exact: `"- Files changed: 3" in
   lines` is a membership test on a list of lines, so it compares whole lines
   and cannot match `- Files changed: 30`. The verdict is `no-classification`,
   so the `Triage:` line, which also carries `files=`, is not printed.
   Residual: hardcoding `HEAD~2` as the base would also give 3. Any linear
   fixture has this property, since its baseline is always `HEAD~N` for some
   fixed N. I left it.
3. **Lint**: `ruff check` passed. `ruff format --check` reported the file
   already formatted. `docformatter -c` exited 0.

## Fixes Applied

- `tests/test_triage_feedback.py`, the new test: tracked `d.txt` and `e.txt` at
  the baseline and added a second post-baseline commit changing both. Changed
  the assertion to `- Files changed: 3` and rewrote the docstring.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m18 / KD-6 (changed-files count is the committed diff since the base) | Satisfied (test pins it) | The new test asserts the count is the `<base> HEAD` committed diff only, with both uncommitted forms (unstaged `b.txt`, staged `c.txt`) excluded, and is red against the unchanged SUT |

The item text says to assert `- Files changed: 1`. The value changed to 3
because the fixture changed, which the dispatch allows.

## Positive Observations

- The RED report rejected an untracked `b.txt` for the right reason (`git diff`
  never lists untracked paths).
- Adding the staged-only `c.txt` makes the test catch a GREEN that handles only
  the unstaged case.
- The test reuses the module's existing `_init_repo` / `_run_git` /
  `_triage_lines` helpers and their config insulation.
