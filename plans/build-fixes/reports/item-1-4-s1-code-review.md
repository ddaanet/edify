# Review: Item 1.4 slice (a) — code review

**Scope**: `plugin/skills/build/scripts/changed-files.sh` as changed by HEAD
(`Item 1.4/1 — phase without boundary gives run base`): argument handling,
usage strings, header comment, no-flag behaviour. Boundary search (slice b),
slices (c)–(d) and the test file are out of scope.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The slice widens the arity check to accept `--phase` as an exact second
argument and updates both usage strings and the header comment. It adds no
boundary search, which is correct for slice (a): `--phase` is accepted and
ignored, so the output equals the bare call's. One real defect: `--phase` on
its own (the job left out) passed as a job name and exited 1 with `NO-BASE:`,
which is the "fresh run" result, not a usage error. That is fixed. A
mutated-SUT run shows the exact-`--phase` guard is not pinned by any test.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A lone `--phase` exits 1 `NO-BASE:` instead of a usage error**
   - Location: `plugin/skills/build/scripts/changed-files.sh:40-45` (job-name
     `case`)
   - Problem: `changed-files.sh --phase` and `changed-files.sh --phase --phase`
     pass the arity check (`$1` is not tested), and `--phase` passes the
     job-name `case`. The script then searches
     `plans/--phase/reports/item-*`, finds nothing, and prints
     `NO-BASE: no committed plans/--phase/reports/item-* report` with exit 1.
     KD-1 gives exit 1 a meaning: no item report committed, so the run is
     fresh. A caller that drops the job therefore gets a valid-looking answer.
     The header promises that only `NO-BASE:` exits 1 and that usage errors
     exit 2, and the scope says `--phase` is accepted only as the exact second
     argument. Probed in a scratch repo before the fix: both calls gave
     `rc=1`.
   - Fix: added `--phase` to the rejected job-name patterns, with a comment
     giving the reason. Both calls now print
     `ERROR: usage: changed-files.sh <job> [--phase]; not a job name: --phase`
     and exit 2. I rejected exactly `--phase` rather than every `-*`, so
     no-flag calls for any other job name behave as before.
   - **Status**: FIXED

### Minor Issues

1. **Header comment did not say the position is exclusive**
   - Location: `plugin/skills/build/scripts/changed-files.sh:28`
   - Note: "accepted as a second argument" now reads "accepted only as the
     second argument". `--phase j` is rejected, and the comment should say so.
   - **Status**: FIXED

2. **The exact-`--phase` guard is untested**
   - Location: `tests/test_changed_files.py` (out of scope, not edited)
   - Note: mutated-SUT run. I replaced
     `if [[ $# -lt 1 || $# -gt 2 || ( $# -eq 2 && $2 != --phase ) ]]; then`
     with `if [[ $# -lt 1 || $# -gt 2 ]]; then`, so any second argument is
     accepted. Result: 4/4 passed, so the mutant survived. The slice's test
     shows `--phase` is accepted but does not show that anything else is
     refused. The lone-`--phase` rejection fixed above has no test either. A
     usage-error test (`j -p`, `--phase j`, `--phase`, each exit 2 with
     `ERROR: usage:`) would pin both. This belongs to whoever owns the test
     file, in a later slice or a follow-up.
   - **Status**: DEFERRED — the test file is OUT for this review; recorded
     for the orchestrator.

## Fixes Applied

- `plugin/skills/build/scripts/changed-files.sh:39-42` — `--phase` added to
  the job-name `case`'s rejected patterns, with a comment explaining why a
  lone flag would otherwise read as `NO-BASE:`.
- `plugin/skills/build/scripts/changed-files.sh:28` — header comment now says
  `--phase` is accepted *only* as the second argument.

## Verification

- `shellcheck -x changed-files.sh`: clean. Plain `shellcheck` reports only
  SC1091 (info) on the `source` line, which this slice did not touch.
- Scratch-repo probes after the fix:
  - `j` → `BASE:` and the list, rc 0
  - `j --phase` → identical output, rc 0
  - `--phase`, `--phase --phase`, `--phase j`, `j --phase x`, `j -p`, `j ''`,
    no args → `ERROR: usage:`, rc 2
- `just test tests/test_changed_files.py`: 4/4 passed after the fixes.
- Mutation: I changed the guard line in place by exact-string replacement and
  restored it by the inverse replacement. `grep -nF` confirmed the original
  guard at line 31, and the re-run passed 4/4.
- `just lint`: fails on `tests/line_limits_helpers.py:32:30 RUF100` (unused
  `noqa`). This failure was already there: the file is outside this slice and
  outside HEAD's diff. Its test step passed 375/376 with 1 xfail.
- Bash 3.2: the `( … )` grouping and `!=` inside `[[ ]]` work on bash 2 and
  later. In `$2 != --phase` the right-hand side contains no glob
  metacharacters, so the pattern match is an exact match. `set -u` is safe
  because `&&` short-circuits before `$2` is read when `$# -eq 1`.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `--phase` accepted only as the exact second argument | Satisfied (after fix) | arity guard line 31; `--phase` rejected as a job name, line 42 |
| Anything else is a usage `ERROR:`, exit 2 | Satisfied (after fix) | probes above |
| Usage strings and header comment accurate | Satisfied | lines 28-29, 32, 43 |
| No-flag behaviour unchanged | Satisfied | the bare `j` output is unchanged; only a job literally named `--phase` is now refused |
| Slice (a): no boundary → `--phase` gives run base | Satisfied | `--phase` output is identical to the bare call |
| No boundary search implemented (slice b OUT) | Satisfied | no `phase-*-corrector.md` query in the script |

## Positive Observations

- The guard keeps everything in one `[[ ]]` and leaves `--phase` unparsed
  into a variable until slice (b) needs it, so nothing is built ahead of need.
- Both usage strings were updated together, so the two error paths still
  agree.
