# Review: review-fixes-3, group `review-code` (scripts, tests, plugin README, learnings)

**Scope**: `git diff daad4769e5eb694f151b9972ed51555033d0e1ca HEAD` over the 16
files the dispatch names: `changed-files.sh`, `triage-feedback.sh`, the
changed-files and triage test modules and helpers, `verify_step_helpers.py`,
`test_build_prose_git_log.py`, `plugin/README.md` and `agents/learnings.md`.
Checked against `plans/review-fixes-3/outline.md` (KD-1..KD-7, Items 1.1, 1.2,
2.1–2.4, 3.1, 3.6).
**Date**: 2026-10-08
**Mode**: review + fix

## Summary

The scripts carry KD-4 and KD-6 as designed. `changed-files.sh` captures the
whole list before `BASE:` prints. `triage-feedback.sh` resolves its own
directory, unsets `CDPATH` and changes to the repository root before
`changed-files.sh` runs. Every triage failure arm Item 2.3 names has a test,
and `test_build_prose_git_log.py` runs the prose's own commands against signed
history. Four issues were found, all minor, and all four are fixed:

- the carried docstring nit;
- a helper docstring that states the opposite of the mechanism it documents;
- an unguarded script-directory `cd` that would exit 1, the usage code;
- a path interpolated through `echo`.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **A decision cited as the actor that reads the diff (carried nit)**
   - Location: `tests/test_changed_files.py:214`
   - Note: the line read "D-90 reads the diff NUL-delimited." A decision does
     not read anything. It now reads "The list is read NUL-delimited (D-90)."
     The summary line is unchanged and nothing was shaved.
   - **Status**: FIXED

2. **`_run_triage_relative`'s docstring states the inverse of its mechanism**
   - Location: `tests/triage_feedback_helpers.py`, `_run_triage_relative`
     docstring
   - Note: the docstring said "The relative path to the real script climbs to
     `/`, where surplus `..` are absorbed, so it would resolve from any
     directory of the fixture." That was the defect
     `item-2-2-s1-test-review.md` Major 1 found and fixed. A path that
     resolves from the root as well as from `sub` lets a GREEN that changes
     directory before resolving `script_dir` pass. The fix routes the path
     through the `plugin` link (`../../plugin/bin/…` from `repo/sub`), which
     resolves from `cwd` only. The sentence from before the fix survived it.
     A maintainer who trusts it could "simplify" the helper back to the
     vacuous form. The sentence now says the path runs to the link, stays
     short and resolves from `cwd` alone, and that a path climbing to `/`
     would resolve from the root as well. It is a correction, not a cut.
   - **Status**: FIXED

