# Review: review-fixes-4 review-gate group review-code (F3, F4, F7)

**Scope**: diffs from baseline 35d470b1 to HEAD of `tests/test_triage_feedback_failures.py`, `plugin/bin/triage-feedback.sh`, `agents/learnings.md`, `plugin/README.md`. Design reference: `plans/review-fixes-4/outline.md`. Requirements: the 7 minors F1-F7; this group holds F3, F4, F7.
**Date**: 2026-10-09
**Mode**: review + fix

## Summary

All three in-scope findings are delivered as the outline states them. F3's new test fails on its assertions under three distinct mutations of the guard and passes on HEAD; the narrowed comment is true and drops the claim the outline said to drop. F4 and F7 match the outline's verbatim text, and their factual claims check out against the current scripts and skill prose. No issues found; no fixes applied.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None. The working tree is unchanged by this review (`git diff HEAD --stat` empty; the three untracked `inbox/*.md` files untouched). The script was mutated three times for the mutation run and restored byte-for-byte from a saved copy each time.

## Checks Performed

**F3 test (`test_root_cd_failure_is_one_error_line`)**

- Passes on HEAD (`tests/test_triage_feedback_failures.py`: 9 passed, `-p no:markdown_report`, foreground).
- Fixture reaches the guard: the shim answers only `rev-parse --show-toplevel` (the exact call at `triage-feedback.sh:35`), every other call execs the real `git`. `_init_repo` runs through `_run_git` without the shim on `PATH`, so the fixture is built with real git; only the triage run gets the shim. The missing path is nonexistent, so `cd` fails after a successful `rev-parse`.
- Wrong-reason hunt: stdout equality with `ERROR: cannot change to <missing root>\n` can only be produced by the guard; nothing upstream prints that text. The assertion is an exact equality (not a substring) and the path is unique to the test.
- Mutation run (the SUT mutated in place, tests not moved, SUT restored after each):
  1. Guard replaced by a bare `cd "$repo_root"`: FAILED on the stdout assertion (`'' == 'ERROR: cannot change to ...'`). This is the outline's mutation red.
  2. `$repo_root` unquoted in the `printf`: FAILED on the stdout assertion (message split at the space: `ERROR: cannot change to root`). The space in `missing root` earns its keep.
  3. Guard's `exit 2` changed to `exit 1`: FAILED on `assert 1 == 2`.
  Every mutation reddened on an assertion, not an error.
- Docstring claims are true: bare `cd` under `set -e` gives exit 1 with empty stdout (mutation 1); stderr additionally carries bash's own `cd:` diagnostic, which the docstring does not contradict (it speaks of stdout and the `ERROR:` line).
- Macos portability: the shim is `/bin/sh` with `case`, `printf`, `exec`; the path is passed through `shlex.quote`. `ruff check` and `ruff format --check` clean. Module is 283 lines, under the 400 cap.

**F3 comment (`triage-feedback.sh:40-43`)**

- Narrowed to the script-directory `cd` only, matching the outline; the "no input provokes the root `cd`" claim is gone; the last sentence names the test that pins this guard, which exists. Lines are within 80 columns. `shellcheck` reports nothing on the script. The edit is comment-only; no behavioural change.

**F4 (`plugin/README.md` Optional plugins, `plugin-dev`)**

- Appended sentence is verbatim from the outline, hard-wrapped at 80, surrounding text kept.
- Claim true: `/requirements` (`skills/requirements/references/formats-and-exit.md:118-127`), `/design` (`skills/design/references/write-outline.md:14-27`, `design-content-rules.md:208-212`) and `/build` (`skills/build/SKILL.md:99`) load `plugin-dev:*` skills for hook, agent, skill and plugin work.

**F7 (`agents/learnings.md:64`)**

- Replacement is verbatim from the outline and a single physical line; the Correct-pattern bullet below is unchanged.
- Claims verified by running the scripts: `triage-feedback.sh plans/outline-proofing` prints `ERROR: usage: changed-files.sh <job> [--phase]; not a job name: plans/outline-proofing` then `ERROR: changed-files.sh exited 2` and exits 2 (before the evidence and log-row code, so no evidence and no log row); `triage-feedback.sh a b` prints the usage line on stderr and exits 1. `changed-files.sh:59` refuses `*/*`.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| F3 (Item 1.1): pin triage's root `cd` failure | Satisfied | New test, three mutation reds; comment narrowed |
| F4 (Item 1.2): README `plugin-dev` sentence | Satisfied | `plugin/README.md:104-109` |
| F7 (Item 1.2): learnings Anti-pattern bullet | Satisfied | `agents/learnings.md:64` |

**Gaps:** none within this group.

## Positive Observations

- The test's fixture path holds a space, which makes the quoting of the `printf` argument observable (mutation 2).
- The test asserts the exact stdout line first and the exit code second, so a failing run reports the missing cause rather than only an exit status.
- The F7 text is shorter and every claim in it is directly checkable against the two scripts.

## Recommendations

None.
