# Review: Item 1.3, slice 2 — code review (`triage-feedback.sh` behavioral-code diff)

**Scope**: HEAD 95f67f7c, `plugin/bin/triage-feedback.sh`: the
behavioral-code diff and its comment. This is the item's last slice, so the
review also checks both diffs and the script's interface across the whole
item. Out of scope: the test file, `finishing.md` call sites (Item 2.4), and
every other item.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The slice changes the behavioral-code diff from `git diff "$baseline_commit"`
to `git diff "$baseline_commit" HEAD`, as KD-6 and m18 require. Both of the
script's diffs now take `<base> HEAD`, and the interface is unchanged. The
exit-status check found a real defect in the `git diff | grep` pipeline: a
failing `git diff` read as `Behavioral code: no` and the script exited 0. A
probe also showed that the user's git config could make the detection lie. I
fixed both by editing the behavioral-code lines only.

**Overall Assessment**: Ready

## Item-wide checks

- **Both diffs take `"$baseline_commit" HEAD`.** Line 15:
  `git diff --name-only "$baseline_commit" HEAD` (slice 1). Line 47:
  `git diff --no-color --no-ext-diff "$baseline_commit" HEAD` (this slice,
  after the fix below). The two flags only control how the output is
  rendered. The range is the same `<base> HEAD` form.
- **Interface unchanged.** `git diff c8b347aa~1 HEAD` on the script touches
  only the two diff lines and their comments. The usage block, the
  `<job-dir> <baseline-commit>` arguments, the stdout format and the log
  append are all untouched.

## Probes (throwaway repos under `$TMPDIR`)

1. **A failing `git diff` reads as "no" (the defect).** I committed a `def`
   after the baseline, then deleted that blob from `.git/objects`. Line 15's
   `git diff --name-only base HEAD` needs only trees, so it succeeded (rc 0)
   and errexit did not fire. Line 45's `git diff base HEAD` then failed with
   `fatal: unable to read <blob>` (rc 128). It ran inside an `if` condition,
   where errexit is off, and `pipefail` turned the failure into a false
   condition. Before the fix the script printed `- Behavioral code: no` and
   exited 0. After the fix it prints only git's fatal line and exits 128.
2. **SIGPIPE.** The removed comment's worry still holds for `grep -q` under
   `pipefail`: measured, the producer got 141. For the old `grep -E … >
   /dev/null` form, GNU grep 3.11 (`/usr/bin/grep`, the binary a child bash
   resolves) drained its input and gave `0 0` in five runs on a 2.4 MB
   stream. The harness's interactive `grep` function (ugrep) exits on the
   first match when output is /dev/null and gave 141. It is not exported, so
   the script never sees it. After the fix there is no producer process, so
   the question no longer applies. BSD grep was not measured, and after the
   fix it does not need to be.
3. **User git config.** With `color.diff=always`, the old line read `no` for a
   committed `def`, because the `+` lines start with ANSI escapes. With
   `diff.external=/bin/true`, it also read `no`, because the diff body is
   empty. With the fix both read `yes`. `--name-only` (line 15) gives the same
   output under both configs, so it needs no change.
4. **After the fix.** shellcheck is clean. A 300k-line committed diff with a
   `def` reads `yes`. A diff whose only definition line is a removal reads
   `no`, rc 0. A bad baseline (`deadbeef`) exits 128 at line 15, as before.

## Mutated-SUT run (once, before the fix)

- **Mutation**: exact-string replacement of
  `if git diff "$baseline_commit" HEAD | grep -E` with
  `if git diff "$baseline_commit" | grep -E`, which is the forbidden
  working-tree form.
- **Result**: `test_uncommitted_definition_is_not_behavioral` failed on its
  negative assertion, `assert "- Behavioral code: no" in lines`, with output
  `- Behavioral code: yes`. It was red for the right reason.
