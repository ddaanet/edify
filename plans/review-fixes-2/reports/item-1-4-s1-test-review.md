# Review: Item 1.4 slice 1 — test review (tdd-slice step (b))

**Scope**: the uncommitted `test_unloadable_exempt_paths_is_an_error_not_no_base`
in `tests/test_changed_files.py`, plus the RED report
`plans/review-fixes-2/reports/item-1-4-s1-red.md`. `changed-files.sh` was
touched only for mutation reproduction and restored each time.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The test does what the item says. It copies `changed-files.sh` into
`tmp_path/scripts` next to a doctored `exempt-paths.sh` (absent, or present
but defining nothing), runs the copy as `j` in a repo with a committed item
report, and asserts three things: exit 2, the exact ERROR line, and no
`NO-BASE:`. I mutated the script three different ways, one per assertion,
and each mutation turned the test red on that assertion alone. So none of
the three assertions is vacuous. Two minor issues are fixed: duplicated run
plumbing, and unreadable parametrize ids.

**Overall Assessment**: Ready

## Mechanical check

**Against the script as it stands:** 2/2 passed. Both changed-files modules
also pass: 12/12 across `test_changed_files.py` and
`test_changed_files_phase.py`.

**RED's `Mutation proof` covers each named case.** It reds both on
`returncode == 2` (`assert 1 == 2`). I reproduced it with my own mutations,
which differ from the RED's bare `source`. Each was an exact replacement of a
string that occurs once. After each one I restored the file by applying the
inverse replacement, then proved the restore: a grep for the mutant text
found nothing, and `git diff --exit-code -- plugin/skills/build/scripts/changed-files.sh`
exited 0.

| Mutation | Effect | absent | defines-nothing |
|---|---|---|---|
| M1: the guard's message `cannot load` → `cannot read` (still exits 2) | pins the ERROR-line assertion | red on the ERROR-line `in splitlines()` assert | red on the ERROR-line assert |
| M2: the guard echoes `NO-BASE: mutant` before the ERROR line (still exits 2, ERROR line still present) | pins the `NO-BASE:` negative | red on `"NO-BASE:" not in stdout` | red on `"NO-BASE:" not in stdout` |
| M3: drop `\|\| [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]` from the guard | shows each case covers its own half of the guard | passes (the source fails, so the guard still fires) | red on `returncode == 2` (`assert 1 == 2`, `EXEMPT_PATHS_ALTERNATION: unbound variable`) |

M3 is a deliberate one-case red: only the defines-nothing case catches a
guard that keeps the `source` check and drops the `-z` check. That is why
the outline names two cases.

## Wrong-reason hunting

- **Does a mutant that exits 2 with a different message pass?** No. M1
  shows the full-line `in result.stdout.splitlines()` membership check reds.
  The message occurs once in the script, so no other `exit 2` path can
  supply it.
- **Does a mutant that prints `NO-BASE:` pass?** No. M2 keeps exit 2 and the
  ERROR line, and the test reds on the negative alone. The negative is not
  bare: the same fixture also asserts the positive (exit 2 plus the ERROR
  line).
- **Does it really run the copy beside the doctored file?** Yes. In
  `changed-files.sh`, `script_dir` comes from `BASH_SOURCE[0]`, which is the
  copy's absolute path. The M1 output for the absent case names
  `.../test_unloadable_exempt_paths_i0/scripts/exempt-paths.sh` as the file
  it tried to source. A script that found `exempt-paths.sh` anywhere else
  would load the real one, exit 0, and red the test. `shutil.copy2` keeps the
  exec bit.
- **Satisfied by birth state / fallback:** not present. The committed
  `plans/j/reports/item-1-1.md` means a script that tolerated the load
  failure and carried on would print `BASE:` and exit 0. That fails the
  returncode assertion.
- **The right exception from the wrong guard:** not present. The two upstream
  `exit 2` paths are usage and job-name validation, and the arguments
  (`j`, one argument) pass both. M1 shows the line comes from the load guard.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Duplicated script-run plumbing**
   - Location: `tests/test_changed_files.py` (the new test's `env` setup and
     `subprocess.run` call)
   - Note: these lines repeated `_run_script`'s git-config insulation and
     `subprocess.run` call word for word. The only reason was that the helper
     hard-codes `SCRIPT`. They also pulled `os` and `subprocess` imports into
     the module just for this test.
   - **Status**: FIXED. `_run_script` in `tests/changed_files_helpers.py` takes
     a keyword `script: Path = SCRIPT`. The test calls
     `_run_script(repo, "j", script=scripts / SCRIPT.name)`, and the `os` and
     `subprocess` imports are gone. Existing callers are unchanged (the
     default applies).

2. **Unreadable parametrize ids**
   - Location: `tests/test_changed_files.py`, `@pytest.mark.parametrize`
   - Note: the ids were `[None]` and `[# defines nothing\n]`. The second
     contains `#`, spaces and an escaped newline, which makes it awkward to
     select by node id. The repo convention is `pytest.param(..., id=...)`
     (`tests/test_review_range_no_prior.py`).
   - **Status**: FIXED. The ids are now `absent` and `defines-nothing`. The
     docstring's `(``None``)` aside is gone with them. The RED report records
     the old ids: `[None]` = `[absent]`, `[# defines nothing\n]` =
     `[defines-nothing]`. I left it unchanged because it is a historical
     record.

## Fixes Applied

- `tests/changed_files_helpers.py` `_run_script`: added the keyword
  `script: Path = SCRIPT` and a docstring line saying why. This test helper
  is outside the dispatch's literal IN list. It is shared with
  `test_changed_files_phase.py`, where all tests still pass. **The GREEN
  commit must stage it along with `tests/test_changed_files.py`.**
- `tests/test_changed_files.py`: dropped the `os` and `subprocess` imports,
  switched the test to `_run_script(..., script=...)`, changed the ids to
  `pytest.param(..., id=...)`, and rewrapped the docstring. The module is now
  312 lines (under the 400 cap).

## Post-fix verification

- Real script: 2/2 passed. Both changed-files modules: 12/12. `just lint`
  OK.
- Red under mutation after the fix: I applied the RED's bare `source`
  replacement again, so that both cases go through the new helper path. Both
  red on `returncode == 2` (`assert 1 == 2`). I restored it by the inverse
  replacement. A grep for the bare `^source "$script_dir/exempt-paths.sh"$`
  line found nothing, `git diff --exit-code -- plugin/skills/build/scripts/changed-files.sh`
  exited 0, and the slice test passes 2/2 again.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m23 (load guard untested in `changed-files.sh`) | Satisfied (this slice) | The test pins exit 2, the exact ERROR line and no `NO-BASE:` for both doctored states. Each assertion is red-proven by M1, M2 and the bare-source mutation. |
| Item 1.4: run the copy beside a doctored `exempt-paths.sh` | Satisfied | `shutil.copy2` into `tmp_path/scripts`, run by absolute path. The absent case's output names the tmp `exempt-paths.sh`. |

The `verify-step.sh` half of m23 is slice 2 and out of scope.

## Positive Observations

- The ERROR assertion matches a whole line, not a substring, so a longer
  line containing the message would not satisfy it.
- The committed item report makes "carried on" observable: exit 0 with
  `BASE:`, which is distinct from the guard's exit 2.
- The two cases map onto the guard's two halves, `source` failure and
  `-z`, as M3 shows.
