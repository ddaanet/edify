# Review: Item 1.3 slice 2 — test review

**Scope**: `test_uncommitted_definition_is_not_behavioral` in
`tests/test_triage_feedback.py` (uncommitted diff), RED report
`plans/build-fixes/reports/item-1-3-s2-red.md`. SUT
`plugin/bin/triage-feedback.sh` OUT and untouched.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The RED was genuine: the test failed on its `Behavioral code: no` assertion,
with no error. But the positive pairing did not exercise the `<base> HEAD`
range. Its repo had exactly one commit after the baseline, and that commit
held the `def`. So an implementation diffing only the last commit read `yes`
on the positive and `no` on the negative, and passed the whole test. A
variant run showed it. The test now builds both repos from one fixture helper,
and the positive adds a trailing plain-text commit. Every wrong variant now
fails and the correct one passes.

**Overall Assessment**: Ready

## Mechanical check

- The RED report shows FAILED on
  `assert "- Behavioral code: no" in lines`, output `Behavioral code: yes`.
  It is not PASSED and not ERROR. `_triage_lines`'s `returncode == 0` held.
- After the fixes, a re-run gives the same result:
  `test_uncommitted_definition_is_not_behavioral FAILED`, with an
  `AssertionError` on `'- Behavioral code: no'` against `- Behavioral code:
  yes`. The other two tests in the file PASSED (2/3 passed).

## Wrong-reason analysis

**The state that fails the test once the fix is in:** the
behavioral-code diff reaches uncommitted state, either the working tree or
the index. The negative then reads `yes`. Or the diff misses committed
history before HEAD, or the regex misses `def`. The positive then reads `no`.

**Regex check.** `definition_re` matches the diff line `+def foo():`. The
`^\+`, then zero modifiers, then `def`, then a space. The same holds for
`+def bar():`. None of the plain lines match the regex: `+x = 1`, `+y = 2`,
`+seed`, `+plain text`, `+    pass`. `shell_fn_re` matches none of them. The
current RED (`yes`, with uncommitted `def` lines as the only definitions in
reach) shows directly that the regex matches the exact lines in the fixture.

**Tracked check.** `module.py` and `other.py` are committed, with no
definition, before the `def` edits. Both edits are diffs on tracked files,
not untracked paths that `git diff` would skip anyway.

**Variant matrix.** I ran these in scratch copies of the SUT, not the tracked
file, with the behavioral-code `git diff` line swapped for each variant:

| Variant | Before fix | After fix |
|---|---|---|
| `git diff "$base"` (current, working tree) | FAIL (negative) | FAIL (negative) |
| `git diff "$base" HEAD` (intended) | PASS | PASS |
| `git diff HEAD~1 HEAD` (last commit only) | **PASS** | FAIL (positive) |
| `git diff --cached "$base"` (index) | FAIL (negative) | FAIL (negative) |
| `git diff HEAD` (uncommitted only) | FAIL (positive) | FAIL (negative) |
| regex never matches | FAIL (positive) | FAIL (positive) |

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The positive pairing passes when only the last commit is diffed**
   - Location: `tests/test_triage_feedback.py`, positive block of
     `test_uncommitted_definition_is_not_behavioral`
   - Problem: the positive repo's only post-baseline commit carried the
     `def`. So `git diff HEAD~1 HEAD` and `git show HEAD` gave the same
     answer as `<base> HEAD`. The negative's last commit is plain text, so
     that variant reads `no` there too. That implementation is plausible but
     forbidden, and it passed the test.
   - Fix: after the `def` commit, the positive lands a plain-text commit
     (`notes.txt`). The `def` is then in `<base>..HEAD` but not in the last
     commit.
   - **Status**: FIXED

2. **Positive and negative were not paired over one fixture**
   - Location: same test
   - Problem: the positive put a new `module.py` holding only `def foo():`
     in one commit. The negative tracked plain `module.py` and `other.py`
     and then edited both. The two fixtures differed in more than the
     trigger (committed vs uncommitted). The negative's `def bar():` line
     and staged path had no positive counterpart.
   - Fix: a new `_def_edits_pending(repo)` helper builds both repos. It
     tracks plain `module.py` and `other.py`, then adds `def foo():`
     unstaged and `def bar():` staged. The positive differs only by
     `git commit -a` of those same edits, plus the trailing plain commit.
   - **Status**: FIXED

### Minor Issues

1. **The positive ran before the negative**
   - Location: same test
   - Note: a failing positive aborts the test before the negative runs. The
     negative's verdict was then never its own (test-discipline,
     non-vacuous-negatives, "Ordering under errexit"). The negative now runs
     first. The docstring states the order and why.
   - **Status**: FIXED

2. **Docstring did not name the last-commit-only case**
   - Location: test docstring
   - Note: I rewrote it to describe the shared fixture, and to list the three
     wrong implementations the positive rules out: a regex that misses,
     uncommitted-only, and last-commit-only. The narration comments
     (`# Unstaged uncommitted def.` and the staged one) went away with the
     move into the helper, whose docstring says the same.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_triage_feedback.py`:
  `test_uncommitted_definition_is_not_behavioral`. Both repos now come from
  `_def_edits_pending`. The negative assertion runs first. The positive
  commits the same edits with `-a` and adds a trailing plain-text commit, then
  asserts `yes`. The docstring is rewritten.
- `tests/test_triage_feedback.py`: new `_def_edits_pending(repo) -> str`,
  placed after its user.

## Lint / size

- `ruff check`: all checks passed. `ruff format --check`: already formatted.
- `docformatter -c`: clean. My first helper summary went past the
  80-column wrap, so I shortened it.
- The file is 212 lines.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m18 / KD-6 (behavioral-code diff is `"$baseline_commit" HEAD`) | Pinned by the test | negative fails against the current working-tree diff; every neighbouring range fails one assertion |

## Positive Observations

- The RED report explained why it chose two repos over one: a committed `def`
  in a shared repo would make the negative impossible. That reasoning still
  holds, and the shared helper keeps the two-repo design.
- Covering staged and unstaged edits in separate files caught the
  index-diff variant, which an unstaged-only fixture would miss.
