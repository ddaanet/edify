# Review: Item 1.4 slice 2 — code review (tdd-slice step (d))

**Scope**: the slice's commit, the one that adds
`plans/review-fixes-2/reports/item-1-4-s2-green.md`, diffed against its
parent. It contains `test_unloadable_exempt_paths_is_an_error_not_dirty` in
`tests/test_verify_step.py` and the keyword-only `script: Path = SCRIPT`
parameter on `_run_script` in `tests/verify_step_helpers.py`. Also in scope:
the load guard in `plugin/skills/build/scripts/verify-step.sh`, which this
slice pins but did not change.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

GREEN made no implementation change: the guard already existed, and the RED
proved the test against it with a mutation. I read the test and the guard
against each other. They agree on the two failure states, the exit code, the
exact ERROR line and the `DIRTY:` contrast. The helper change leaves every
existing caller on its old behaviour. I found nothing to fix.

**Overall Assessment**: Ready

## Test and guard against each other

- **Guard** (`verify-step.sh` lines 17-21):
  `if ! source "$script_dir/exempt-paths.sh" || [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]`,
  which echoes the ERROR line and runs `exit 2`. Each arm has its own case:
  `absent` fires the `! source` arm, and `defines-nothing` fires the `-z`
  arm. The step (b) review's M3 showed that `defines-nothing` alone catches
  a guard missing its `-z` arm.
- **Exit code.** The test asserts 2. The script reserves 1 for `DIRTY:` and
  `PRECOMMIT:`, and its comments name exit 1 as the verdict code that a
  script failure must never use. The comment above the guard says why the
  `-z` arm exists: an unset variable trips `set -u`, and its exit 1 would
  read as DIRTY. The test docstring makes the same argument.
- **ERROR line.** The test asserts the whole line through
  `in result.stdout.splitlines()`. The guard echoes it verbatim. Because of
  `exec 2>&1`, bash's own `No such file or directory` line also reaches
  stdout in the `absent` case. The membership check tolerates that line,
  and it should, since the line is bash's message and not the interface.
- **`script_dir` resolution.** The test runs the copy by absolute path, so
  `BASH_SOURCE[0]` contains `/`, and `script_dir` resolves to
  `tmp_path/scripts`. The mutation output below names
  `.../scripts/exempt-paths.sh` in the tmp directory as the file the copy
  tried to source.
- **Carry-on is observable.** The untracked `dirt.txt` means a script that
  got past the guard would print `DIRTY:`, or die with exit 1 on the unbound
  variable. The stub-`just` marker would catch one that reached precommit.
- **Agreement with slice 1.** The test has the same shape as slice 1's
  `test_unloadable_exempt_paths_is_an_error_not_no_base` in
  `tests/test_changed_files.py`: the same `pytest.param` ids, copy layout,
  ERROR-line assertion and negative on the verdict prefix. This slice adds
  the `just` marker, which suits a script that would go on to run
  precommit.

## Helper change and existing callers

`_run_script(repo, bin_dir, *, extra_env=None, script=SCRIPT)` is
keyword-only with the old value as its default. Every existing call passes
no `script`:

- `tests/test_verify_step.py` lines 34, 62 and 93
- `tests/test_verify_step_exemption.py`, 10 calls

All of them still run the repo's `verify-step.sh`. Calls named
`_run_script` in `tests/test_changed_files*.py` belong to the separate
`changed_files_helpers._run_script` and are untouched. Both verify-step
modules pass, 11/11, through `just test`.

The docstring now matches its sister in `changed_files_helpers.py`, after
the step (b) fix.

## Mutated-SUT run (one)

I chose a mutation the step (b) review did not run: **warn and carry on**.
It drops the guard's `exit 2` and keeps the echo. This is the plausible
wrong implementation that prints the right message but still falls into the
verdict path.

- Applied by exact replacement: a Python `str.replace` with `count == 1`
  asserted. The tests were not relocated.
- `[absent]`: red on `assert result.returncode == 2` with `assert 1 == 2`.
  stdout held the ERROR line, then
  `line 38: EXEMPT_PATHS_ALTERNATION: unbound variable`.
- `[defines-nothing]`: red on the same assertion, with the same output.
- Both tests redded. The returncode assertion carries the case on its own,
  because the ERROR line is present under this mutation.
- Restored by the inverse replacement, with `count == 1` asserted. Proof:
  `grep -A1 'cannot load EXEMPT'` shows `exit 2` back under the echo, and
  `git diff --exit-code -- plugin/skills/build/scripts/verify-step.sh`
  printed nothing and exited 0. After the restore the modules ran 11/11
  green.
- No tool call was denied while the script was mutated.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

I did not re-raise slice 1's unscoped observation that neither guard
clears an inherited `EXEMPT_PATHS_ALTERNATION`. It is already recorded.

## Fixes Applied

None. Nothing was edited, so `just precommit` was not rerun. The GREEN
report records `Precommit OK` for this commit.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m23: the `verify-step.sh` load guard is pinned by a test | Satisfied | `tests/test_verify_step.py::test_unloadable_exempt_paths_is_an_error_not_dirty`, with the cases `absent` and `defines-nothing`. The RED's bare-`source` mutation and this review's carry-on mutation both red. |
| Item 1.4: run a copy beside a doctored `exempt-paths.sh` | Satisfied | `shutil.copy2` into `tmp_path/scripts`, run through `_run_script(..., script=...)` |
| Slice 2: exit 2, that ERROR line, never `DIRTY:` | Satisfied | `tests/test_verify_step.py` lines 128-133 |

## Line caps

- `tests/test_verify_step.py`: 134 lines, cap 400
- `tests/verify_step_helpers.py`: 113 lines, cap 400

## Refactoring signals

None.

## Positive Observations

- The helper extension is the minimum the test needs: one keyword-only
  parameter that defaults to the old behaviour. It mirrors slice 1's change
  to `changed_files_helpers._run_script`.
- The fixture makes each wrong outcome distinguishable. A carry-on shows up
  as exit 1, a `DIRTY:` line, or the `just` marker, and the guard as
  exit 2 plus the ERROR line.
