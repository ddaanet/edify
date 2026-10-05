# Review: Item 1.3 slice 1 — code review

**Scope**: the slice's committed change, the commit that adds
`plans/review-fixes-2/reports/item-1-3-s1-green.md`, diffed against its
parent. Its only code change is
`tests/test_changed_files.py::test_paths_with_space_and_non_ascii_bytes_are_listed_whole`
(+35 lines). The implementation the test pins is
`plugin/skills/build/scripts/changed-files.sh`, and the slice left it
unchanged.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The slice changed no implementation. The review therefore reads the test
against the script's NUL-delimited read and against the contract both
surfaces cite:

- build-fixes Item 1.2 Interfaces: "Paths are read from a NUL-delimited
  diff, never split on whitespace".
- deliverable-review finding M6, which names two mutants.

The three surfaces agree. The fixture, the exact expected stdout and the
docstring's account of each mutant's failure match the script and the
outline's slice text. A mutated-SUT run reproduced the red. I found no
in-scope defects and made no edits.

**Overall Assessment**: Ready

## Surfaces read against each other

- **Rule → test.** M6 requires that `my file.txt` is not split and that
  `café.txt` is not C-quoted, so an exempt `inbox/é.md` is still dropped.
  The fixture carries all three paths. The assertion compares the full
  `splitlines()` list, including `BASE: <pre-run sha>`, where `base_sha` is
  taken with `rev-parse HEAD` independently of the script. The expected
  order (`café.txt` before `my file.txt`) is git's byte order: `c` sorts
  before `m`.
- **Script → test.** In `changed-files.sh`, `git diff --name-only
  --no-renames -z … | while IFS= read -r -d '' path` feeds the
  `[[ $path =~ $exempt_re ]]` match, and the script prints each path with
  `printf '%s\n'`. The test expects the unquoted UTF-8 path on one line,
  which is what that loop prints.
- **Docstring → behaviour.** The docstring's "Item 1.2" is build-fixes Item
  1.2, the item that owns the NUL read. That matches the module docstring,
  which anchors to `plans/build-fixes/outline.md`. Its per-mutant
  observables (the split `my` / `file.txt`, the quoted
  `"caf\303\251.txt"`, the leaked quoted `inbox/é.md`) match the RED
  report's output and my run below. The docstring is `r"""`, so the octal
  escapes render literally (the test review's fix).
- **Encoding.** Every `é` in the test source is NFC (`303 251`). Python
  writes the fixture names NFC, so on macOS the source literal and git's
  output compare equal. `git init` sets `core.precomposeunicode` there,
  which keeps git's output NFC too.
- **Consumer.** `plugin/bin/triage-feedback.sh:23-39` splits the script's
  stdout on newlines only and counts lines with `wc -l`. That is consistent
  with the one-path-per-line format this test pins.

## Mutated-SUT run (once)

- Mutant: M6's second mutant, a newline `read` with `-z` dropped. The
  exact-string replacement in `changed-files.sh` was
  `git diff --name-only --no-renames -z "$base_sha" HEAD -- | while IFS= read -r -d '' path; do`
  →
  `git diff --name-only --no-renames "$base_sha" HEAD -- | while IFS= read -r path; do`.
  The mutation landed (grep count 1).
- Result: `0/1 passed`. The test reds at `tests/test_changed_files.py:267`,
  which is the stdout assertion, not the returncode assertion:
  `At index 1 diff: '"caf\\303\\251.txt"' != 'café.txt'`, with
  `"inbox/\303\251.md"` leaked.
- Restore: by the inverse replacement. Grep for the mutant line returns 0,
  and `git diff --exit-code` on the script is clean. The module then ran
  `6/6 passed`. `git status --porcelain` shows only the pre-existing entries
  and the sandbox phantoms.

The RED report records mutant 1 (the word-split `for`) reddening. The test
review records a third mutant of its own (`tr '\0' '\n'` with a word split)
reddening too. Every test in the slice (one) redded under the mutation run.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None that are new and in scope.

## The test review's minor issue 2 (my view; not applied)

My human partner's call, as dispatched. My view: add `back\slash.txt` to
this fixture.

- The repo already depends on the clause this path would pin.
  `changed-files.sh`'s own KD-6 comment says the read is "never split on
  whitespace or newlines". `triage-feedback.sh:50-53` justifies its own
  `-z` with "without `-z`, git C-quotes a name holding `"`, `\` or a control
  byte whatever `core.quotePath` says".
- Mutant A (`git -c core.quotepath=off` with a newline read) is the
  plausible regression. It is what someone would write to "fix"
  `café.txt` being quoted, and this fixture cannot tell it apart from the
  correct read.
- One more path closes both surviving mutants. Mutant B is `read` without
  `-r`.
- The cost: one more fixture path, and `back\slash.txt` first in the
  expected list.

One more survivor, from reasoning rather than a probe: dropping `IFS=` keeps
`-z` and `-r` and goes green on this fixture. The reason is that no fixture
path has leading or trailing whitespace. A ` lead.txt` path would pin it.
That mutant is less plausible, so I would not add the path unless the
fixture is reopened for `back\slash.txt` anyway.

## Refactoring signals

None. `tests/test_changed_files.py` is 271 lines, under the 400 cap. The
test reuses the module's `_init_repo`, `_commit`, `_run_git` and
`_run_script` helpers and adds none of its own.

## Fixes Applied

None. Because nothing changed, I did not run `just precommit`. The GREEN
report records `Precommit OK` (398/399 passed, 1 xfail) for this commit's
tree.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| M6: a test pins the NUL-delimited read; both named mutants red it | Satisfied | Mutant 1: RED report `Mutation proof`. Mutant 2: RED report, and this review's mutated-SUT run (red at `tests/test_changed_files.py:267`) |
| Slice 1: the run commit adds `item-1-1.md`, `my file.txt`, `café.txt`, exempt `inbox/é.md`; stdout is exactly `BASE: <pre-run sha>`, `café.txt`, `my file.txt` | Satisfied | `tests/test_changed_files.py:252-271` |
| Implementation unchanged by the slice | Satisfied | The commit's stat touches only the test and three reports |

**Gaps:** none within M6. Coverage beyond M6 (backslash and the read's
`-r` and `IFS=`) is recorded above for my human partner's decision.

## Positive Observations

- Each fixture path has one job. The space reds only the split mutants. The
  non-ASCII name reds only the quoting mutants. The exempt `inbox/é.md`
  turns the quoting failure into a filter leak, so its absence from the
  expected list is backed by a positive and is not a bare negative.
- The docstring names both mutants and the observable each produces, so a
  later reader can rerun the mutation proof from the test alone.
