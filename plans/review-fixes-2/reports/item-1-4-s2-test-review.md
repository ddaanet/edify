# Review: Item 1.4 slice 2 — test review (tdd-slice step (b))

**Scope**: the uncommitted `test_unloadable_exempt_paths_is_an_error_not_dirty`
in `tests/test_verify_step.py`, the `script` keyword added to `_run_script` in
`tests/verify_step_helpers.py`, and the RED report
`plans/review-fixes-2/reports/item-1-4-s2-red.md`. `verify-step.sh` was
touched only for mutation reproduction and restored after each mutation.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The test copies `verify-step.sh` into `tmp_path/scripts` next to a doctored
`exempt-paths.sh` (absent, or present and defining nothing). It runs the copy
in a repo that holds an untracked `dirt.txt` and asserts four things: exit 2,
the exact ERROR line, no `DIRTY:`, and that `just` was never invoked. I ran
four mutations of my own, each different from the RED's bare `source`. Each
of the three asserted properties reds under a mutation that leaves the other
two intact, so none of the assertions is vacuous. The helper change keeps
every existing caller green. One minor issue was fixed: the helper docstring.

**Overall Assessment**: Ready

## Mechanical check

**Against the script as it stands:** both modules pass, 11/11
(`test_verify_step.py` and `test_verify_step_exemption.py`). Both cases of
the new test pass.

**The RED's `Mutation proof` covers both named cases.** It reds each on
`returncode == 2` with `assert 1 == 2`. I reproduced it with my own
mutations. Each was an exact replacement of a string that occurs exactly
once, checked by a count assertion before writing. After each one I restored
the file with the inverse replacement and proved the restore: a grep for the
mutant text returned 0, and
`git diff --exit-code -- plugin/skills/build/scripts/verify-step.sh` exited 0.

| Mutation | What it pins | absent | defines-nothing |
|---|---|---|---|
| M1: the guard's message changed from `cannot load` to `cannot read`; still exits 2 | the ERROR-line assertion | red on `... in result.stdout.splitlines()` | red on the same assertion |
| M2: the guard echoes `DIRTY: mutant` before the ERROR line; still exits 2 and still prints the ERROR line | the no-`DIRTY:` negative | red on `"DIRTY:" not in result.stdout` | red on the same assertion |
| M3: drop `\|\| [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]` from the guard | each case covers its own half of the guard | passes, because the `source` failure still fires the guard | red on `assert 1 == 2`, with `line 39: EXEMPT_PATHS_ALTERNATION: unbound variable` |
| M4: the guard's `exit 2` changed to `exit 3`; still prints the ERROR line | the returncode assertion, independently of the bare-source exit 1 | red on `assert 3 == 2` | red on `assert 3 == 2` |

M3 reds only one case, and that is intended. It shows that the
defines-nothing case alone catches a guard that kept the `source` check but
lost the `-z` check, which is why the outline names two cases.

## Wrong-reason hunting

- **Exit 2 is pinned.** M4 keeps the ERROR line and the absence of `DIRTY:`,
  and changes only the code. Both cases red on the returncode. The RED's
  bare `source` covers the exit-1 direction.
- **The ERROR line is pinned.** M1 keeps exit 2, and the whole-line
  `in splitlines()` check reds. The message appears once in the script,
  and none of its other `exit 2` paths (`git status failed`,
  `filtering git status failed`, `just not found`) can produce it.
- **The absence of `DIRTY:` is pinned, and the check is not a bare
  negative.** M2 keeps exit 2 and the ERROR line, and the test reds on the
  negative alone. The same fixture also asserts the positive: exit 2 plus
  the ERROR line.
- **The test runs the copy beside the doctored file.** `script_dir` comes
  from `BASH_SOURCE[0]`, which is the absolute path of the copy. Under M1,
  the absent case's output names
  `.../test_unloadable_exempt_paths_i0/scripts/exempt-paths.sh` as the file
  the script tried to source. If the script resolved `exempt-paths.sh`
  anywhere else, it would load the real file, carry on to `DIRTY:` because
  of `dirt.txt`, and red the test. `shutil.copy2` keeps the exec bit.
