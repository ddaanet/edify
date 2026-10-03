# Review: Item 1.4 slice 3 — `--phase` list keeps the filters

**Scope**: `plugin/skills/build/scripts/changed-files.sh`, the whole script as
it stands after 8365eb53. The slice changed no implementation: it added
`test_phase_list_keeps_the_filters` only. The tests are out of scope and were
not edited.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The filter path is shared. `--phase` does one thing: it reassigns `base_sha`
inside the `[[ ${2:-} == --phase ]]` block. After that block there is one
`printf 'BASE:'` and one `git diff -z` read loop, which applies the
`plans/<job>/` drop and the exempt match. No second list path exists to drift.
The script matches Item 1.2's interface line and KD-6's `--phase` sentence.
I found one genuine defect, a minor one: the KD-1 `item-*` pathspec still
lacked the `:(glob)` magic that slice 2 gave the phase query. I also made
two header-comment fixes, for accuracy and so that each rule is stated once.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **The KD-1 pathspec `*` crossed `/`, so a non-report file could set the
   run base**
   - Location: `changed-files.sh:83`, the `first_commit` query
   - Problem: the phase query got `:(glob)` in the slice-2 code review, but
     the item query had the same exposure and was left as it was. Probed on
     a throwaway repo before the fix. A commit adding
     `plans/j/reports/item-x/notes.md` and `pre.txt`, made ahead of the first
     real `item-1-1.md` commit, became "the first item report commit". The
     script printed the parent of that commit as `BASE:` and listed
     `pre.txt`, which is not run work. With only that file committed, the
     script printed `BASE:` where KD-1 calls for `NO-BASE:`. A file under
     `reports/item-x/` is not an item report. The error runs in the safer
     direction (an earlier base over-reports), but it is the same rule
     slice 2 fixed for the phase query. Left as it was, the two queries
     differed in magic for no stated reason, and a later reader could have
     "harmonised" `:(glob)` away.
   - Fix: give the item pathspec `:(glob)` too, and state the rule once for
     both queries.
   - **Status**: FIXED. Re-run of the same probe after the fix: `BASE:` is
     the parent of the `item-1-1.md` commit, the list is `a.txt` alone, and
     the directory-only repo gives `NO-BASE:` with exit 1. No test pins this
     behaviour, and the test files are outside my scope (see
     Recommendations).

2. **The header stated the `:(glob)` rule for one query only**
   - Location: header, KD-1 and `--phase` paragraphs
   - Problem: once both queries carry the magic, keeping its reason in the
     `--phase` paragraph would leave the KD-1 query's magic unexplained.
     Repeating the reason in both places would state it twice.
   - Fix: move the reason into the KD-1 paragraph, worded for both pathspecs
     (`reports/item-x/notes.md` as an item report,
     `reports/phase-1/old-corrector.md` as a boundary), and drop it from the
     `--phase` paragraph. In its place the `--phase` paragraph now says that
     either base feeds the one print-and-filter path. That invariant is what
     this slice pins.
   - **Status**: FIXED

3. **The KD-6 parenthetical was garbled, and "the log" became wrong once
   there were two logs**
   - Location: header, KD-6 paragraph
   - Problem: "a run commit can also carry a `/handoff` or memory-pointer
     commit's exempt paths" describes one commit carrying another commit's
     paths. KD-6 actually says that the range `<base>..HEAD` can hold such a
     commit. Also, "`--no-renames`, on the diff and the log alike" dates from
     before slice 2. Both log queries now pass `--no-renames`.
   - Fix: "the range can also hold a `/handoff` or memory-pointer commit,
     whose exempt paths are not the run's own work", and "on the diff and
     both logs alike".
   - **Status**: FIXED

## Scope questions answered

- **One filter path, or two?** One. The block at lines 100–108 only
  reassigns `base_sha`, and lines 110–126 run whatever the base is. The
  mutated-SUT run below shows that the slice's test catches the drift shape:
  a filter that applies to only one of the two calls.
- **Item 1.2 interface line.** `<job> [--phase]`: the argument guard admits
  1–2 arguments, with `--phase` only as the exact second one, and the `case`
  rejects `--phase` as a job. Exit 0 prints `BASE: <sha>` and then one path
  per line. Exit 1 is `NO-BASE:` only: every other failure maps to exit 2
  `ERROR:`. That covers the source of `exempt-paths.sh`, `rev-parse`, `cd`,
  both logs, the parent lookup, the `BASE:` write, and the diff pipeline,
  where a failed `printf` in the loop body exits the subshell, `pipefail`
  carries the status, and the `|| exit 2` catches it. Paths come from
  `git diff -z` with `read -r -d ''`. `--phase` takes the phase base.
  Satisfied.
