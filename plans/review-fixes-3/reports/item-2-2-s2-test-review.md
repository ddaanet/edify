# Review: Item 2.2 slice 2 test review

**Scope**: Uncommitted test changes in `tests/test_triage_feedback.py`,
`tests/test_triage_feedback_failures.py`, `tests/triage_feedback_helpers.py`,
and `plans/review-fixes-3/reports/item-2-2-s2-red.md`. The SUT
`plugin/bin/triage-feedback.sh` was used only for in-place mutation runs, each
restored.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

Both slice tests pass the mechanical check. The outside-work-tree test fails
on its assertion against the unchanged script. The CDPATH test's mutation proof
reproduces with a different mutation. One major finding: `CDPATH=.` names the
same directory the script is already in, so the fixture could see only the
print and never the move. A `cd` that silenced the print and still honoured
CDPATH stayed green. A decoy `CDPATH` fixes it. Two minor findings are also
fixed.

**Overall Assessment**: Ready

## Mechanical first check

- `test_outside_a_work_tree_is_one_error_line` FAILED on its assertion against
  the unchanged script:
  `assert len(lines) == 1` with `0 == 1`. Stdout is empty, and stderr carries
  git's `fatal: not a git repository (or any of the parent directories)`.
- `test_cdpath_does_not_move_the_script_dir` passes against the unchanged script
  and carries a mutation proof (`unset CDPATH` -> `: inert`).
- My own mutation, different from the RED's: I swapped the two lines so
  `unset CDPATH` runs after `script_dir=$(cd "$script_dir" && pwd)`. That is the
  right command in the wrong order. The test redded on its own assertion
  (`assert "- Files changed: 1" in lines`). The capture held the printed
  destination, and the run ended with `ERROR: changed-files.sh exited 127`.
- I restored the line order by applying the swap again in reverse.
  `git diff --exit-code -- plugin/bin/triage-feedback.sh` came back empty, and
  `unset CDPATH` is line 20, directly above the `cd` on line 21.
- After the fixes below I re-ran the same mutation against the stronger
  fixture. The test redded again on the same assertion, now through the decoy
  (`.../decoy/plugin/bin/../skills/build/scripts/changed-files.sh: No such file
  or directory`). The restore was verified the same way.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`CDPATH=.` cannot detect a move, only a print**
   - Location: `tests/test_triage_feedback.py`,
     `test_cdpath_does_not_move_the_script_dir`
   - Problem: `CDPATH=.` resolves `plugin/bin` to the directory `cd` would
     reach anyway. The only thing the fixture can see is bash printing the
     destination. I tried this mutation:
     `unset CDPATH` + `script_dir=$(cd "$script_dir" && pwd)` ->
     `script_dir=$(cd "$script_dir" >/dev/null && pwd)`. It silences the print
     and still honours CDPATH, and the test stayed **green**. A CDPATH naming
     another directory with a `plugin/bin` would send that script to the wrong
     place. The test's name claims "does not move", which the fixture could not
     check.
   - Fix: the fixture now creates a decoy `tmp_path/decoy` outside the repo,
     holding an empty real `plugin/bin`, and sets `CDPATH` to the decoy. A
     honoured CDPATH now moves `script_dir` into the decoy, where
     `../skills/build/scripts/changed-files.sh` does not exist. The docstring
     describes the decoy and says why `.` was not used.
   - Verification:
     - Silenced-`cd` mutant: was green, now red on
       `assert "- Files changed: 1" in lines`, with `ERROR: changed-files.sh
       exited 127` from `.../decoy/plugin/bin/../skills/...`.
     - Restored by the reverse replacement. `command grep -c 'dev/null && pwd'`
       gives 0, and `git diff --exit-code` on the SUT is empty.
     - Reorder mutant: red, as above.
  - The RED's own `unset CDPATH` -> `: inert` mutant, re-run against the decoy:
    red on the same assertion (`.../decoy/plugin/bin` printed into the
    capture). Restored; `command grep -c inert` gives 0, and the SUT diff is
    empty.
     - Unchanged SUT: green. With CDPATH unset, `cd` resolves against the CWD
       and never looks at the decoy.
   - Deviation from the slice text: the slice says `CDPATH=.` in the
     environment. The decoy replaces it, because `.` was shown above to accept
     a wrong implementation. The expected evidence, verdict, row and exit 0 are
     unchanged.
   - **Status**: FIXED