- **No assertion is satisfied by the fixture's starting state.** The
  untracked `dirt.txt` means a script that tolerated the load failure, for
  example by falling back to a default alternation, would print `DIRTY:` and
  exit 1. It would not pass by exiting 0. The `just` marker would also catch
  a carry-on that reached precommit.
- **The ERROR line does not come from a different guard.** The guard is the
  first thing the script does after resolving `script_dir`, so no earlier
  check can exit 2 first.
- **Helper change and existing callers.** The new parameter is keyword-only,
  `script: Path = SCRIPT`. Only two modules import `verify_step_helpers`:
  `tests/test_verify_step.py` and `tests/test_verify_step_exemption.py`.
  `changed_files_helpers.py` mentions it only in a docstring. Every existing
  call passes no `script`, so it gets the default, and 11/11 pass.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Helper docstring stranded a paragraph and diverged from its sister
   helper**
   - Location: `tests/verify_step_helpers.py`, `_run_script` docstring
   - Note: the docstring had a one-line paragraph, "``script`` is invoked by
     absolute path.". It did not say why the parameter exists. Slice 1's
     identical change to `tests/changed_files_helpers.py::_run_script`
     already words this as "Run ``script`` by absolute path with CWD at
     ``repo``" followed by the default and its purpose. The two helpers
     should read the same way.
   - **Status**: FIXED. The docstring now uses the sister helper's wording,
     naming the `verify-step.sh` default and the doctored-`exempt-paths.sh`
     use.

## Fixes Applied

- `tests/verify_step_helpers.py` `_run_script` docstring: now matches
  `changed_files_helpers._run_script`. The module is 113 lines.
  `tests/test_verify_step.py` is unchanged at 134 lines, under the 400 cap.

## Post-fix verification

- Real script: 11/11 passed across both verify-step modules. `just lint`
  OK.
- Red under mutation after the fix: I applied the RED's own bare-`source`
  replacement again, so both cases ran through the post-fix helper. Both
  red on `returncode == 2`:
  - `[absent]`: `assert 1 == 2`, with `line 18: .../scripts/exempt-paths.sh: No such file or directory`
  - `[defines-nothing]`: `assert 1 == 2`, with `line 36: EXEMPT_PATHS_ALTERNATION: unbound variable`

  I restored the file with the inverse replacement. `grep -cx` for the bare
  `source "$script_dir/exempt-paths.sh"` line returned 0, and
  `git diff --exit-code -- plugin/skills/build/scripts/verify-step.sh`
  exited 0.
- No tool call was denied while the script was mutated.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m23 (load guard untested in `verify-step.sh`) | Satisfied (this slice) | Pins exit 2, the exact ERROR line and no `DIRTY:` for both doctored states. Each is red-proven by M4, M1 and M2 respectively, and by the RED's bare-source mutation. |
| Item 1.4: run the copy beside a doctored `exempt-paths.sh` | Satisfied | `shutil.copy2` into `tmp_path/scripts`, run by absolute path. The absent case's output names the `exempt-paths.sh` in the tmp directory. |

## Positive Observations

- The untracked `dirt.txt` makes "carried on" observable as `DIRTY:` with
  exit 1, which differs from the guard's exit 2 on two axes. Without it, a
  carry-on would exit 0 through the stub `just`.
- The helper extension follows slice 1's committed pattern exactly: a
  keyword-only `script` defaulting to `SCRIPT`. It does not duplicate the
  env and subprocess plumbing inside the test.
- The ids, `absent` and `defines-nothing`, follow the `pytest.param(..., id=...)`
  convention that slice 1's review settled on.

## Note for the GREEN commit

The GREEN commit must stage this report together with `tests/test_verify_step.py`,
`tests/verify_step_helpers.py` and the RED report.
