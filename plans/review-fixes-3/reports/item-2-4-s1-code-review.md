# Review: Item 2.4 slice 1, code review

**Scope**: the GREEN commit's five prose edits (`phase-boundary.md` §Base and
changed files, `tdd-slice.md` GREEN-commit query, `escalation.md` §Resuming
step 1 with its `just format` reflow, `tdd-auditor.md` check 2,
`docs/references/build-run-state.md` D-88 and D-89 query blocks) and
`tests/test_build_prose_git_log.py`
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

Every hash-reading `git log … --format=%H` in the six scanned files now carries
`--no-show-signature`, placed right before `--format=%H` as in `finishing.md`,
and no other wording changed. The test runs the prose's own commands against a
signed history and finds every `--format=%H` site. One sibling site was
missing: D-86's query block in `docs/references/pipeline-contracts.md` repeats
`tdd-slice.md`'s query word for word, still lacked the flag, and was not in
the scanned set. It is now fixed and pinned.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **D-86's slice-commit query has no `--no-show-signature`, and no test
   checks it**
   - Location: `docs/references/pipeline-contracts.md:259` (D-86);
     `tests/test_build_prose_git_log.py` `SCANNED`
   - Problem: D-86 records the query that resolves the slice commit,
     `git log --diff-filter=A --format=%H -- plans/<job>/reports/item-N-M-s<k>-green.md`.
     This is the command `tdd-slice.md` runs. After the GREEN commit the
     decision record and the prose it records no longer matched: the prose
     carries the flag and the record does not. That is the m14 seam between
     prose and decision, the same reason D-88 and D-89 are in the item's file
     list. KD-7 lists its sites (phase-boundary, D-88, D-89, tdd-auditor check
     2, tdd-slice, escalation §Resuming step 1) and leaves D-86 out. This is a
     planning gap in the outline, not a GREEN defect. A repo-wide search for
     `git log … --format`/`--pretty` without the flag (excluding `plans/`,
     `dist/`, `tmp/`, `scratch/`) found only this site.
   - Fix: add `--no-show-signature` before `--format=%H` in the D-86 block,
     the same position as in `tdd-slice.md`. Add
     `docs/references/pipeline-contracts.md` to `SCANNED` so the block is
     tested like the others. The file has one `--format=%H`, and extraction
     finds one command, so the `:missed` guard stays quiet. The test now has
     10 parametrized cases instead of 9.
   - **Status**: FIXED

### Minor Issues

None.

## Fixes Applied

- `docs/references/pipeline-contracts.md:259`: added `--no-show-signature` to
  D-86's query block. No other wording changed.
- `tests/test_build_prose_git_log.py` `SCANNED`: added
  `docs/references/pipeline-contracts.md` after `build-run-state.md`.

## Verification

- **Word-level diff of the GREEN commit** (each file's parent and commit
  versions split on whitespace, then diffed): each of the five files gains
  exactly one token, `--no-show-signature`. `build-run-state.md` gains two,
  one per block. `escalation.md`'s reflow changed line breaks only. No reason
  sentence was added to D-88, which stays with Item 4.1.
- **Flag placement**: every site reads `… --no-show-signature --format=%H …`.
  The three `finishing.md` commands use the same order.
- **Extraction completeness**: the number of `--format=%H` occurrences in each
  scanned file equals the number of extracted cases: phase-boundary 1,
  tdd-slice 1, escalation 1 (inline span), tdd-auditor 1, build-run-state 2,
  pipeline-contracts 1, finishing 3. The `git log` mentions in `tdd-auditor.md`
  §Inputs (lines 60–61, 227) are tool lists without `--format=%H`, so KD-7
  correctly excludes them.
- **Test discrimination**: the fixture checks its own discriminating state.
  Every commit has `%G?` = `G`, and a bare `git log -1 --format=%H` prints a
  non-hash line. Expectations are exit 0, non-empty stdout, and every line a
  40-hex sha. A `<…>` left after substitution fails the test.
- **Mutated-prose run (once)**: I removed `--no-show-signature` from D-86's
  block by exact string replacement, the inverse of the fix above. I picked
  this site because it was the only pin never seen red. The other sites'
  reds, including escalation's inline span, are in the RED report. With the
  mutation, `command grep` found the unflagged line at
  `pipeline-contracts.md:259`. Result: 1 failed, 9 passed. Only
  `pipeline-contracts.md:1` failed, on the non-hash-lines assertion
  (`Good "git" signature for test@example.com with ED25519 key …`). Every
  other case stayed green.
- **Restore**: I re-added the flag with the inverse Edit. `command grep` for
  `git log --diff-filter=A --format=%H` in `pipeline-contracts.md` then found
  nothing (rc 1).
- **Gate**: `PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`
  printed `Precommit OK`. Tests were not cached: 431/432 passed, 1 xfail
  (pre-existing). Version consistency 0.3.0. Design links: 94 decisions
  indexed, defined once, conclusions match, 9 nodes present. Line limits gave
  only the existing oversized warnings for `corrector.md` (682),
  `outline-corrector.md` (450) and `design-corrector.md` (460). None of these
  files was touched.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m14 (KD-7): every hash-reading `git log` `/build` reads prints hashes only on signed history | Satisfied | All 10 extracted commands pass on a `log.showSignature=true` signed repo; D-86 gap closed above |
| Item 2.4 GREEN: flag added, no other wording changed | Satisfied | word-level diff shows only the flag token |
| `finishing.md` stays pinned as regression | Satisfied | `finishing.md:1–3` pass, file untouched |

**Gaps:** none remaining.

## Positive Observations

- The `:missed` case compares extracted commands with the raw `--format=%H`
  count. An extractor that drops a command shape fails the test; it cannot
  pass vacuously.
- `_git_env` removes all of `GIT_CONFIG*`, including `GIT_CONFIG_PARAMETERS`
  and `GIT_CONFIG_COUNT`. Inherited config therefore cannot turn
  `log.showSignature` off and leave every case vacuously green.

## Recommendations

- For the orchestrator: KD-7's site list in the outline left out D-86. Item
  4.1 (D-88 reason sentence, "covers every `git log` `/build` reads") can rely
  on the scanned set now including `pipeline-contracts.md`.
- No refactoring flagged.
