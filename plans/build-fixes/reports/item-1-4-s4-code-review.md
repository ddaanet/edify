# Review: Item 1.4 / slice 4, code review (`core.quotePath` fix vs its pin)

**Scope**: `plugin/skills/build/scripts/verify-step.sh` and the
`exempt-paths.sh` it sources (unchanged by `88ef264e`), read against
`tests/test_verify_step.py::test_quotepath_false_does_not_hide_dirt`. Tests
were OUT for edits.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The fix and the test agree. The test sets up exactly the hazard the fix
closes: a repo-local `core.quotePath false`, a raw `0xFF` byte in a
non-exempt untracked path, and GNU grep in a UTF-8 locale. It runs the real
script and asserts the outcome, and an in-place mutant that drops the forced
quoting turns it red on its assertion. The fix is complete: `git status` is the
only git call in the script, `exempt-paths.sh` makes none, and neither
environment-level config nor color config gets past the `-c`. One minor fix was
applied: the DIRTY listing was printed with `echo`, which garbles the
backslash escapes that the forced quoting produces if `xpg_echo` is inherited.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **The DIRTY listing went through `echo`, though forced quoting fills it
   with backslash escapes**
   - Location: `plugin/skills/build/scripts/verify-step.sh:60`
     (`echo "$status"`)
   - Note: with `core.quotePath=true`, git writes C-style escapes into the
     status lines: `\t`, `\\`, `\"`, `\nnn`. `echo` is implementation-defined
     on backslash operands (`shell-scripting:shell-gotchas` rule 5). Bash
     reads `xpg_echo` from an exported `BASHOPTS`. Measured:
     `env BASHOPTS=xpg_echo bash -c 'echo "?? \"a\tb.txt\""'` emits a real
     TAB where git wrote `\t`. The verdict and the exit code are unaffected,
     so this is not fail-open. The listing just stops matching what git
     wrote. After the fix, a repo holding an untracked `a<TAB>b.txt` run under
     `BASHOPTS=xpg_echo` prints `?? "a\tb.txt"` literally.
   - Not pinned by a test: discriminating it needs `BASHOPTS=xpg_echo` plus a
     path with a `\t` or `\\` escape. Tests are OUT for this dispatch. The
     orchestrator can add it to a later slice if it wants the pin. Without the
     pin, the exact-listing assertions in the existing tests still check that
     plain listings are unchanged.
   - **Status**: FIXED

## Check results

**1. Does the test exercise the hazard the fix closes, as production invokes
it?** Yes.

- Hazard: with `quotePath` off, git emits the raw byte. GNU grep 3.11 in a
  UTF-8 locale then reports `binary file matches`, drops that line and exits
  0, so `status` is empty and the script prints `CLEAN:`. Measured on this
  box: `printf 'a\n\377\nc\n' | LC_ALL=C.UTF-8 grep -vE zzz` prints `a`, `c`
  and the binary message. Only the bad line is lost, which matches the
  script comment's and the test docstring's "drop that line".
- The test makes that state: the config is repo-local (global and system
  config are nulled for the run, so it is the only `quotePath` the script
  sees), the raw byte is written through a surrogateescape `Path`, and
  `LC_ALL=C.UTF-8` is pinned. Its path `inbox/x\377/y.md` is non-exempt
  either way, since the `/` fails `inbox/[^/]+\.md`. So neither the
  exemption nor the quoting can supply the verdict. Only the line surviving
  grep can.
- Production calls the script by its relative path from the repo root. The
  test calls it by absolute path with CWD at the repo root. The hazard does
  not depend on the invocation path, and both resolve `exempt-paths.sh`
  (script comment, lines 5-10). In production `quotePath false` can come from
  global config too. `-c` overrides every config source, so the repo-local
  fixture stands for all of them.
- The test is reached and not skipped on Linux: `just precommit` reported
  379/380 passed, 1 xfail, 0 skipped.

**2. Mutated-SUT run (once, in place).**

- Mutation: an exact-string replacement in `verify-step.sh`, with each string's
  count asserted (old 1, new 0). It changed
  `porcelain=$(git -c core.quotePath=true status --porcelain` to
  `porcelain=$(git status --porcelain`.
  `grep -cF 'porcelain=$(git status --porcelain'` gave 1, so the mutation
  landed.
