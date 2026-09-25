# Review: Item 1.2 / Slice 2 — test review (F-1/F-2 pinning tests)

**Scope**: `tests/test_verify_step.py`, meaning the four new tests and the
`_run_script` `extra_env` change, plus `plans/build-defects/reports/item-1-2-s2-red.md`.
`plugin/skills/build/scripts/verify-step.sh` is OUT and was not edited:
`git status --porcelain -- plugin/skills/build/scripts/verify-step.sh` is
empty.
**Date**: 2026-09-25
**Mode**: review + fix (test review, mutation-red variant)

## Summary

All four tests fail on their own `returncode` assertion against a targeted
mutant of mine, and each of those mutants reds only its own test. The RED
report's `pre-f1.sh` proof reproduces (1 passed, 4 failed). The one
wrong-reason gap was in `test_quoted_exempt_path_is_clean`. It had no
negative case, so a mutant that exempts *every* quoted path passed all five
tests. I added a decoy phase and the mutant now reds. The `extra_env`
change does not affect the slice 1 test.

**Overall Assessment**: Ready

## Mechanical check: mutation reds

Each mutant is a copy of the tracked script under `tmp/mutants/` with one
change, built by an exact-string replacement that asserts `count(old) == 1`.
Each was run as
`MUTANT=tmp/mutants/<f> PYTHONPATH=tmp/mutants pytest -p rebind tests/test_verify_step.py -v`.
`tmp/mutants/current.sh` is byte-identical to the tracked script (`cmp`).

