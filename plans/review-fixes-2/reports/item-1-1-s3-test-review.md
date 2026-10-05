# Review: Item 1.1 slice 3 — test review (review-fixes-2)

**Scope**: uncommitted change to `tests/test_triage_feedback.py`
(`test_behavioral_code_reads_the_lists_paths_only`) and
`reports/item-1-1-s3-red.md`. SUT `plugin/bin/triage-feedback.sh` read-only.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The RED is genuine: the new test fails on `assert "- Behavioral code: no"`
(stdout `Behavioral code: yes`, from the whole-range diff reading
`inbox/x.md`'s `def`), and the other 9 tests pass. Two mutants survived the
fixture as written: an empty-list short-circuit that otherwise diffs the list
plus the job's reports, and non-literal (glob) pathspecs. Both are now killed
by fixture changes; the slice's named assertions are unchanged.

**Overall Assessment**: Ready

## Mutant probe

The SUT stayed untouched. A scratch script built each fixture with the
module's helpers, took the list from the real `changed-files.sh`, and ran the
definition regex over `git diff --no-color --no-ext-diff --no-renames <base>
HEAD` limited each way. `yes` means the leg's `no` assertion reds.

| Diff the mutant runs | leg 1 (empty list) | non-empty repo | `*.md` repo |
|---|---|---|---|
| whole range | yes | yes | yes |
| list, glob pathspecs | n/a | no | **yes** |
| list, `:(literal)` (correct) | n/a | no | no |
| list + `plans/<job>/` | yes (class line) | **yes** (after fix) | yes |
| range minus `plans/<job>/`, exempt kept | yes | yes | yes |

The `class with an explicit whitelist` line matches `definition_re`:
`+class with…` hits `^\+[[:space:]]*` then `class[[:space:]]`. In leg 1 it is
the only definition under `plans/<job>/`, so it alone reds the
"list + job reports" mutant.

## Issues Found

### Major Issues

1. **Empty-list short-circuit plus job-report inclusion survived**
   - Location: `tests/test_triage_feedback.py`, non-empty repo leg
   - Problem: the `class` report line sat only in leg 1, whose list is empty.
     An implementation that returns `no` on an empty list without diffing,
     and otherwise diffs the list plus `plans/<job>/reports/`, passed every
     leg: the non-empty repo's `item-1-1.md` held `item report` alone.
   - Fix: the non-empty repo's `item-1-1.md` carries the same
     `class with an explicit whitelist` line, so that mutant reads `yes`
     there.
   - **Status**: FIXED

2. **Literal pathspecs unpinned**
   - Location: `tests/test_triage_feedback.py`, new third repo
   - Problem: KD-1 requires the list's paths as literal pathspecs; no slice
     (including 1.1/5, whose odd name is a tracked `HEAD`) asserts it. Every
     list path in the test held no glob characters, so plain `-- <paths>`
     passed.
   - Fix: a third repo (`glob-name`) commits a file named `*.md` holding
     `plain` beside `inbox/x.md` holding `def foo():`. The list is `*.md`
     (`Files changed: 1`); as a glob pathspec it matches `inbox/x.md` (git's
     default `*` crosses `/`) and reads `yes`, while `:(literal)*.md` reads
     `no`. Asserts `- Files changed: 1` and `- Behavioral code: no`.
   - **Status**: FIXED

### Minor Issues

1. **Docstring did not name the added discriminations**
   - Location: test docstring
   - Fix: names the report line in the second repo and the literal-pathspec
     repo.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_triage_feedback.py` — non-empty repo's item report gains the
  `class` line; third repo `glob-name` with a `*.md` list path; docstring
  extended. Module 356 → 375 lines, under 400, no split.

## Verification

- `pytest tests/test_triage_feedback.py`: 9/10 passed, 1 failed.
  `test_behavioral_code_reads_the_lists_paths_only` FAILED at line 348,
  `assert "- Behavioral code: no" in lines`, stdout
  `Files changed: 0 / Reports: 0 / Behavioral code: yes` — an assertion,
  not an error.
- Legs 2–4 are not reached in the red run (leg 1 stops the test); the probe
  table is their evidence, including that the correct `:(literal)` form
  reads `no` in both later repos, so GREEN can pass them.
- `ruff check` and `ruff format --check` clean.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Slice 3: item report with `class…` line + `inbox/x.md` `def` → `no` | Satisfied | leg 1 |
| Slice 3: further `a.py` `def` → `yes` | Satisfied | leg 2 |
| KD-1: empty list reads `no`, runs no diff | Satisfied | leg 1 + non-empty repo |
| KD-1: limited to exactly the list's paths | Satisfied | non-empty repo |
| KD-1: literal pathspecs | Satisfied | `glob-name` repo |
| KD-1: newline-path residual bound comment | Out of test scope | code review checks the comment |

## Positive Observations

- The RED already added the non-empty repo to rule out the empty-list
  special case, and pins `Files changed: 0` before the `no` assertion, so the
  empty list is a checked precondition rather than an assumption.
- Leg 1 carries two independent definition sources (job report, exempt path),
  so mutants that drop only one of the two exclusions each red.
