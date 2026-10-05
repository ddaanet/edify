# Review: Item 1.3 slice 1 — test review

**Scope**: uncommitted `tests/test_changed_files.py` change
(`test_paths_with_space_and_non_ascii_bytes_are_listed_whole`) and
`plans/review-fixes-2/reports/item-1-3-s1-red.md`. `changed-files.sh` touched
only for mutation reproductions, each restored.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The test pins M6: the run commit's fixture and the exact stdout match the
runbook's slice spec, and the RED report records both named mutants reddening
on the stdout assertion. A reproduction with a third mutant of my own also reds
on that assertion. One gate-breaking defect was fixed: the docstring was not raw
(ruff D301), so `\303\251` rendered as `Ã©`. Two further NUL-discipline mutants
survive. Both lie outside M6's two named mutants, and one backslash path would
close them. That fix is recorded below, not applied.

**Overall Assessment**: Ready

## Mechanical check

- Against the unchanged script: module `6/6 passed`. The slice test passes, as
  it should for a mutation-red slice.
- RED report: `Mutation proof` covers both named mutants. Each was restored by
  the inverse replacement, with a grep proof and a green module recorded. The
  quoted assertion output for each is consistent with the fixture.
- Reproduction, mutant C (mine, distinct from both named mutants). `-z` is
  kept, so `café.txt` arrives unquoted and the exempt match still holds. The
  NULs are translated and the result is word-split:
  `for path in $(git diff --name-only --no-renames -z "$base_sha" HEAD -- | tr '\0' '\n'); do`.
  The mutation landed (grep count 1). The test reds at
  `tests/test_changed_files.py:267`, the stdout assertion, not the returncode
  one:

  ```
  E   AssertionError: BASE: e5feaa05328b79404883a748ebce6252d11901b6
  E     café.txt
  E     my
  E     file.txt
  E   At index 2 diff: 'my' != 'my file.txt'
  E   Left contains one more item: 'file.txt'
  ```

  This isolates `my file.txt` as the space's discriminator: `café.txt` and
  `inbox/é.md` play no part in this red. Restored by inverse edit. Proof: the
  grep for `tr '\0'` returns 0, `git diff --exit-code` on the script is clean,
  and the module is `6/6 passed`.

## Wrong-reason hunting

- **Exact assertion.** The whole `splitlines()` list is compared, with
  `BASE: <sha>` first. `base_sha` is `rev-parse HEAD` taken before the run
  commit, which is derived independently of the script. `returncode == 0` is
  asserted first, so an exit-2 path cannot pass.
- **Exempt drop has a positive.** `inbox/é.md` is absent from the expected
  list, and that absence is not a bare negative: under mutant 2 the same path
  leaks quoted. The fixture therefore carries the exempt rule's trigger.
- **Each named mutant has its own discriminator.** Mutant 1 reds on both the
  split and the quoting. Mutant 2 reds only on the quoting (`"caf\303\251.txt"`
  and the leaked `"inbox/\303\251.md"`). Mutant C reds only on the split. No
  single path is carrying both mutants.
- **Surviving mutants** (probed, each restored and proven):
  - Mutant A drops `-z`, reads newline-delimited and adds
    `git -c core.quotepath=off`. Result: `1/1 passed`. `quotepath=off` leaves
    `é` and the space raw, so this fixture cannot tell it apart.
  - Mutant B keeps `-z` and drops `-r` from `read`. Result: `1/1 passed`.
    None of the fixture paths holds a backslash. Shellcheck flags it (SC2162),
    but only through the in-session hook: no `just` recipe runs shellcheck.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Docstring with backslashes not raw**
   - Location: `tests/test_changed_files.py:242`
   - Note: the `"""` docstring holds `"caf\303\251.txt"`. Python decodes the
     octal escapes, so the docstring reads `"cafÃ©.txt"`, which misstates git's
     quoted form. Ruff reports D301, which fails `just precommit`. The module's
     other backslash docstrings already use `r"""`.
   - **Status**: FIXED

2. **Mutants A and B survive the slice's fixture**
   - Location: `tests/test_changed_files.py:239-271`
   - Note: both drop part of the NUL discipline, the raw `-z` stream and the
     backslash-safe read. Neither is among M6's two named mutants. Mutant A is
     the plausible one: it is what someone would write to "fix" `café.txt`
     being quoted. One added run-commit path, `back\slash.txt`, reds both.
     Probed in a scratch repo, git 2.47.3: mutant A prints
     `"back\\slash.txt"`, mutant B prints `backslash.txt`, and the correct read
     prints `back\slash.txt`. Git escapes a backslash whatever
     `core.quotePath` says.
   - **Status**: OUT-OF-SCOPE — Item 1.3's requirement is M6, which names
     exactly the two mutants the test reds. The runbook pins the slice's run
     commit and its exact stdout. Adding the path changes that pinned contract,
     so it is not a strengthening "within the slice's fixture". The orchestrator
     or a follow-up item should decide: add `back\slash.txt` to this fixture,
     with `back\slash.txt` sorted first in the expected list, or open a sibling
     slice.

## Fixes Applied

- `tests/test_changed_files.py:242`: `"""` changed to `r"""`. `ruff check`
  and `ruff format --check` pass, and the module is `6/6 passed`.

## Line caps

`tests/test_changed_files.py` is 271 lines, under the 400 cap.

## Tree state

`changed-files.sh` is byte-identical to HEAD (`git diff --exit-code` clean
after each restore). `git status --porcelain` shows only the pre-existing
entries, plus ` M tests/test_changed_files.py` and the untracked RED report.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| M6: pin the NUL-delimited read; both named mutants red | Satisfied | RED report `Mutation proof`; reproduction with mutant C above |
| Slice 1: fixture and exact stdout | Satisfied | `tests/test_changed_files.py:253-271` match the outline verbatim |

**Gaps:** none within M6. The mutant A/B gap beyond M6 is recorded under minor
issue 2.

## Positive Observations

- The RED report explains why each fixture path is needed, and each one is
  confirmed by which mutant it alone reds.
- The docstring names both mutants and the observable each one would produce.
