# Review: build-defects Items 1.1 and 1.2 — scripts and their tests

**Scope**: `git diff f44ddbbf -- plugin/bin/triage-feedback.sh plugin/skills/build/scripts/verify-step.sh tests/test_triage_feedback.py tests/test_verify_step.py` (committed), against `plans/build-defects/outline.md` KD-3, KD-7 and Items 1.1–1.2
**Date**: 2026-09-26
**Mode**: review + fix

## Summary

Both scripts implement their decisions as written. `triage-feedback.sh`
excludes `review.md`, `review-*.md` and `final-review.md` from
`reports_count` and leaves `review_artifact` alone. `verify-step.sh` treats
every porcelain line under `--untracked-files=all` as dirt except the three
KD-7 paths. It rejects `R`/`C` lines, allows git's quoting, echoes the
matched lines on DIRTY, and exits 2 when `git status` fails or `just` is
missing. Every fix the per-slice reviews routed (F-1, F-2, F-3 and Item 1.1's
three minors) is present in the committed scripts. The review found one test
gap: the `memory` exemption, the only one that fires in this repo every
session, was pinned by no test. Deleting it from the pattern passed the whole
suite. A test now pins it.

**Overall Assessment**: Ready

## Evidence gathered

- `shellcheck` on both scripts: clean.
- The two test files before the fix: 6/6 passed.
- Mutation runs used scratch copies with the test module's `SCRIPT` rebound.
  The tracked script was never touched. With `memory|` deleted from `exempt`,
  all 5 `verify-step` tests passed. With `memory.*` substituted, all 5 also
  passed.
- Cross-surface read (rule / enforcer / consumer):
  - The rule is KD-7, restated in `SKILL.md` §2 at lines 56–60.
  - The enforcer is `verify-step.sh`.
  - The consumers are `escalation.md` §Post-item remediation, and the
    `git commit -- <paths>` form at `SKILL.md:134`,
    `dispatch-composition.md:35`, `test-driver.md:103`, `refactor.md:184`,
    `finishing.md:54` and `phase-boundary.md:38`.

  The script's comment claims exempt dirt never enters a commit, even when
  staged. That claim now holds on every committing surface, which settles
  slice 1's UNFIXABLE (option a). Exit 2 means "no verdict" in both
  `SKILL.md` §2 and `escalation.md`, and that matches all three exit-2 paths
  in the script.
- KD-3 names against the naming rule: `dispatch-composition.md` §Naming
  gives `review-<group>` and `final-review`, and item 5 derives
  `reports/<dispatch name>.md` from them. Both fall inside the exclusion.
  Slice reports such as `item-N-M-s<k>-code-review.md` do not start with
  `review-`, so they still count. That is Q-2's territory, not this item's.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The `memory` gitlink exemption is unpinned**
   - Location: `tests/test_verify_step.py`, which has no test for it before
     the fix. The pattern is at `plugin/skills/build/scripts/verify-step.sh:19`.
   - Problem: the requirement names three exemptions "in any porcelain
     state". The tests pin `.claude/handoff-*.md` and `inbox/*.md` but never
     put a gitlink in the fixture. Two mutations survived the whole suite:
     deleting `memory` from the pattern, and widening it to `memory.*`.
     The slice 1 test review left this as a residual because "` M memory`
     [is] already implemented in the pre-fix script". That reason no longer
     holds. GREEN replaced the `grep -vx ' M memory'` line with the new
     regex, so nothing of the pre-fix implementation remains to lean on. The
     widened "any state" behaviour (`MM memory`, the state this repo's
     gitStatus showed at dispatch) was never exercised.
   - Fix: add `test_memory_gitlink_is_clean_and_a_sibling_name_is_not`. It
     builds a real nested repo at `memory`, records it as a gitlink, stages
     a bump and commits again inside it, and pins the porcelain as
     `MM memory`. It then asserts exit 0, `CLEAN:` and one `precommit`
     call. Its decoy phase adds an untracked `memory.md` and asserts exit 1
     with a DIRTY listing of exactly `?? memory.md`. The positive and the
     decoy share one fixture and differ only in the exemption's trigger.
   - **Status**: FIXED. Against the real script the test passes. It fails
     against four mutants:
     - `memory` removed: DIRTY on the clean phase.
     - `memory.*`: CLEAN on the decoy phase.
     - The pre-KD-7 ` M memory`-only form: DIRTY on the clean phase.
     - A pattern that also exempts `memory\.md`: CLEAN on the decoy phase.