- **KD-6 `--phase` sentence.** The base is the latest commit in
  `<run base>..HEAD` touching `plans/<job>/reports/phase-*-corrector.md`, or
  the run base when no such commit exists, and the list is the same filtered
  diff since that base. Satisfied. `exempt-paths.sh` is the one sourced home
  of the alternation, and `verify-step.sh` reads it too.
- **Header read top to bottom.** These rules are each stated once: the KD-1
  query and its flags (`--no-show-signature` and, after the fix, `:(glob)`);
  the exit-code contract; the KD-6 filters; NUL reading; `--no-renames`; the
  in-loop exempt match; the newline residual bound; the KD-2 query. The
  inline comments (job validation, the `BASH_SOURCE` locator, root `cd`,
  root-commit error, `BASE:` write failure, the `--` before the diff
  pathspec) each cover a local point that the header does not repeat.
  bash-3.2 portability holds: `[[ =~ ]]` with the regex in a variable,
  `read -d ''`, `$'\n'` in a parameter expansion, no arrays beyond
  `BASH_SOURCE`.

## Mutated-SUT run

Mutation, one exact-string Edit:
`    if [[ $path =~ $exempt_re ]]; then` →
`    if [[ ${2:-} != --phase && $path =~ $exempt_re ]]; then`. This is the
plausible-but-forbidden shape: the exempt filter survives on the bare call
and is lost under `--phase`. That is what a second, drifting code path would
produce. It differs from the RED report's mutations, which disabled each
filter for both calls.

- `test_phase_list_keeps_the_filters`: **red**. The list gained
  `.claude/handoff-task.md`, `inbox/x.md` and `memory`.
- All bare-call tests in `tests/test_changed_files.py`, and the other phase
  tests: green, as expected, since the bare filter is intact.

Restored with the inverse exact-string Edit. Proof of the restore: `grep -c`
of `!= --phase &&` returns 0, `grep -nF` finds the original line at `:119`,
shellcheck `-x` is clean, and `test_changed_files.py`,
`test_changed_files_phase.py` and `test_verify_step.py` give 15/15 passed.

## Fixes Applied

- `changed-files.sh:83`: pathspec `"plans/$job/reports/item-*"` →
  `":(glob)plans/$job/reports/item-*"`.
- `changed-files.sh:9-15`: the `:(glob)` reason now sits in the KD-1
  paragraph and covers both pathspecs.
- `changed-files.sh:18-20`: the KD-6 parenthetical is reworded to say that
  the range holds the `/handoff` or memory-pointer commit.
- `changed-files.sh:22`: "the log" → "both logs".
- `changed-files.sh:36-38`: the `--phase` paragraph drops its copy of the
  `:(glob)` reason and states the shared print-and-filter path.

Verification: shellcheck `-x` is clean. The three script test modules give
15/15. `just precommit` passes: `Precommit OK`, 378/379 passed, 1 xfail. The
only warnings are the three pre-existing oversized-file warnings on
`plugin/agents/*corrector.md`.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 1.4/3: exempt-path and `plans/<job>/` filters apply under `--phase` | Satisfied | the shared loop at `:113-126`; `test_phase_list_keeps_the_filters`, which reds under the phase-only mutation above |
| Item 1.4/3 list revision: pin the slice-2 `:(glob)` fix | Satisfied | the decoy commit in the same test (RED report mutation 3) |
| Item 1.2 interface: exits 0/1/2, NUL paths, `--phase` | Satisfied | see Scope questions |
| KD-6 `--phase` sentence | Satisfied | `:100-108` |
| KD-1: base from the first `item-*` report | Satisfied after fix | `:83` with `:(glob)` |

**Gaps:** none.

## Positive Observations

- `--phase` changes a single variable. That is the strongest structural
  guarantee available that the two lists share their filters, and the
  slice's test catches the one way that guarantee could erode.
- The RED report's decoy deviation (`phase-9/old-corrector.md` in place of
  the prompt's `sub/phase-9-corrector.md`) is grounded in the slice-2 probe,
  and the test's docstring records it.

## Recommendations

- The `:(glob)` fix on the KD-1 query is not pinned. A one-commit addition to
  `test_base_is_parent_of_first_item_report_commit` would pin it: an earlier
  commit adding `plans/j/reports/item-x/notes.md` together with a non-plans
  file, where the asserted `BASE:` and list stay unchanged. That test file is
  outside this review's scope, and this was the last `changed-files.sh`
  slice. Whether to add it is the orchestrator's call.
- The outline's KD-1 text spells the query without `:(glob)`, as KD-2's text
  does. Item 2.14 records both decisions. Its executor should carry the magic
  into the recorded queries, or the decision record and the script will
  disagree.

REFACTOR-NEEDED: none.
