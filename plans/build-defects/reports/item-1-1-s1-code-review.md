# Review: Item 1.1 / Slice 1 — code review

**Scope**: `plugin/bin/triage-feedback.sh` at 2152b28b, whole script audited, KD-3 change as focus. Tests out of scope.
**Date**: 2026-09-25
**Mode**: review + fix (TDD code review, dispatch 4 of 4)

## Summary

The KD-3 change is correct. It excludes exactly `review.md`, `review-*.md` and
`final-review.md`, uses portable `find` primaries, and is shellcheck-clean.
The review found one newline-in-filename overcount on the edited line, one
comment inaccuracy and one pre-existing portability nit. **None of the fixes
could be applied.** The auto-mode classifier returned "no verdict" on every
`Edit` of the script, which is a hard failure it says not to retry. I did not
fall back to `sed` or a Bash rewrite, because that would bypass the gate. The
mutated-SUT run was blocked the same way. The script is byte-identical to
2152b28b: `git diff --stat` is empty.

**Overall Assessment**: Needs Minor Changes. No critical or major issues.
Three minor fixes are written out below, ready to apply.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **A newline in a report filename inflates `reports_count`**
   - Location: `plugin/bin/triage-feedback.sh:25-28`
   - Problem: `find … | wc -l` counts lines, not files. Probe: in a directory holding `a b.md`, `item<NL>1.md` and `review-skill.md`, the current form counts 3 and a per-file byte count gives the correct 2. One extra count on a Simple job flips `match` to `underclassified`. Spaces are safe; only a newline miscounts.
   - Fix: replace `| wc -l | tr -d ' '` with `-exec printf x \; | wc -c | tr -d ' '`. This is POSIX, and `pipefail` still carries a `find` failure into the assignment.
   - **Status**: NOT APPLIED. The `Edit` was refused by the auto-mode classifier ("gave no verdict … retrying this action will get the same answer"). This is a tool blockage, not a U-code: the fix is known and unambiguous.

2. **The comment says `review_artifact` reports all three excluded names; it does not report `final-review.md`**
   - Location: `plugin/bin/triage-feedback.sh:18-21`
   - Problem: `review_artifact` (lines 76-90) looks only at `review.md` and `review-*.md`. `final-review.md` is the closing corrector's report (`finishing.md` §3.1). The script never surfaces it, so "already reports their presence separately" overstates. Its fourth line narrates the bug being fixed rather than the rule.
   - Fix: make lines 18-21 read:
     ```
     # Exclude review-gate and closing-review reports too: review.md, review-*.md,
     # final-review.md (KD-3). They record review, not execution; review_artifact
     # below reports the review gate's presence separately.
     ```
     Add `# One byte per file, not \`wc -l\`: a newline in a filename would overcount.` if fix 1 lands.
   - **Status**: NOT APPLIED (same classifier refusal).

3. **`\s` in the classification grep/sed is not POSIX ERE (pre-existing)**
   - Location: `plugin/bin/triage-feedback.sh:51`
   - Problem: `\s` is a GNU extension. POSIX ERE leaves it undefined, and I have not verified how BSD `grep -E` and `sed -E` handle it. The script's own regexes at lines 38-40 already use `[[:space:]]`.
   - Fix: replace the three `\s` with `[[:space:]]`. This is equivalent on GNU and defined on BSD. It is trivially safe, and the slice test's `- **Classification:** Simple` line exercises it.
   - **Status**: NOT APPLIED (same classifier refusal).

## Deferred Items

The following items were identified but are out of scope:

- **`xargs` used as a trimmer, with `|| true` masking the whole pipeline** (`:51`). A classification value containing a quote makes `xargs` fail with "unterminated quote". `|| true` then turns that into an empty classification, and the result is a silent `no-classification`. `|| true` is legitimate for grep's no-match exit, but it also covers `sed` and `xargs`. The reason for deferral: this is pre-existing, outside KD-3, and not a one-token fix (it needs the grep status tested separately).
- **The `WARNING: No corrector report` path** (`:107-110`). Scope OUT (Item 2.3).
- **`reports_count` still counts per-item and per-slice reports** (for example `item-1-1-s1-code-review.md`). Scope OUT, outline Q-2.

## Mutated-SUT run

Not run. The in-place mutation (dropping `! -name "review.md" `, the partial GREEN the slice rules out) was refused by the same classifier, so the SUT was never changed and no restore was needed. The test review had already run that variant against a scratch copy and recorded FAIL (`Reports: 1`), per `item-1-1-s1-test-review.md` §Wrong-reason checks. The unmutated run passes: `pytest tests/test_triage_feedback.py -v` → 1/1 passed.

## Whole-script audit (no finding)

- `:14`, `:25` assignments from pipelines: a failure propagates through `pipefail` and `set -e` on the assignment.
- `:43`: `grep -E … > /dev/null` rather than `grep -q`, with the SIGPIPE reason stated inline. It redirects stdout only; the script has no `2>/dev/null` anywhere.
- `:80-88`: `compgen -G` works in bash 3.2. The `find | wc -l` there is newline-safe in effect: it only tests for `== 1`, and the only file that can make it 1 is `review-skip.md`, whose name has no newline. BSD `wc` pads its output, which `[[ -eq ]]` arithmetic tolerates.
- `:104`, `:124`: `echo` of data that always starts with a literal (`Triage:` or `|`), so there is no option or backslash ambiguity in bash.
- `set -u`: `$classification` is read only on paths where it was assigned.
- `-maxdepth` is not POSIX but exists in both GNU and BSD `find`, which covers the macOS and Linux targets.

## Fixes Applied

None. Every `Edit` was refused by the auto-mode classifier (see above). The script is unchanged from 2152b28b.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| KD-3 / inline M3: `reports_count` excludes `review.md`, `review-*.md`, `final-review.md` | Satisfied | `triage-feedback.sh:27`; slice test passes |
| `review_artifact` still reports review presence | Satisfied | `:76-90` untouched |

KD-3 also changes behaviour on the Complex branch. A Complex run whose only reports are review-gate ones, with at most 2 changed files and `Behavioral code: no`, now reads `overclassified` where it used to read `match`. That is consistent with KD-3's "stop counting as execution evidence", and no test pins it.

## Positive Observations

- The exclusion set matches KD-3 exactly: no over-broad `*review*` that would swallow slice code-review reports.
- The line continuations keep the `find` primaries grouped by rationale: pre-execution artifacts on one line, review-gate reports on the next.
- shellcheck exit 0.

## Recommendations

Apply minor fixes 1-3 in a session where `Edit` on `plugin/bin/triage-feedback.sh` is permitted. Then run `shellcheck plugin/bin/triage-feedback.sh` and `PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_triage_feedback.py -v`.
