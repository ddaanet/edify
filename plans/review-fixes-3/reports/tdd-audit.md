# TDD Process Review: review-fixes-3

**Date:** 2026-10-08
**Runbook:** none. The hosting file is `plans/review-fixes-3/outline.md`, Group 2
(tdd Items 2.1, 2.2, 2.3, 2.4).
**Commits analyzed:** `a48cc81c..6ffd0b3d`, i.e. from 2.1/1's GREEN commit
through 2.4/1's list revision, inclusive. That range also holds the build-leg
report commits `d33f4a59` and `94fac1f5`, which are not slice commits. The
review gate `b4e1cf11` comes later and is not audited as a slice.

## Executive Summary

All seven slices follow the four-dispatch discipline. Each slice report
resolves to exactly one adding commit, and each GREEN commit carries exactly
its own slice's tests, implementation (if any) and RED, test-review and GREEN
reports. Every test id the test reviews name is present in its slice commit,
under the same name and in the same file. Each test file's line count at the
GREEN commit matches the count its test review recorded, line for line, and no
GREEN report records editing a test. No critical or major violation was found.

Four minor findings remain:

- 2.2/1's GREEN changed a line that its slice test does not reach. The plan
  sanctioned the change.
- Two refactor commits have reports with no suite-pass result.
- Two slice commits touched test modules outside their item's `Files` list.
- One list revision's wording was departed from at test review, and the
  outline does not record the departure.

The recommendations are about reporting, not about the work.

## Per-Slice Compliance

| Item/slice | RED evidence | Test review | One slice commit | Tests unmodified | Issues |
|------------|--------------|-------------|------------------|------------------|--------|
| 2.1/1 | Genuine red. `test_late_diff_failure_prints_error_alone` FAILED on its stdout assertion (`item-2-1-s1-red.md`) | Still red after its fixes (docformatter summary, `shlex.quote`). Final run: 1 failed, 15 passed | `a48cc81c` (GREEN); `486810b5` (code review); `f46660c0` (list revision, outline only) | Yes. Id present; 201 and 94 lines match the review; GREEN says "No test file edited" | None |
| 2.2/1 | Genuine red. `test_subdirectory_run_measures_the_repository_root` FAILED on `- Reports: 1` | Still red after its fixes (symlinked relative invocation, `is_file` assertion) | `bc986e6e`; `9fa45f86` (code review); `efbe062c` (list revision) | Yes. Id present; 356 and 184 lines match | V1: GREEN added the bash-3.2 `(` case pattern, which the slice test does not reach. Plan-sanctioned |
| 2.2/2 | `test_outside_a_work_tree_is_one_error_line`: genuine red (`0 == 1`). `test_cdpath_does_not_move_the_script_dir`: mutation proof (`unset CDPATH` → `: inert`), restore verified | Still red. The CDPATH proof was reproduced with different mutations (line reorder, silenced `cd`). Decoy `CDPATH` fix | `923626ea`; `c0848e9f` (code review); `4ff6c37d` (refactor); `ed8eabca` (list revision) | Yes. Both ids present; 399, 115 and 192 lines match | V2: refactor report has no suite result. V3: the outside-work-tree test lives in a module in Item 2.3's `Files`. Untested `cd` guard is the Interfaces residual bound, not a finding |
| 2.3/1 | Mutation proof per case: `[no-args]`, `[stale-base]`, `test_changed_files_error_is_printed_then_exit_2`. Three mutants, each restored | Reproduced with different mutants (A, B, C, D and E). Mutant E exposed a gap, which was fixed | `5de9fd6b`; `a48a9f1e` (code review, report only) | Yes. Ids present; 184 and 194 lines match | V3: `tests/triage_feedback_helpers.py` is not in Item 2.3's `Files` |
| 2.3/2 | Mutation proof per test: `test_unreadable_classification_is_an_error`, `test_failing_label_sed_is_an_error` | Reproduced with different mutants (A, B, C). Sed shim fixed | `a03aaa11`; `ef695ca3` (code review); `e83f26b8` (refactor); `40ce062f` (list revision) | Yes. Ids present; 273 lines match | V2: refactor report has no default-shell suite result |
| 2.3/3 | Mutation proof per test: `test_failing_definition_grep_is_an_error_not_no`, `test_unwritable_log_is_an_error_not_a_usage_exit[directory]` | Reproduced with different mutants. The `[directory]` mkdir-versus-header gap was fixed | `327c5ea8`; `d1c3569e` (code review) | Yes. Ids present; 260 and 222 lines match | None |
| 2.4/1 | Genuine red: 6 of 9 cases FAILED on `assert not stray`. The 3 `finishing.md` cases passed as planned regression pins | Still 6 failed, 3 passed after its fixes. The passing cases were disposed of by the fixture guards (`%G?` all `G`, non-hash line present) | `02c17122`; `568dbb0e` (code review); `6ffd0b3d` (list revision) | Yes. Id present; 261 lines match | None. Note: `pipeline-contracts.md:1` was added at code review (see observations) |

