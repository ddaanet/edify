# Review: Item 1.1 slice 4 code review — unrecognised label

**Scope**: HEAD `32a9767b`'s change to `plugin/bin/triage-feedback.sh`: the
exact-label branch in the verdict chain, `unrecognised_label`, and the
`unrecognised classification: <label>` line. The script was re-audited where
it changed. Tests are out of scope.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The exact-label check is correct. Only an exact `Simple`, `Moderate`,
`Complex` or `Defect` reaches the verdict rules, and those rules are
unchanged. An unrecognised label leaves the verdict `no-classification`,
which the log block already skips. One defect: the label was printed with
`echo`, which mangles a backslash when `xpg_echo` is on. It is now printed
with `printf`. In-place mutation proves the test reds on a prefix-match
allowlist.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Label printed with `echo`**
   - Location: `plugin/bin/triage-feedback.sh:197`
   - Note: `echo "unrecognised classification: $unrecognised_label"`. A label
     starting with `-` is safe, because the fixed prefix is the start of
     echo's operand. A backslash is not safe: bash's `echo` expands escapes
     when `xpg_echo` is on, and `BASHOPTS=xpg_echo` in the environment turns
     it on at startup. Probe, `env BASHOPTS=xpg_echo bash -c …` on the label
     `a\tb`: the `echo` form printed a TAB, while
     `printf 'unrecognised classification: %s\n'` printed `a\tb` literally.
     The fixed script was then run under `BASHOPTS=xpg_echo` on a fixture
     whose label parses to `X\tY`, and printed `X\tY` byte for byte.
   - **Status**: FIXED — `printf 'unrecognised classification: %s\n'
     "$unrecognised_label"`. This matches the script's own
     `printf '%s\n' "$changed_output"` and shell-gotchas rule 5. Under
     default bash options the output is the same, so no current test
     distinguishes the two forms, and none was added. A test cannot pin it
     yet: the parse's `xargs` rewrites every backslash before the line
     prints, and no file content survives `xargs` with a backslash intact.
     Slice 5 removes `xargs`. See Recommendations.

## Points checked, no change needed

- **Placement.** `## Verdict` and the verdict come first, then a blank line
  and the unrecognised line, then the divergence line, then `WARNING:`. The
  unrecognised line prints only when the verdict is `no-classification`, so
  it never appears together with the divergence line. Its position between
  the verdict and `WARNING:` keeps `## Verdict`'s first line the verdict, as
  the Interfaces block requires.
- **No row.** The append is gated on `verdict != no-classification`, and the
  new branch sets the verdict to `no-classification`. Nothing else on this
  path writes to the log.
- **Verdict chain for the four classes.** The new `elif` sits between the
  empty check and the `Simple` branch, and lets only the four exact labels
  through. The Simple, Complex and else (`match` for Moderate and Defect)
  branches are byte-identical to the parent commit. The empty value still
  takes the first branch, with no unrecognised line.
- **Bash 3.2.** The comparison uses four `!=` comparisons inside `[[ ]]`,
  with a newline after `&&`. It does not use an extglob `@(...)`, which
  bash 3.2 cannot parse without `shopt -s extglob`. The `!=` operands are
  quoted, so each is an exact string compare, not a pattern.
- **Shellcheck**: clean.

## Mutated-SUT run

The SUT was mutated in place: `"$classification" != "Simple" &&` became
`"$classification" != Simple* &&`, a plausible prefix-match allowlist. Then
`test_unrecognised_label_is_no_classification` ran:

- It redded at `tests/test_triage_feedback.py:278` with
  `assert 'match' == 'no-classification'`.
- The mutation was restored by the inverse edit. `git diff` then showed only
  the `printf` fix.
- After the restore, `tests/test_triage_feedback.py` and
  `tests/test_triage_feedback_behavioral.py` passed 12/12.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:197`: `echo` became
  `printf 'unrecognised classification: %s\n'`, so the label prints
  verbatim under any `echo` behaviour.

Files changed: `plugin/bin/triage-feedback.sh` only.

## Gate

- `just precommit`: `Precommit OK`, with 390/391 passed and 1 xfail.
- The precommit run printed `oversized-file` warnings for files this slice
  did not touch: `plugin/agents/corrector.md` 682, `outline-corrector.md`
  450 and `design-corrector.md` 460, each against a cap of 400.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| N-1: only an exact class is a class | Satisfied | `triage-feedback.sh:144-147` |
| N-1: `unrecognised classification: <label>` line | Satisfied | `triage-feedback.sh:195-198` |
| N-1: no row on that path | Satisfied | log block gated on `no-classification` |
| KD-1 verdict rules unchanged | Satisfied | Simple/Complex/else branches unchanged |

## Recommendations

- Slice 5's verbatim-label case: add a backslash to the label next to the
  apostrophe, and run that case once with `BASHOPTS=xpg_echo` in the
  environment. Once `xargs` is gone, that case pins the `printf` form. Swap
  `printf` back to `echo` to get the mutation red.

No REFACTOR-NEEDED.