### Minor Issues

1. **`_run_git` is copied verbatim into a third module**
   - Location: `tests/test_triage_feedback.py:21-39` and
     `tests/test_verify_step.py:21-39`, both identical to
     `tests/review_range_helpers.py:18-36`. The two `_init_repo` functions
     differ only in their seed content.
   - Note: all three copies are the same D-21 helper. A shared git-fixture
     helper would remove the copies, but it has to live in
     `tests/review_range_helpers.py`, `tests/pytest_helpers.py` or a new
     module, and none of those is a Changed file. Importing a private helper
     from another script's fixture module would couple two unrelated suites.
   - **Status**: DEFERRED. The fix location is outside the Changed files,
     which are Scope OUT. REFACTOR-NEEDED: `tests/review_range_helpers.py`,
     `tests/test_triage_feedback.py`, `tests/test_verify_step.py`. Extract
     `_run_git` into one shared test helper and import it from all three.

## Deferred Items

The following items were identified but are out of scope:

- **Shared git test helper**: covered in Minor 1 above. The Scope OUT that
  applies is "every file not in the Changed files list".

These items are recorded as Scope OUT and not raised: the `C` half of the
`[^RC]` guard, unmerged exempt paths, the unbalanced-quote acceptance, the
`xargs` / `|| true` item, RUF100, Q-1/Q-2 and sandbox masks.

## Fixes Applied

- `tests/test_verify_step.py`: added
  `test_memory_gitlink_is_clean_and_a_sibling_name_is_not` before
  `test_rename_out_of_exempt_path_is_dirty`. It pins the `memory` exemption
  in the `MM` state and adds a `memory.md` decoy (Major 1).
- `just precommit` (foreground): 367/368 passed, 1 xfail, and
  `Precommit OK`. It reported three `oversized-file` lines for agent
  definitions; those files are not in this changeset.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| KD-3: `reports_count` excludes `review.md`, `review-*.md`, `final-review.md` alongside `review-skip.md` | Satisfied | `triage-feedback.sh:25-28`; `test_simple_with_review_reports_matches` (0, then 1 with a slice report) |
| KD-3: review presence stays in `review_artifact` | Satisfied | `triage-feedback.sh:76-90` unchanged |
| KD-7: any change is dirt, untracked included, `--untracked-files=all` | Satisfied | `verify-step.sh:20`; slice 1 inbox phase (`?? inbox/notes.txt`) |
| KD-7: `memory`, `.claude/handoff-*.md`, `inbox/*.md` exempt in any state | Satisfied | `verify-step.sh:19`; `MM` handoff, untracked inbox and now `MM memory` pinned |
| Rename out of an exempt path is dirt | Satisfied | `[^RC][^RC]`; `test_rename_out_of_exempt_path_is_dirty` |
| Git-quoted exempt paths are exempt | Satisfied | `"?…"?`; `test_quoted_exempt_path_is_clean` with its `.txt` decoy |
| Failed `git status` → exit 2 | Satisfied | `verify-step.sh:20-23`; `test_git_status_failure_exits_2` |
| Missing `just` → exit 2 | Satisfied | `verify-step.sh:45-48`; `test_missing_just_exits_2` |
| DIRTY echoes the matched porcelain lines | Satisfied | `verify-step.sh:40`; exact-listing assertions in every DIRTY phase |
| Tests: real `git` in `tmp_path`, script by path, CWD at repo root | Satisfied | `_run_script` / `_triage_lines` in both files |

**Gaps:** none after the fix.

---

## Positive Observations

- Every DIRTY phase asserts the exact listing, not a substring. That proves
  exempt lines are filtered out of the echo, not just out of the verdict.
- Each positive test has a decoy that differs only in the exemption's
  trigger: `.claude/notes.md` and `.claude/handoff-notes.txt`,
  `inbox/notes.txt`, `inbox/my notes.txt`. The whitespace-bearing path is
  exercised on purpose.
- `verify-step.sh` keeps the 0/1/2 contract on every path. Each exit 2 is a
  named `ERROR:` line, and the comments give the reason for the pipe rather
  than a here-string, which is the one choice a later edit would be tempted
  to "simplify".
- `reports_count` counts one byte per file instead of lines, so a newline in
  a filename no longer inflates it. The `[[:space:]]` swap makes the
  classification regex defined under BSD as well.

## Recommendations

- Apply the REFACTOR-NEEDED helper extraction when a later job touches the
  test helpers.
