# Review: Item 2.2 slice 2 code review

**Scope**: `plugin/bin/triage-feedback.sh`. This covers slice 2's GREEN commit
`923626ea` and all of Item 2.2's script change, `git diff efbe062c~3 HEAD`. The
range was checked with `git log --oneline`: `bc986e6e` (2.2/1 GREEN),
`9fa45f86` (2.2/1 code-review fixes), `efbe062c` (list revision), `923626ea`
(2.2/2). The tests were out of scope and were not edited.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

Item 2.2 resolves the script directory to an absolute path with `CDPATH`
unset. It then reads `git rev-parse --show-toplevel` and changes to the root
before `changed-files.sh` runs. Both new failure arms print one `ERROR:` line
on stdout and exit 2. The bash 3.2 `case (pattern)` fix from 2.2/1 is in place.
Two minor findings were fixed. The first was an `ERROR:` line that named a
diagnosis the guard never checks. The second was a residual-bound comment that
claimed file-wide uniqueness. One refactoring is flagged for the test hub.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **The `rev-parse` error line named a cause the guard does not establish**
   - Location: `plugin/bin/triage-feedback.sh:34`
   - Note: the line was `ERROR: not inside a git work tree`. `rev-parse`
     also fails inside a work tree, and then this diagnosis is wrong. Two
     examples: git's `safe.directory` refusal ("detected dubious ownership"),
     and `git` missing from `PATH` (exit 127). Every other git-failure line in
     this file names the failing command (`ERROR: git diff failed`).
     `changed-files.sh:85` prints `ERROR: git rev-parse --show-toplevel failed`
     for the same call. Git's own stderr, which passes through, carries the
     actual cause. I probed git 2.47.3: inside `.git` and inside a bare repo,
     `rev-parse --show-toplevel` exits 128 with "this operation must be run in
     a work tree". So the failure is a real exit there too, never an empty
     success.
   - Fix: the line now reads `ERROR: git rev-parse --show-toplevel failed`.
     The test pins only the `ERROR: ` prefix and a non-empty cause, so the
     wording is free. The `changed-files.sh exited` negative and the one-line
     count still tell triage's own guard apart from a pass-through of
     `changed-files.sh`'s two-line failure (see the mutation run below).
   - **Status**: FIXED

2. **The residual-bound comment claimed to be the only arm with no test**
   - Location: `plugin/bin/triage-feedback.sh:37-38`
   - Note: the comment said the root `cd` "is the one arm with no test". The
     outline's interface says "the one *new* arm". As a file-wide claim, the
     comment is false today. The `ERROR: sed failed` arm has no test
     (`grep -n "sed failed" tests/test_triage_feedback*.py` finds nothing),
     and Item 2.3 exists to pin it. Adding "new" would make the comment rot
     once the change is no longer new.
   - Fix: it now reads "this `cd` failing after a successful `rev-parse` has
     no test; no input provokes it without fault injection". This states the
     bound and makes no claim of uniqueness.
   - **Status**: FIXED

## Checked, no finding

- **The `ERROR:` line comes before `changed-files.sh`.** The `rev-parse` and
  `cd` guards (lines 31-41) both `exit 2` before the `changed-files.sh` call
  at line 48. The comment at lines 28-30 is accurate.
- **The residual bound is true.** `cd` is a builtin, so a `PATH` shim cannot
  fail it. A root that `rev-parse` just resolved from a CWD inside it is
  searchable, unless a permission change or a race lands between the two
  calls. That is fault injection.
- **The `script_dir` resolution (line 21) is unguarded.** It is a `set -e`
  abort, not an `ERROR:` arm. Bash opened the script through that same
  directory path, so the directory is searchable. A guard would be defensive
  code against a state only fault injection reaches.
- **`unset CDPATH`.** It comes before the only relative `cd`, and the
  comment's reasoning (a move, and a print into the capture) matches
  `shell-gotchas`. Because the variable is exported-then-unset,
  `changed-files.sh` inherits no `CDPATH` either.
- **Error wording.** `ERROR: cannot change to $repo_root` matches the file's
  `cannot <verb> <path>` lines. The `echo` with a path is the file's existing
  pattern.