2. **The test checked only part of the evidence the slice expects**
   - Location: `tests/test_triage_feedback.py`,
     `test_cdpath_does_not_move_the_script_dir`
   - Problem: the slice expects "slice 1's evidence": `Files changed: 1`,
     `Reports: 1`, `Behavioral code: yes`. The docstring claims all three, but
     the test asserted only `Files changed`.
   - Fix: added `assert "- Reports: 1" in lines` and
     `assert "- Behavioral code: yes" in lines`.
   - **Status**: FIXED

### Minor Issues

1. **The docstring used a plan-lifecycle ID**
   - Location: `test_cdpath_does_not_move_the_script_dir` docstring
   - Note: it said "what slice 1's run does". Plan item and slice IDs in code
     fall in the same class as the no-`KD-N` rule. It now says "what the
     subdirectory run does".
   - **Status**: FIXED

2. **The `ERROR:` line could have an empty cause**
   - Location: `tests/test_triage_feedback_failures.py`,
     `test_outside_a_work_tree_is_one_error_line`
   - Note: `startswith("ERROR: ")` accepts a bare `ERROR: ` with nothing after
     it. The interface says `ERROR: <cause>`. Added
     `assert lines[0].removeprefix("ERROR: ").strip(), output`. It does not pin
     any particular wording.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_triage_feedback.py`, `test_cdpath_does_not_move_the_script_dir`:
  - docstring rewritten to describe the decoy and why `.` was not used;
  - "slice 1's run" replaced by "the subdirectory run";
  - decoy `tmp_path/decoy/plugin/bin` created (2 lines);
  - `env_extra={"CDPATH": str(decoy)}`;
  - added the `Reports: 1` and `Behavioral code: yes` assertions.
- `tests/test_triage_feedback_failures.py`,
  `test_outside_a_work_tree_is_one_error_line`: added the non-empty-cause
  assertion.
- `tests/triage_feedback_helpers.py`: unchanged by this review.

## Wrong-reason hunt: checked, no finding

- **Really outside a work tree**:
  - The red's own stderr (`fatal: not a git repository`) shows git found no
    repository from `tmp_path/outside`.
  - `GIT_CEILING_DIRECTORIES=tmp_path` stops the search before `tmp_path`, so a
    host whose temp directory sits inside a repository still sees no work
    tree. Git resolves symlinks in ceiling entries unless an empty entry comes
    first, so macOS's `/var` -> `/private/var` is handled.
- **`GIT_DIR`/`GIT_WORK_TREE` leaking in**:
  - No helper in the suite strips them. This is a suite-wide pattern that was
    already there, so it is not raised as a finding.
  - For this test, a leak would only give a false red, never a false green: a
    found repository means evidence lines or another error, not exactly one
    `ERROR:` line.
  - Inside a hook, git sets a relative `GIT_DIR=.git`, which resolves against
    `outside` and finds nothing.
- **"Nothing created under the CWD"**:
  - This is a bare negative the slice asks for. Triage writes the log only
    after `changed-files.sh` succeeds and a classification exists, and neither
    is possible outside a work tree. So the assertion catches only a GREEN that
    creates something (for example `mkdir -p plans/reports`) before the git
    check.
  - The matching positive is
    `test_subdirectory_run_measures_the_repository_root`, which asserts the log
    lands at the root and not under the CWD.
  - Kept as written.
- **`ERROR:` plus stderr while stdout is wrong**:
  - Stdout must be exactly one line starting `ERROR: ` with a non-empty cause.
    A GREEN that sends its line to stderr fails, and so does one that also
    prints `changed-files.sh`'s line.
  - Stderr is deliberately not checked: git's own `fatal:` there is the
    diagnostic the no-stderr-suppression rule wants surfaced.
  - Known gap: outside a repository, `changed-files.sh` prints exactly one
    line, `ERROR: git rev-parse --show-toplevel failed` (probed, exit 2). A
    GREEN that skipped its own check, ran `changed-files.sh` and printed only
    its output without triage's trailer would pass this test. KD-6 says the
    check comes "before `changed-files.sh` runs".
  - Asserting that the line differs from `changed-files.sh`'s would wrongly
    reject a correct GREEN that reuses the same wording, so it is not added.
    The `changed-files.sh exited` negative and the one-line count rule out the
    common shape, where both lines are printed.
- **The untracked `plugin` symlink and the changed-files count**:
  - `changed-files.sh` lists only the committed `<base> HEAD` diff ("never the
    working tree", per its header comment), and the behavioural-code diff is
    committed-only too.
  - The unchanged-SUT run reads `Files changed: 1` with the symlink present.
  - The decoy sits outside `repo`, so it cannot enter any list.
- **The CDPATH run invokes the script as production does**:
  - The relative `plugin/bin/triage-feedback.sh` gives a `BASH_SOURCE` that
    CDPATH acts on.
  - An absolute path would never reach CDPATH, as the RED report notes.

## RED report notes

- The RED report correctly says the outline sentence "Today stdout carries
  `changed-files.sh`'s line and triage's second one" is stale. After slice 1,
  the failing `rev-parse` aborts under `set -e` with empty stdout. This is
  input for the list revision.
- The mutation proof and the restore proof are recorded as required.

## Line budget

- `tests/test_triage_feedback.py`: 392 -> **399** lines, against a hard cap of
  400. No prose was shaved. The hub is now one line under the gate, so the next
  test added to it breaks the build. That is a split signal for the
  orchestrator. Candidate seam: move the two run-location tests
  (`test_subdirectory_run_measures_the_repository_root` and
  `test_cdpath_does_not_move_the_script_dir`) to their own module.
  `REFACTOR-NEEDED: tests/test_triage_feedback.py — at 399/400 after slice 2.2/2; split the run-location tests into a sibling module before the next hub test lands.`
- `tests/test_triage_feedback_failures.py`: 114 -> 115.
- `tests/triage_feedback_helpers.py`: 192, unchanged.
- `ruff format` left both files unchanged, `ruff check` passed, and
  `docformatter -c` exited 0 on all three files. Docstring summaries are 70
  characters or fewer.

## Final test run

`.venv/bin/pytest -p no:markdown_report` over all four triage modules, against
the unchanged SUT:

```
tests/test_triage_feedback.py ............                               [ 46%]
tests/test_triage_feedback_failures.py ..F                               [ 57%]
tests/test_triage_feedback_behavioral.py .....                           [ 76%]
tests/test_triage_feedback_log.py ......                                 [100%]