- `pytest tests/test_verify_step.py tests/test_verify_step_exemption.py -v`
  gave **8/9 passed, 1 failed**. The failure was
  `test_quotepath_false_does_not_hide_dirt` at
  `assert result.returncode == 1`, with output
  `grep: (standard input): binary file matches` /
  `CLEAN: tree clean, just precommit passed`.
- The same test with an outer `LC_ALL=C` also failed (0/1), which confirms
  the locale pin holds.
- Restore: the inverse replacement, with counts asserted.
  `grep -cF 'porcelain=$(git -c core.quotePath=true status --porcelain'` gave
  1, and `git diff --quiet plugin/skills/build/scripts/` exited 0. A re-run
  gave **9/9 passed**.
- The test has red against the canonical forbidden implementation in place,
  not only against copies (the RED and the test review used copies).

**3. Is the fix complete?** Yes.

- Line 40's `git status` is the only git call in `verify-step.sh`.
  `exempt-paths.sh` defines one variable and runs nothing. `just precommit`
  reads no paths into the script.
- Precedence was probed on git 2.47.3 with a repo holding `quotePath false`,
  `b c.txt` and `inbox/x\377/y.md`:
  - `GIT_CONFIG_PARAMETERS="'core.quotepath'='false'"`, and the
    `GIT_CONFIG_COUNT`/`KEY_0`/`VALUE_0` form, each set to `false`: both
    still print `?? "inbox/x\377/y.md"`, so the `-c` wins.
  - `-c color.status=always -c color.ui=always`: the porcelain stays plain
    ASCII (checked with `od -c`, no escape sequences).
- Porcelain v1 paths are always relative to the repo root, so
  `status.relativePaths` does not apply. `--untracked-files=all` overrides
  `status.showUntrackedFiles`.
- With quoting forced, every byte at or above `0x80` and every control byte
  arrives as an ASCII escape, and paths cannot hold NUL. No other input can
  trip grep's binary detection.

**4. Shell checks.** `shellcheck -x` on `verify-step.sh` is clean after the
fix. The plain `shellcheck` run reports only SC1091 (info), because it does not
follow the dynamic source. Nothing in the touched line affects macOS:
`printf '%s\n'` is POSIX, and bash 3.2 handles it.

## Fixes Applied

- `plugin/skills/build/scripts/verify-step.sh:60`: changed
  `echo "$status"` to `printf '%s\n' "$status"`, so the git-quoted listing is
  printed byte for byte (Minor 1).

## Files changed

- `plugin/skills/build/scripts/verify-step.sh`
- `plans/build-fixes/reports/item-1-4-s4-code-review.md` (this report)

## Gate

`just precommit`: `Precommit OK`. The suite gave 379/380 passed, 1 xfail.
Version is consistent at 0.3.0, and design-links found 87 decisions. The three
pre-existing `oversized-file` warnings (`plugin/agents/corrector.md`,
`outline-corrector.md`, `design-corrector.md`) are outside this scope.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 1.4/4: repo-local `core.quotePath false` + untracked `inbox/x\377/y.md` → exit 1 | Satisfied | test passes on the real script; reds in place without the `-c` |
| Skipped on macOS | Satisfied | `skipif(sys.platform == "darwin")`; runs on Linux (0 skipped in the gate) |
| Mutation red, as in Item 1.1 | Satisfied | RED/test review mutants on copies; this review's in-place mutant, restored by inverse replacement |
| Fix complete (1.1/2 code review Major 1) | Satisfied | single git call; `-c` beats env config; porcelain is ASCII under color config |

## Positive Observations

- The test pins the locale, so its red does not depend on the runner. Under
  an outer `C` locale the mutant still reds on the assertion, not on a
  decode error.
- The script comment (lines 31-34) states the hazard precisely, and the
  measurement agrees with it: one line is dropped, and grep exits 0.

## Process note

In the reviewer's interactive shell, `grep` is a harness function that
dispatches to ugrep. A `grep -c` probe with `$(` in a BRE returned 0 there
against the landed mutant, and it was re-run as `grep -cF`. The script itself
resolves `/usr/bin/grep` (GNU 3.11), because the function is not exported.