3. **Unguarded script-directory resolution exits 1, the usage code**
   - Location: `plugin/bin/triage-feedback.sh:21` (as of HEAD)
   - Note: `script_dir=$(cd "$script_dir" && pwd)` sits under `set -e` with
     no guard. If the `cd` or `pwd` fails, the script exits 1 and stdout is
     empty. Exit 1 is the usage error's code. The script keeps that code to
     usage everywhere else ("A failed write would exit 1 under `set -e`, the
     usage error's code"), and `changed-files.sh` guards its own `cd`. The
     line now ends in `|| { echo "ERROR: cannot resolve the script directory";
     exit 2; }`. The residual-bound comment on the root `cd` now covers both
     `cd`s, because no input provokes either one without fault injection.
   - **Status**: FIXED

4. **A path interpolated through `echo`**
   - Location: `plugin/bin/triage-feedback.sh:40` (as of HEAD)
   - Note: `echo "ERROR: cannot change to $repo_root"` puts arbitrary data
     through `echo`. The other error lines that carry data use
     `printf '… %s\n'` (`changed-files.sh` lines 60, 100 and 106), and
     shell-gotchas rule 5 asks for the same. The line is now
     `printf 'ERROR: cannot change to %s\n' "$repo_root"`.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_changed_files.py:214`: "D-90 reads the diff NUL-delimited." →
  "The list is read NUL-delimited (D-90)."
- `tests/triage_feedback_helpers.py` `_run_triage_relative` docstring: the
  stale "climbs to `/` … resolve from any directory" sentence is replaced by an
  accurate statement of why the path goes through the link.
- `plugin/bin/triage-feedback.sh`: `script_dir=$(cd "$script_dir" && pwd)`
  is guarded with `ERROR: cannot resolve the script directory` and exit 2.
  The residual-bound comment covers both `cd`s. The root-`cd` error line uses
  `printf '%s'`.

Verification after the fixes:

- `/tmp/claude-1000/bash32/bin/bash -n` (GNU bash 3.2.57) on both scripts:
  OK.
- `shellcheck -x` 0.10.0 on both scripts: clean.
- `PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`: 431/432
  passed, 1 xfail, Precommit OK. The line-limit lines are the three
  corrector agents, which are out of scope.
- `.venv/bin/pytest -p no:markdown_report` over the nine touched test modules
  (`test_changed_files*.py`, `test_triage_feedback*.py`,
  `test_build_prose_git_log.py`): 59 passed.
- The same changed-files and triage modules with bash 3.2.57 first on `PATH`:
  48 passed, 1 failed. The failure is
  `test_unloadable_exempt_paths_is_an_error_not_no_base[absent]`, the
  standing-ruling `source` defect under bash 3.2, which stays out of this job.
  Nothing else fails under 3.2.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 1.1 (m10): split on the exit-code seam | Satisfied | `tests/test_changed_files_errors.py` holds the four named tests, with bodies unchanged against the baseline hunks. Each module docstring says what it holds and gives the line-cap reason. |
| Item 1.1: no `KD-N`; D-IDs; `Item N.M` rule | Satisfied | `command grep 'KD-[0-9]'` over the changed-files modules and helpers finds nothing. `Item 1.1` at `test_changed_files.py:189` names the fixture's own commit, so it stays. Line 214 is fixed (Minor 1). |
| Item 1.1: collected count unchanged; no shave; summary ≤70 | Satisfied | `item-1-1.md`: 15 before, 15 after. Every summary line over 70 that an AST scan finds is on a line this diff did not touch. |
| Item 1.2 (m7, m8, m9) | Satisfied | The hub docstring names all four siblings (`_location` added by the 2.2/2 refactor), each with what it holds, and gives the line-cap reason. `verify_step_helpers.py:5` points at `triage_feedback_helpers.py`. The log module docstring says the *append* is skipped and the run still prints. `item-1-2.md`: 23 before, 23 after. |
| Item 2.1 (m2, m18, KD-4) | Satisfied | `changed-files.sh:120-143` captures the list, then prints `BASE:` and the paths. The header at lines 37-39 states the order, and lines 26-39 are reflowed to ≤80. `test_late_diff_failure_prints_error_alone` pins stdout as exactly `["ERROR: git diff failed"]`. It parses under bash 3.2. |
| Item 2.2 (m1, KD-6) | Satisfied | `triage-feedback.sh:17-46` covers the absolute `script_dir`, `unset CDPATH`, the `rev-parse` guard, the root `cd` and the residual-bound comment. `test_subdirectory_run_measures_the_repository_root`, `test_outside_a_work_tree_is_one_error_line` and `test_cdpath_does_not_move_the_script_dir` pin them. It parses and passes under bash 3.2. |
| Item 2.3 (m4, m5, m6, KD-5) | Satisfied | Usage: `test_usage_error_exits_1[no-args,stale-base]`. Changed-files error: `test_changed_files_error_is_printed_then_exit_2`. Unreadable classification: `test_unreadable_classification_is_an_error`. Sed: `test_failing_label_sed_is_an_error`. Definition grep: `test_failing_definition_grep_is_an_error_not_no`. Log directory: `test_unwritable_log_is_an_error_not_a_usage_exit[directory]`. |
| Item 2.4 (m14, KD-7) | Satisfied | `tests/test_build_prose_git_log.py` extracts from fenced blocks and inline spans. It cross-checks against the `--format=%H` count (a `:missed` case), fails on leftover placeholders and asserts its own discriminating fixture state. `SCANNED` includes `docs/references/pipeline-contracts.md`. |
| Item 3.1 (m11) | Satisfied | `agents/learnings.md` §"When calling triage-feedback.sh": the job name alone, `plans/<job>` exits 2 with `changed-files.sh`'s exact `not a job name:` line, and the two-argument call exits 1 with `Usage:`. The one-line bullet style is kept. |
| Item 3.6 (C-2) | Satisfied | `plugin/README.md` §Optional plugins names `plugin-dev`, `craft` and `sandbox-lies`. The wording matches `plugin/fragments/review-requirement.md:66-70`, and the `sandbox-lies` entry points at the `verify-step.sh` bullet. |

**Gaps:** none.

## Deferred Items

The following items were identified but are out of scope:

- **The bash 3.2 `source` defect in `changed-files.sh`**: an absent
  `exempt-paths.sh` exits 1 under bash 3.2. It reproduced as the one 3.2
  failure above. Reason: standing ruling, in the dispatch's Scope OUT.

## Positive Observations

- `changed-files.sh` appends `x` on success and strips it, which keeps a last
  path's trailing newline. Line 135 couples it to the pipeline's status, so a
  failed diff can never emit a partial list.
- The `(pattern)` form inside `$(…)` is explained at both sites. It is the
  form bash 3.2 parses, and bash 3.2 was verified here.
- Every Item 2.3 test pins stdout exactly (`== ["ERROR: …"]`). None checks a
  substring that another line could satisfy. The two textually identical
  `grep failed` arms are told apart by stderr (`classification.md`) and by
  the shim's `-qE` trigger.
- The signed-history fixture asserts that every commit is good-signed and
  that a bare `git log -1 --format=%H` prints a non-hash line. Without that
  signature line the test could pass vacuously.
- `_write_shim` embeds the real tool's path with `shlex.quote`, and all
  three shim users share it.

## Recommendations

None beyond the fixes applied.