- **Restore**: the inverse exact-string replacement. `grep -nF` found the
  original line at line 45, `git diff --stat HEAD` on the script was empty,
  and the slice test passed (1/1).

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A failing `git diff` reads as "no behavioral code"**
   - Location: `plugin/bin/triage-feedback.sh:45` (pre-fix)
   - Problem: `if git diff … | grep -E … > /dev/null` runs where errexit is
     off. Under `pipefail`, a git failure only makes the condition false. The
     script then prints `Behavioral code: no` and exits 0. On a Complex
     classification with few files and no reports, that becomes an
     `overclassified` verdict, which is appended to
     `plans/reports/triage-feedback-log.md`. Probe 1 reproduces it: a missing
     blob lets line 15 succeed and line 45 fail.
   - Fix: capture the diff with
     `committed_diff=$(git diff … "$baseline_commit" HEAD)`. The assignment's
     status is git's status, so errexit stops the script. Then match with
     `grep -qE … <<< "$committed_diff"`. A here-string is bash 3.2-safe, and
     `grep -q` is safe here because no producer can be killed. The removed
     `Not grep -q` comment is replaced by one that explains the capture.
   - **Status**: FIXED

2. **User git config can make the detection lie**
   - Location: same line
   - Problem: porcelain `git diff` honours `color.diff=always` and
     `diff.external`. Under either, a committed `def` read `no` (probe 3).
     triage-feedback.sh is a plugin script that runs in whatever repo
     invokes it.
   - Fix: add `--no-color --no-ext-diff` to the behavioral-code diff. The
     range stays `<base> HEAD`. The new comment names both flags.
   - **Status**: FIXED

### Minor Issues

None. The `(KD-6)` citation that GREEN added to the comment matches how
`verify-step.sh`, `changed-files.sh` and `exempt-paths.sh` cite this job's
KDs, so it is consistent with the existing pattern and not a finding.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:38-48` removes the `Not grep -q` comment. It
  adds a four-line comment above a new capture line,
  `committed_diff=$(git diff --no-color --no-ext-diff "$baseline_commit" HEAD)`,
  and the condition becomes
  `if grep -qE "$definition_re|$shell_fn_re" <<< "$committed_diff"; then`.
  The regexes and the comment that explains them are unchanged.
- Verification: shellcheck is clean. `tests/test_triage_feedback.py` passes
  3/3. `just precommit` passes: version consistency, tests 374/375 passed
  with 1 xfail, line limits (three oversized agent files that predate this
  slice, outside its scope), and design links. It ended
  `✓ Precommit OK`.
- Tree after review: ` M plugin/bin/triage-feedback.sh` (uncommitted, as
  instructed) and `?? inbox/brief-corrector-reads-surfaces-against-each-other.md`
  (present before this review, not touched).

## Flagged, not fixed (outside scope)

- **No test pins the two fixes.** The test file is OUT here. A follow-up test
  could delete a committed blob, which is probe 1's fixture, and assert a
  non-zero exit and no `Behavioral code:` line. A second could set
  `color.diff=always` in the fixture repo and assert `yes`. As it stands, a
  regression back to the piped form would pass the suite.
- **Residual: textconv.** Porcelain `git diff` still applies
  `diff.<driver>.textconv` from attributes. A textconv on source files could
  rewrite the `+` lines. I did not add `--no-textconv`: I found no such
  config here, and it is a separate rendering axis. I did not measure it.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m18 / KD-6: both diffs take `"$baseline_commit" HEAD` | Satisfied | `triage-feedback.sh:15` and `:47`; the slice test passes, and the mutated working-tree form reds on the negative |
| Interface unchanged | Satisfied | the item-wide diff touches only the two diff lines and their comments |
| `finishing.md` §2 passes `changed-files.sh`'s `BASE:` | DEFERRED | prose call site, Item 2.4 |

## Positive Observations

- The test-review fixture rules out last-commit-only, index-only and
  working-tree variants. The mutated run confirmed that the working-tree form
  reds on the negative assertion, not on setup.
- The GREEN change is one token, and the comment now says which range is
  diffed.