tests/test_triage_feedback_failures.py:110: in test_outside_a_work_tree_is_one_error_line
    assert len(lines) == 1, output
E   AssertionError: fatal: not a git repository (or any of the parent directories): .git
E   assert 0 == 1
FAILED tests/test_triage_feedback_failures.py::test_outside_a_work_tree_is_one_error_line
1 failed, 25 passed
```

Per test:

- `test_outside_a_work_tree_is_one_error_line`: FAILED on its assertion. This
  is the expected red.
- `test_cdpath_does_not_move_the_script_dir`: PASSED on the unchanged SUT. It
  redded on its assertion under both the reorder mutant and the silenced-`cd`
  mutant, and both were restored.

The final check `git diff --exit-code -- plugin/bin/triage-feedback.sh` came
back empty.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Interface: outside a work tree gives exit 2, one `ERROR: <cause>` line, no row | Pinned | `test_outside_a_work_tree_is_one_error_line` checks the one line, the `ERROR:` prefix, a non-empty cause, no trailer, exit 2, and an empty CWD |
| List revision: an exported CDPATH does not move the script dir | Pinned | `test_cdpath_does_not_move_the_script_dir` with a decoy CDPATH; it reds under three mutants (RED's `: inert`, reorder, silenced `cd`) |

## Positive Observations

- The RED report already explains why the run must use a relative invocation
  (an absolute `BASH_SOURCE` never reaches CDPATH) and why the outside test
  went to the failures module.
- `env_extra` is added to both runners without changing any existing caller.
