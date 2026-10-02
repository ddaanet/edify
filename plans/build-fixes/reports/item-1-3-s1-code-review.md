# Review: Item 1.3, slice 1 — code review (`triage-feedback.sh` files-changed count)

**Scope**: HEAD c8b347aa, `plugin/bin/triage-feedback.sh` line 14, the
files-changed computation:
`files_changed=$(git diff --name-only "$baseline_commit" HEAD | wc -l | tr -d ' ')`.
Out of scope: the behavioural-code diff (line ~43, which slice 2 changes), the
test file (already test-reviewed), and every other item.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

Adding `HEAD` turns the count from "baseline against the working tree" into
"baseline against HEAD", which is what KD-6 and m18 ask for. I probed the three
concerns the dispatch named, and none of them is a defect. The only finding is
minor: the comment above the line was stale. I fixed it.

**Overall Assessment**: Ready

## Probes (run on a throwaway repo in the session scratchpad)

1. **Exit-status honesty, bad baseline.** The script runs under
   `set -euo pipefail`, and `pipefail` carries into the `$( … )` subshell. So
   when `git diff` fails, the pipeline's status is git's non-zero status. The
   assignment then returns that status and `errexit` stops the script. Measured:
   - `triage-feedback.sh job deadbeef…` printed `fatal: bad object …` on
     stderr, nothing on stdout, and exited 128.
   - `triage-feedback.sh job nosuchref` printed `fatal: ambiguous argument …`
     and exited 128.

   The script never prints `Files changed: 0` for a bad baseline. This line
   runs before line 43, so line 43's `if git diff … | grep` (where errexit is
   off) cannot be reached with a bad baseline either.
2. **Filename safety of counting lines.** Without `-z`, `git diff --name-only`
   always C-quotes a path that contains a newline: a file named `a<NL>b`
   printed as `"a\nb"` on one line. This still holds under
   `-c core.quotePath=false`, because quotePath only affects bytes ≥ 0x80. A
   path with a space prints as one line. So `wc -l` counts one line per file,
   and the probe repo counted 3 for three changed paths, one of them the
   newline path. A rename counts once, under its new name. The pre-slice form
   did the same.
3. **BSD `wc` padding.** I put a shim on PATH that pads `wc` output to 8
   columns with leading spaces, as BSD `wc` does. With it the script still
   printed `- Files changed: 3`, because `tr -d ' '` strips the padding. The
   `reports_count` line next to it uses the same pattern. Residual bound: BSD
   `wc` pads with spaces, not tabs. I took that from the BSD source format
   (`" %7lld"`) and did not measure it on macOS.

## Mutated-SUT run (once)

- **Mutation**: exact-string replacement that drops `HEAD`, giving back the
  forbidden working-tree form
  `git diff --name-only "$baseline_commit" | wc -l`.
- **Result**: `test_files_changed_counts_committed_changes_only` failed on its
  assertion. The output read `- Files changed: 5`, the baseline-vs-working-tree
  count, where the test expects 3. It was red for the right reason.
- **Restore**: the inverse exact-string replacement. I proved it three ways:
  `grep -nF` found the original line at line 14,
  `git diff HEAD -- plugin/bin/triage-feedback.sh` was empty, and the slice
  test passed again (1/1).

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Stale comment above the count**
   - Location: `plugin/bin/triage-feedback.sh:13`
   - Note: The comment still read `# Count files changed since baseline`. That
     describes the old working-tree form, not a count that now leaves
     uncommitted edits out. Nothing at the site said why `HEAD` is there, so a
     later edit could drop it and bring m18 back. Nothing said why counting
     lines is safe for odd filenames either.
   - **Status**: FIXED. The comment now says the count covers committed changes
     since the baseline, that the HEAD form keeps uncommitted dirt out, and
     that git C-quotes a path holding a newline, so one line is one file. I did
     not put a plan KD number in the comment: KD numbers are per job, and the
     script already cites a KD-3 from a different job.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:13-14`: rewrote the one-line comment as a
  two-line comment that states why `HEAD` is there and why counting lines is
  safe. The code is unchanged. Afterwards shellcheck was clean and
  `tests/test_triage_feedback.py` passed 2/2.

## Flagged, not fixed (outside this slice)

- Line 43, `if git diff "$baseline_commit" | grep …`, still uses the
  working-tree form, so after this slice the two diffs use different ranges.
  Slice 2 (`test_uncommitted_definition_is_not_behavioral`) is next and closes
  this. It is OUT for this review, and I did not touch it.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m18 / KD-6 (files-changed diff takes `<base> HEAD`) | Satisfied for this slice's diff | `triage-feedback.sh:15`; the slice test passes, and the mutated SUT reds at 5 |
| Interface unchanged (`<job-dir> <baseline-commit>`) | Satisfied | the usage/argument block is untouched |

**Gaps:** the second diff (line 43) is slice 2's work and was not reviewed here.

## Positive Observations

- The change is one token. It keeps the existing `| wc -l | tr -d ' '` pattern
  and adds no new failure path.
- The test pins a value (3) that differs from every neighbouring range: the
  mutated SUT read 5, not something that happens to equal 3.

## Recommendations

None beyond slice 2.