| Mutant | Single change | Named test | Failing assertion | Other four |
|---|---|---|---|---|
| `current.sh` (control) | none | — | — | 5/5 green |
| `m-rc.sh` | `^[^RC][^RC] ` → `^.. ` (quote allowance kept) | rename: **red** | `returncode == 1` (got 0, `CLEAN: …`) | green |
| `m-quote.sh` | drop both `"?` (R/C guard kept) | quoted: **red** | `returncode == 0` (got 1) | green |
| `m-gitstatus.sh` | drop the `\|\| { echo "ERROR: git status failed"; exit 2; }` | git-status: **red** | `returncode == 2` (got 128) | green |
| `m-just.sh` | drop the `command -v just … exit 2` block | missing-just: **red** | `returncode == 2` (got 1, `PRECOMMIT: validation failed`) | green |
| `m-anyquoted.sh` (wrong-reason probe) | path group gains a `"[^"]*"` alternative that exempts any quoted path | quoted: green before fix, **red** after | after fix: decoy phase `returncode == 1` (got 0) | green |
| `pre-f1.sh` (RED report's mutant) | `31fe4a16` script | all four **red** | same four assertions as above | slice 1 test green |

Every red is an `AssertionError` on the test's own assertion. None is an
ERROR, ImportError or AttributeError. The table reflects the final
post-fix test file: the formatter changed only line wrapping after the
mutant runs, so the assertions the mutants hit are unchanged.

## Wrong-reason analysis

- **Rename**: a fixture guard pins the porcelain to
  `R  inbox/a.md -> notes.md\n` exactly. The exact-lines assertion then
  requires that line to be echoed. With the rename guard removed, the same
  fixture goes CLEAN (`m-rc.sh`), so the DIRTY verdict comes from the guard.
  No finding.
- **Quoted**: the fixture guard pins `?? "inbox/my brief.md"`. The test
  asserted only the positive, so an over-broad quote allowance satisfied it
  (Major 1).
- **Git status failure**: the only source of the line
  `ERROR: git status failed` is the `git status` guard, and the test checks
  it as a whole line. A missing `git` would also reach that guard, but that
  is still a `git status` failure, which is the property named. A leaked
  `GIT_DIR` would make `git status` succeed, which gives a false red, not a
  false green. `GIT_CEILING_DIRECTORIES=tmp_path` stops discovery before
  any enclosing checkout. No finding.
- **Missing just**: `PATH` is exactly the symlinked `bash`, `git` and
  `grep`, and a guard asserts that `just` cannot be resolved. If `bash` were
  missing, the exit would be 127. If `git` were missing, stdout would carry
  `ERROR: git status failed`. If `grep` were missing, it would carry
  `ERROR: filtering git status failed`. The `just` message assertion rejects
  all three, so exit 2 cannot pass for the wrong reason. The assertion was
  a substring check, while its sibling test checks whole lines (Minor 1).
- **`_run_script` `extra_env`**: the default is `None` and the update is
  applied last. Slice 1 calls it without `extra_env`, so its environment is
  unchanged (`PATH` prepend and git config insulation). No finding.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Quoted-path test passes with every quoted path exempt**
   - Location: `tests/test_verify_step.py`, `test_quoted_exempt_path_is_clean`
   - Problem: the test is a bare positive. `m-anyquoted.sh` exempts any
     quoted porcelain path, and it passed all five tests. The slice 1 dirty
     phases use only unquoted paths, so nothing covered the direction the
     quote allowance could over-exempt.
   - Suggestion: add a decoy that differs only in the exemption's trigger,
     an untracked `inbox/my notes.txt` (quoted, not `*.md`). Pin the
     porcelain, then assert exit 1 with a DIRTY listing of just that line.
     This also shows the quoted brief stays filtered in a DIRTY listing.
   - **Status**: FIXED. `m-anyquoted.sh` now reds on the decoy phase's
     `returncode == 1`. `m-quote.sh` still reds on the first phase.

### Minor Issues

1. **Missing-just message asserted as a substring**
   - Location: `test_missing_just_exits_2`
   - Note: now checked as a whole line (`in result.stdout.splitlines()`),
     the same way as `test_git_status_failure_exits_2`.
   - **Status**: FIXED

2. **Rename docstring summary misstated the behaviour**
   - Location: `test_rename_out_of_exempt_path_is_dirty`
   - Note: "is dirt, not its destination" did not say what the test pins.
     It now reads "A staged rename out of an exempt path is listed as
     dirt."
   - **Status**: FIXED

## Fixes Applied

- `tests/test_verify_step.py` `test_quoted_exempt_path_is_clean`: added the
  decoy phase with a porcelain guard (`?? "inbox/my brief.md"`,
  `?? "inbox/my notes.txt"`) and asserted exit 1 with the exact listing
  `["DIRTY: uncommitted changes", '?? "inbox/my notes.txt"']`. The docstring
  now describes the decoy.
- `tests/test_verify_step.py` `test_missing_just_exits_2`: the message check
  is now whole-line membership.
- `tests/test_verify_step.py` `test_rename_out_of_exempt_path_is_dirty`:
  rewrote the docstring summary line.
- `ruff format` rewrapped one line. `ruff check` and `ruff format --check`
  are clean. The file is 274 lines, under the 400-line cap.

## Post-fix verification

- Tracked script, plain `pytest tests/test_verify_step.py -v`: **5/5
  passed**.
- Rebind runs after the fixes: `current.sh` 5/5 green. `m-rc.sh`,
  `m-quote.sh`, `m-gitstatus.sh`, `m-just.sh` and `m-anyquoted.sh` each red
  exactly their one named test. `pre-f1.sh` is 1 passed, 4 failed. The
  numbers are in the table above.

## RED report check

The report's claims reproduce: the control is 5/5, `pre-f1.sh` is 1/4 with
the observed exit codes it states (0, 1, 128, 1), and the script is
untouched. Its line count (258) is from before this review's additions.

## Requirements Validation

| Requirement (slice 2 text) | Status | Evidence |
|---|---|---|
| Rename `R  inbox/a.md -> notes.md` → exit 1, DIRTY listing of that line | Satisfied | Porcelain guard plus exact-lines assertion; `m-rc.sh` reds |
| Quoted `inbox/my brief.md` → exit 0, `CLEAN:` | Satisfied | Porcelain guard; `m-quote.sh` reds; decoy pins that the allowance is not over-broad |
| CWD outside any repo → exit 2, `ERROR: git status failed` | Satisfied | `GIT_CEILING_DIRECTORIES`; line assertion; `m-gitstatus.sh` reds |
| No `just` on `PATH` → exit 2, `ERROR: just not found on PATH` | Satisfied | Explicit `PATH` plus `which` guard; `m-just.sh` reds |
| Mutation red against `31fe4a16` as a copy with `SCRIPT` rebound | Satisfied | `pre-f1.sh` 1 passed, 4 failed; tracked script has no diff |

## Positive Observations

- Every fixture pins its own porcelain before the script runs, so no test
  relies on an assumed git output format.
- The missing-just `PATH` is built from explicit symlinks and checked with a
  `which` guard, which does not depend on the ambient `PATH` layout.
- `GIT_CEILING_DIRECTORIES` makes the not-a-repo failure hold whatever
  checkout `tmp_path` sits under.

## Recommendations

- The `C` (copy) half of the `[^RC]` guard is not pinned. A mutant with
  `^[^R][^R]` would pass all five tests. Pinning it needs a
  `status.renames=copies` fixture to make git emit a `C` line. That would be
  a test beyond the slice's enumerated four, so it is left to the
  orchestrator.
