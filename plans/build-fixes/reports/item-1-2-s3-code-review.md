# Review: Item 1.2 slice 3 — code review (`changed-files.sh`, whole script)

**Scope**: `plugin/skills/build/scripts/changed-files.sh` as of HEAD (`✨ Item 1.2/3 — no item report exits 1`). Reviewed whole against the Item 1.2 Interfaces block and KD-1/KD-6, as well as the slice's own change. Out of scope: Item 1.3 (`triage-feedback.sh`), every prose item, and the test files.
**Date**: 2026-10-02
**Mode**: review + fix (TDD code review)

## Summary

The slice's change is correct. The `[[ -z $first_commit ]]` check sits after `git log`'s own `|| { ERROR; exit 2; }`, so a `git log` failure is exit 2 and never reads as an empty result. Probed on an unborn-HEAD repo: `fatal: …`, `ERROR: git log failed`, exit 2. Reviewing the whole script turned up one exit-0 contract defect from slice 1: `git diff` and `git log` ran with rename detection on. That made the list depend on the user's `diff.renames`, and once the rename limit was hit it printed git's warnings among the paths, because `exec 2>&1` merges them into stdout. There was also one unguarded write that exited 1 (NO-BASE's code), and the slice restated one rule three times in comments. All are fixed. Precommit is green.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Rename detection breaks the exit-0 output contract**
   - Location: `changed-files.sh`, the `git diff --name-only -z "$base_sha" HEAD --` pipeline, and the `git log --diff-filter=A` query
   - Problem: The Interface promises `BASE: <sha>`, then one path per line. `git diff` honours `diff.renames`, which defaults to true. Once the candidates pass `diff.renameLimit`, git writes `warning: exhaustive rename detection was skipped due to too many files.` plus a second hint line to stderr, and `exec 2>&1` puts both on stdout between `BASE:` and the paths. Reproduced with `diff.renameLimit=1` and three renames: two `warning:` lines came out as list entries, exit 0. The list's content also changed with user config. Under the default it was `g1.txt g2.txt g3.txt`, with the rename sources dropped. Under `diff.renames=false` or a hit limit it was `f1..f3` plus `g1..g3`. On the log side, a report renamed into place (`draft.md` → `item-1-1.md`) is an `R`, not an `A`, so `--diff-filter=A` missed it and derived a later base or NO-BASE. This is the same user-config hazard class the script already guards with `--no-show-signature`.
   - Fix: added `--no-renames` to both `git diff` and `git log`. Now a rename is always a deletion plus an addition, no rename warning can be emitted, and a report renamed into place counts as added. The KD-6 header paragraph states the reason once.
   - Verified: the same fixture under `diff.renameLimit=1` and under the default now prints the same `f1..f3, g1..g3` list with no `warning:` lines. The renamed-in report derives `BASE:` as its commit's parent.
   - **Status**: FIXED

### Minor Issues

1. **Writing `BASE:` could exit 1, NO-BASE's code**
   - Location: `printf 'BASE: %s\n' "$base_sha"`
   - Problem: This was the only fallible command in the script with no explicit exit-2 path. If the write fails, `set -e` exits with printf's status 1. Reproduced: `changed-files.sh j > /dev/full` exited 1, which a caller reads as "no committed item report". (With SIGPIPE at default, a closed pipe kills the shell with 141 instead. The `/dev/full` case, or SIGPIPE ignored, gives 1.)
   - Fix: `printf … || exit 2`, with a one-line comment giving the reason. No `ERROR:` line, because stdout is the stream that failed. Verified: `> /dev/full` now exits 2.
   - **Status**: FIXED

2. **The root-commit rule was stated three times**
   - Location: the header's KD-1 paragraph, the new comment above `[[ -z $first_commit ]]`, and the existing `# A root commit has no parent: an error, never a fallback base.`
   - Problem: The slice added two restatements of what the pre-existing comment at the parent lookup already says. The new inline comment also repeated the header's NO-BASE sentence.
   - Fix: the header now states the exit contract once: NO-BASE exits 1, usage and git failures exit 2 with `ERROR:`, so nothing else exits 1. I removed the new inline comment, since the `printf 'NO-BASE: …'; exit 1` block explains itself. The root-commit rule stays where it was, at the parent lookup.
   - **Status**: FIXED

## Fixes Applied

- `changed-files.sh` header: replaced the slice's NO-BASE/root-commit sentences with one statement of the exit contract. Added the `--no-renames` rationale to the KD-6 paragraph, which I rewrapped at 80 columns.
- `changed-files.sh` `git log`: added `--no-renames`.
- `changed-files.sh`: removed the three-line comment above `[[ -z $first_commit ]]`.
- `changed-files.sh` `printf 'BASE: …'`: added `|| exit 2` and a one-line reason comment.
- `changed-files.sh` `git diff`: added `--no-renames`.

Post-fix checks: `shellcheck -x` clean. `tests/test_changed_files.py` and `tests/test_verify_step.py` 11/11 passed. `just precommit`: version consistent 0.3.0, 372/373 passed with 1 xfail, design-links clean, `✓ Precommit OK`. The three `oversized-file` lines name pre-existing agent definitions unrelated to this item.

## Mutated-SUT run

Mutant: `git log`'s failure branch (`echo "ERROR: git log failed"; exit 2`) replaced in place by `first_commit=`. This is the forbidden behaviour the dispatch names, where a `git log` failure is mistaken for an empty result and answered with NO-BASE.

- `tests/test_changed_files.py`: **3/3 passed**. No test redded.
- Manual probe of the mutant on an unborn-HEAD repo: `NO-BASE: …`, exit 1. The unmutated script gives `ERROR: git log failed`, exit 2.
- Restore by the inverse exact-string replacement. Proved by `grep -c 'first_commit=$'` → 0, `grep -n 'ERROR: git log failed'` → line 69, an empty `git diff --stat` on the file, and a 3/3 green run.

So the `git log` ERROR/NO-BASE separation is correct in the code but pinned by no test, which is the gap the test review's Recommendation predicted. See Recommendations.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Exit 0: `BASE: <sha>`, then one path per line | Satisfied (after Major 1) | `--no-renames` on the diff. No git warning can enter stdout from rename detection |
| Exit 1: `NO-BASE:` with no committed `item-*` report | Satisfied | `[[ -z $first_commit ]]` after a successful `git log`. `test_no_item_report_exits_1` |
| Exit 2: `ERROR:` on usage or git failure | Satisfied | usage, `case` job-name guard, `source`, `rev-parse --show-toplevel`, `cd`, `git log`, parent lookup and `git diff` each `exit 2`. `BASE:` write failure now exits 2 too (Minor 1) |
| Paths read NUL-delimited, never split on whitespace | Satisfied | `git diff -z` → `while IFS= read -r -d ''`. The line-format residual bound is stated in the header |
| KD-1: base = parent of earliest commit adding `plans/<job>/reports/item-*`, from committed history only | Satisfied | `git log --diff-filter=A --reverse`, first line, `^`. Rename-in now counted as an addition |
| KD-6: `<base> HEAD` diff minus `plans/<job>/` and exempt paths | Satisfied | `"$exclude_prefix"*` and `$exempt_re` inside the NUL loop. Slice 2's test |

## Positive Observations

- `git log`'s failure is handled before its output is read, so the empty check can only see a successful empty result. The separation the dispatch asked about holds by construction.
- The job-name `case` guard against pathspec glob syntax closes the sibling-job prefix hazard at the input rather than relying on the pathspec.
- `--quiet` on the parent lookup keeps the root-commit `ERROR:` as the first stdout line, which the paired test asserts.
- The `set -u` comment's claim checks out empirically: an unbound variable in a bash script file exits 1 (bash 5.2.37).

## Recommendations

- No test pins `git log`'s failure → exit 2, a rename in the run diff, or the `BASE:` write failure. The mutated-SUT run above shows the `git log` mutant stays green. A `test_git_log_failure_exits_2` (unborn-HEAD repo: exit 2, a line starting `ERROR:`, no `NO-BASE:`) would pin the separation this slice exists for. A rename fixture under `diff.renameLimit=1` would pin Major 1. Test files are out of this dispatch's scope, so both go to the orchestrator as possible added slices.
- For git failures other than the parent lookup, git's own `fatal:` line precedes `ERROR:` on stdout, because `exec 2>&1` merges it. This matches `verify-step.sh`, and the Interface does not require `ERROR:` as the first line for exit 2. Not a finding. Recorded so that no consumer is written to key on the first line for exit 2.