- **Stderr.** There is no `2>/dev/null` in the change. Git's `fatal:` from
  `rev-parse` and `cd`'s own message both reach stderr.
- **Decision citations.** The comments cite D-88, D-90 and D-91 only. No
  `KD-N` and no plan or slice IDs appear in the script.
- **The `status=0` / `|| status=$?` idiom** follows the `changed-files.sh`
  block below it. Not flagged.
- **Consumer seam.** `finishing.md` §2 already says exit 2 is `ERROR:` "on
  a failure of its own: STOP and report its output". The new arms fit that
  without a prose change. D-90's amendment is Item 4.1, which is out of scope.

## Bash 3.2 and lint

- `/tmp/claude-1000/bash32/bin/bash --version`: `GNU bash, version
  3.2.57(2)-release`.
- `bash -n plugin/bin/triage-feedback.sh` under 3.2: OK, before and after the
  fixes.
- `shellcheck` 0.10.0: clean, before and after.
- `PATH=/tmp/claude-1000/bash32/bin:$PATH .venv/bin/pytest -p no:markdown_report
  tests/test_triage_feedback*.py` after the fixes: 26 passed.

## Mutated-SUT run

- Mutant: the rev-parse guard was replaced by
  `repo_root=$(git rev-parse --show-toplevel) || repo_root=.`. This is the
  implementation KD-6 rules out: no guard of triage's own, with
  `changed-files.sh` left to report.
- `test_outside_a_work_tree_is_one_error_line` went red on its own assertion,
  `assert len(lines) == 1` (`2 == 1`). Stdout was
  `ERROR: git rev-parse --show-toplevel failed` and then
  `ERROR: changed-files.sh exited 2`.
- I restored the original by the inverse replacement.
  `git diff --exit-code -- plugin/bin/triage-feedback.sh` came back empty.
  This was done before the fixes above.

## Gate

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, run in the
foreground after the fixes, printed `Precommit OK`. The test report showed
414/415 passed with 1 xfail, so the tests ran and were not cached. The gate
warned about oversized files that were already over before this change:
`corrector.md` at 682, `outline-corrector.md` at 450 and `design-corrector.md`
at 460. None of them is in scope. Nothing is committed. The tree holds the
script diff (3 lines changed), this report, and the untracked
`inbox/brief-*.md` files, which were left alone.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:34`: the `ERROR:` line now names the failed
  command, as the file and `changed-files.sh` do.
- `plugin/bin/triage-feedback.sh:37-38`: the residual-bound comment no
  longer claims the arm is the file's only untested one.

## Refactoring flagged

`REFACTOR-NEEDED: tests/test_triage_feedback.py — confirmed. It is at 399/400.
Move the two run-location tests into a sibling module, for example
tests/test_triage_feedback_location.py. The tests are
test_subdirectory_run_measures_the_repository_root (line 310) and
test_cdpath_does_not_move_the_script_dir (line 359). The hub's
_run_triage_relative import moves with them, since both callers leave. The hub
docstring should name the new sibling.`

This amends the test review's flag with a second reason for the split. The
hub docstring says the module holds "the files-changed, reports and
classification tests", and it names three siblings. The two run-location tests
fit none of these, so the docstring is already inaccurate. After the split the
hub should be about 310 lines. Neither the split nor the docstring edit was
done here, because the tests are out of scope.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| KD-6: changes to the root before `changed-files.sh`, with the script dir made absolute first | Satisfied | lines 17-41, ahead of line 48 |
| KD-6: a `rev-parse` or `cd` failure exits 2 with one `ERROR:` line, before `changed-files.sh` | Satisfied | lines 31-41; the test and the mutant above |
| Interface: outside a work tree, exit 2, one `ERROR: <cause>` line, no row | Satisfied | `test_outside_a_work_tree_is_one_error_line` passes under bash 5 and bash 3.2 |
| Residual bound stated in a comment | Satisfied | lines 37-38, reworded |
| Bash 3.2 parses and passes | Satisfied | above |

## Positive Observations

- The guard keeps git's stderr and adds stdout's one line. It does not replace
  the diagnostic.
- The `CDPATH` fix has its reasoning inline and is pinned by a decoy-fixture
  test that three mutants turn red.