Every report resolved to one adding commit, with
`git log --diff-filter=A --no-show-signature --format=%H -- <report>`:

- each GREEN commit adds that slice's `red`, `test-review` and `green`
  reports and no other slice's report;
- each code-review report has its own adding commit;
- the two refactor reports are added by `4ff6c37d` and `e83f26b8`, both after
  their slice's code-review commit.

Every `review-fixes-3 Item 2.x/k` commit is one of these: a GREEN commit, a
code-review commit, a refactor commit, or a list revision that touches
`outline.md` alone (`git show --stat` confirms all five list revisions are
outline-only). No marker commit is left unaccounted for.

## Violations

- **V1 (minor). 2.2/1, check 2/scope: GREEN made a change its slice test does
  not reach.** `bc986e6e` rewrites the `case` pattern in
  `plugin/bin/triage-feedback.sh`:

  ```
  -            review.md | review-*.md | final-review.md | tdd-audit.md) continue ;;
  +            (review.md | review-*.md | final-review.md | tdd-audit.md)
  +                continue ;;
  ```

  `test_subdirectory_run_measures_the_repository_root` passes either way
  under the default shell. The change matters only under bash 3.2.
  Mitigations:

  - The Item 2.2 Notes require it ("The script must still parse and pass
    under bash 3.2"), added by list revision `f46660c0` before the slice ran.
  - The defect was pre-existing (`item-2-2-s1-green.md`: "present at HEAD").
  - No later slice was left without a behaviour to red against.

  The change has no automated pin. Only a manual bash-3.2 run catches its
  removal; see the code-review comment in `9fa45f86`.

- **V2 (minor). 2.2/2 and 2.3/2, check 2: the refactor commits' suite state
  cannot be confirmed from their reports.**

  - `item-2-2-s2-refactor.md` (`4ff6c37d`) records collected counts only
    ("26 before, 26 after"), not a pass result.
  - `item-2-3-s2-refactor.md` (`e83f26b8`) records a bash-3.2 run only
    ("46 passed, 1 failed (the known …[absent])"). It has no default-shell
    or `just precommit` result.
  - `verify-step.sh` checks only that the tree is clean, so the build legs'
    "every committed step … `CLEAN`" says nothing about the suite.

  The gap is bounded by the next GREEN reports, which ran the tests uncached:
  `item-2-3-s1-green.md` (417/418 passed, 1 xfail) after `4ff6c37d`, and
  `item-2-3-s3-green.md` (421/422 passed, 1 xfail) after `e83f26b8`.

- **V3 (minor). Cross-slice scope: slice commits touched test files outside
  their item's `Files` list.** Neither case is a later item's work product
  landing early. Both are placement or helper choices, with the reason
  recorded in the RED report:

  - **`923626ea` (2.2/2)** adds `test_outside_a_work_tree_is_one_error_line`
    to `tests/test_triage_feedback_failures.py`. That module is listed under
    Item 2.3, not Item 2.2. Reason given (`item-2-2-s2-red.md` §Placement):
    the hub would have gone over 400 lines.
  - **`5de9fd6b` (2.3/1)** extends `_run_triage` in
    `tests/triage_feedback_helpers.py` with `extra_args` and a `None` job.
    Item 2.3's `Files` does not list that helper module. The change appears in
    `item-2-3-s1-red.md` and `item-2-3-s1-test-review.md`.

  No list revision brought either file into scope. `ed8eabca` records only
  the location module.

No critical violation was found. No test was dropped, renamed or moved
between its test review and its GREEN commit. No GREEN report records editing
a test. No commit took a report from another slice. No slice was split across
commits.

## List Revisions

All five revisions are orchestrator commits that touch only
`plans/review-fixes-3/outline.md`:

- **`f46660c0`, after 2.1/1.** Item 2.2 gains a bash-3.2 `bash -n` and suite
  requirement. Item 2.3's shims use `shlex.quote`. Item 4.1's D-90 bullet
  gains "`ERROR:` alone".
- **`efbe062c`, after 2.2/1.** Slice 2.2/2 gains
  `test_cdpath_does_not_move_the_script_dir` as a mutation red, pinning the
  `unset CDPATH` fix from 2.2/1's code review.
- **`ed8eabca`, after 2.2/2.** Slice 2.3/1's `$status` mutant must take in
  the `changed-files.sh` call line, because 2.2/2 added a second identical
  guard. The run-location tests now live in `test_triage_feedback_location.py`.
- **`40ce062f`, after 2.3/2.** Slice 2.3/3's `grep` shim uses `_write_shim`
  from the 2.3/2 refactor.
- **`6ffd0b3d`, after 2.4/1.** D-86's query in
  `docs/references/pipeline-contracts.md` was added as a seventh site. This
  records `568dbb0e`'s change to a file outside Item 2.4's `Files`, plus the
  new `SCANNED` entry.
- **No revision after 2.3/1 or 2.3/3.** This is recorded in
  `build-leg2.md` §Run summary notes ("2.3/1 and 2.3/3: none").

Divergences recorded only in reports, not in the outline:

- **2.2/2's test review replaced the revision's `CDPATH=.` with a decoy
  directory.** It showed that `.` passes a silenced-`cd` mutant
  (`item-2-2-s2-test-review.md` Major 1). The change is recorded in
  `build-leg2.md`. The outline still says `CDPATH=.`.
- **2.2/2's "Today stdout carries …" text no longer describes the script.**
  The RED and test-review reports record this, and `build-leg2.md` leaves the
  text as plan-as-written. That follows the convention 2.4/1's revision
  states explicitly ("KD-7's site list above is plan-as-written and stays").
  This is a process note, not a defect.

## Code Quality Observations

- **GREEN regressions were caught at code review, not by the suite.**
  - 2.1/1's GREEN (`a48cc81c`) moved a bare `case` pattern inside `$(…)`.
    That stops the script parsing under bash 3.2, and the Linux suite was
    green. `486810b5` fixed it, and also fixed a trailing-newline byte change
    on exit 0 (`item-2-1-s1-code-review.md`, Critical 1 and Minor 1).
  - 2.2/1's GREEN (`bc986e6e`) introduced the `CDPATH` capture corruption,
    fixed in `9fa45f86` (`item-2-2-s1-code-review.md`, Major 1).

  Both fixes were made one at a time, each with its own repro and
  verification.
- **Test reviews raised discrimination, not just coverage.** Each test review
  ran mutants of its own that differed from the RED report's. Six of those
  mutants exposed a test that passed for the wrong reason, and each was fixed
  before GREEN (see Process Metrics).
- **Code reviews edited tests after GREEN in the pinning slices.**
  - `ef695ca3` (2.3/2 code review) rewired the fixture of 2.3/1's
    `test_usage_error_exits_1` to use `_underclassified_repo`.
  - `d1c3569e` (2.3/3 code review) changed the `[directory]` stderr positive
    from `"Permission denied"` to the operand path, proven by a
    `2>/dev/null` mutant.

  No check bars a reviewer from editing tests; only GREEN is barred. Each
  edit carries its own mutation evidence in the report.
- **One test case went through no RED or test review.** At code review,
  `568dbb0e` added `pipeline-contracts.md:1` to the 2.4/1 test. Its red comes
  from a single mutation by the reviewer who added it
  (`item-2-4-s1-code-review.md` §Verification), and no second agent
  reproduced it.
- **2.4/1's GREEN report gives two different suite statuses.** It says "Full
  suite via precommit: 430/431 passed", and its recap says "tests cached".
  `build-leg2.md` records the same 430/431. `item-2-4-s1-code-review.md`
  then ran the suite uncached: 431/432 passed.
- **Residual bounds are stated in code.** The untested `cd "$repo_root"`
  guard (`plugin/bin/triage-feedback.sh`, Item 2.2 Interfaces) and the BSD
  and locale wording limits in the triage tests are all stated in comments or
  docstrings, not implied.
- **One refactor left part of its flagged scope undone.**
  `tests/line_limits_helpers.py`'s shim was left un-migrated by `e83f26b8`,
  which judged it outside the job's scope (`item-2-3-s2-refactor.md`).

## Recommendations

### Critical

None.

### Important

None.

### Minor

1. **Refactor reports must state a suite result.** Issue: V2. Impact: check 2
   cannot be confirmed for `4ff6c37d` or `e83f26b8` from their own reports.
   `plugin/agents/refactor.md` already requires a precommit-validated commit
   (its Goal line), but it does not require the report to record the result.
   Action: require the report to carry the `just precommit` recap line, as a
   GREEN report does. Location: `plugin/agents/refactor.md`, the report step
   (Step 6).
2. **Record placement deviations in the list revision.** Issue: V3 and the
   `CDPATH` decoy departure. Impact: the outline's `Files` lists and slice
   text drift from what landed, and the only trace is in reports. Action:
   when a slice lands a test in another item's module, or a test review
   departs from the revised slice text, the orchestrator's next list-revision
   commit should name it. Location: `plugin/skills/build/references/tdd-slice.md`,
   the list-revision step.
3. **Pin plan-mandated portability fixes.** Issue: V1. The bash-3.2 `(`
   patterns in `plugin/bin/triage-feedback.sh` and
   `plugin/skills/build/scripts/changed-files.sh` have no automated pin.
   Action: route to my human partner alongside the existing out-of-scope
   bash-3.2 suite question. It is already ruled out of this job and is noted
   here only as the reason V1 cannot be closed by a test.
4. **Have someone reproduce a review-added case's red.** Issue: the
   `pipeline-contracts.md:1` case was proven only by its author. Action: when
   a code review adds a test case, a later review should reproduce its red
   with a different mutation; the review gate is one place for it. Location:
   `plugin/skills/build/references/tdd-slice.md`, the code-review step.

## Process Metrics

- **Slices executed:** 7.
- **Fully compliant:** 3 (2.1/1, 2.3/3, 2.4/1). The other 4 have minor
  findings only: 2.2/1 (V1), 2.2/2 (V2, V3), 2.3/1 (V3), 2.3/2 (V2).
- **Wrong-reason tests caught at test review:** 6.
  - `item-2-2-s1-test-review.md` Major 1: a cd-first GREEN passed the
    `relpath` invocation.
  - `item-2-2-s2-test-review.md` Major 1: `CDPATH=.` missed a silenced
    `cd`.
  - `item-2-3-s1-test-review.md` Major 1: a print-without-exit guard
    (mutant E) passed.
  - `item-2-3-s2-test-review.md` Major 1: an emptiness guard passed the sed
    test.
  - `item-2-3-s3-test-review.md` Major 1: the `[directory]` case accepted
    the header guard's line.
  - `item-2-4-s1-test-review.md` Major 1: once GREEN landed, the fixture's
    signing state was unguarded, so the cases could pass vacuously.
- **Mutation proofs:**
  - 9 named tests or cases needed one (2.2/2: 1; 2.3/1: 3; 2.3/2: 2;
    2.3/3: 2; plus `pipeline-contracts.md:1` at code review).
  - All 9 have one mutant per test or case, with restore verified.
  - The 8 proved at RED were each reproduced at test review with a different
    mutation. `pipeline-contracts.md:1` was not (see Minor 4).
- **Dispatches per item:**
  - 2.1: 4.
  - 2.2: 9 (8 slice dispatches and 1 refactor).
  - 2.3: 13 (12 slice dispatches and 1 refactor).
  - 2.4: 4.
