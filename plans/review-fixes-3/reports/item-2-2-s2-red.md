# Item 2.2 slice 2 RED

## Placement

- `test_cdpath_does_not_move_the_script_dir` is in `tests/test_triage_feedback.py` (356 -> 392 lines).
- `test_outside_a_work_tree_is_one_error_line` is in `tests/test_triage_feedback_failures.py` (89 -> 114 lines), not the hub. Both in the hub would have passed 400. The failures module docstring now names the outside-work-tree run. The hub docstring enumerates no contents that this changes.
- `tests/triage_feedback_helpers.py` (184 -> 192): `_run_triage` and `_run_triage_relative` gain an optional `env_extra` dict, merged into the environment. No existing caller changed.
- The SUT is untouched apart from the mutation below, which is restored. `git diff` on `plugin/bin/triage-feedback.sh` is empty.

## Per-test output

`test_outside_a_work_tree_is_one_error_line` -- FAILED on its assertion against the unchanged script:

```
tests/test_triage_feedback_failures.py:110: in test_outside_a_work_tree_is_one_error_line
    assert len(lines) == 1, output
E   AssertionError: fatal: not a git repository (or any of the parent directories): .git
E   assert 0 == 1
```

Today the failing `git rev-parse --show-toplevel` aborts under `set -e` with git's stderr and empty stdout. The outline's "changed-files.sh's line and triage's second one" no longer describes the script after slice 1. The test's assertions (one `ERROR:` line, exit 2, nothing created) still red.

`test_cdpath_does_not_move_the_script_dir` -- PASSED against the unchanged script (the behaviour exists). Proven by mutation below.

## Mutation proof

Test: `test_cdpath_does_not_move_the_script_dir`.
Strings: `unset CDPATH` (own line 20, occurs once; `command grep -c` gives 1) was replaced by `: inert`. Restored by the swapped replacement.

Mutant run, red on its own assertion:

```
tests/test_triage_feedback.py:388: in test_cdpath_does_not_move_the_script_dir
    assert "- Files changed: 1" in lines, output
E   ERROR: changed-files.sh exited 127
E   plugin/bin/triage-feedback.sh: line 35: .../repo/plugin/bin
E   .../repo/plugin/bin/../skills/build/scripts/changed-files.sh: No such file or directory
```

This is the failure the slice 1 code review reproduced. The fixture does exercise CDPATH: `cd plugin/bin` resolved through `CDPATH=.` and printed its destination into the capture.

Restore proof: `command grep -n inert plugin/bin/triage-feedback.sh` gives no hit, and `git diff --stat plugin/bin/triage-feedback.sh` is empty. Running both modules gives 14 passed and 1 failed, the failure being the expected red `test_outside_a_work_tree_is_one_error_line`.

## Fixtures tried and rejected

- Both tests in the hub: would pass 400 lines, and docstrings must not be shaved. The outside test moved to the failures module.
- `GIT_CEILING_DIRECTORIES` equal to the CWD itself: git does not stop at a ceiling equal to the start directory the same way. The parent (`tmp_path`) is used, as the slice states.
- A CDPATH run through `_run_triage`'s absolute script path: CDPATH applies only to an operand not starting with `/`, `.` or `..`. An absolute `BASH_SOURCE` would never reach `cd` through CDPATH, so the run could not red even under the mutation. The relative `plugin/bin/...` path is required.
