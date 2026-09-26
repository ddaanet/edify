# TDD Process Review: build-defects

**Date:** 2026-09-26T16:02:18Z
**Runbook:** plans/build-defects/outline.md (no `runbook.md` for this job — a
Simple job; item text lives under outline.md's `## Items`)
**Commits analyzed:** f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474..8811af354c327e579590c1a0ca6f65f852e15667
(Items 1.1 and 1.2 only)

## Executive Summary

Both tdd items — 1.1/1, 1.2/1, 1.2/2 — show genuine reds, disciplined
one-slice-per-commit packaging, and no dropped or renamed reviewed tests: at
test-id granularity, every test the test-review report names is present,
unchanged in name and file, in its slice's GREEN commit. The one structural
gap is in slice 1.2/2's RED: its mutation proof uses a single batched mutant
(a revert to the pre-fix commit) to red all four named tests at once, instead
of one mutation per test; the test review's own per-test mutants
(`m-rc.sh`, `m-quote.sh`, `m-gitstatus.sh`, `m-just.sh`) correctly close that
gap. A recurring tooling failure — the auto-mode `Edit` classifier refusing
edits to `plugin/` shell scripts — pushed every code-review fix in this run
(1.1/1's three minors, 1.2/1's F-1/F-2, 1.2/2's F-3) out of the review
dispatch and into a separate, human-applied commit; each is documented in the
orchestrator's leg report and pre-verified on a copy before landing, so none
is a silent fix, but it means every reviewed slice in this run carries three
`Item N.M/k`-marked commits rather than two. List revision (slice 1.2/2 added
mid-run) is recorded in both `outline.md`'s git history and `build-leg2.md`.

## Per-Slice Compliance

| Item/slice | RED evidence | Test review | One slice commit | Tests unmodified | Issues |
|---|---|---|---|---|---|
| 1.1/1 | Genuine: 1 failed/0 passed on named assertion (`- Reports: 0`), no mutation needed (behaviour absent, ordering suffices) | Confirms still-red post-fix; 2 major wrong-reason gaps fixed | `2152b28b` (GREEN); `a2b4ac2c` (code-review, report only) | `test_simple_with_review_reports_matches` present, same name/file, in `2152b28b` | Third marker-bearing commit `7cc0e5c2` applies the code-review's 3 minor fixes (classifier-refused, human-applied); documented in `build-leg1.md`, not a violation but a deviation from the two-commit shape |
| 1.2/1 | Genuine: 1 failed/0 passed on named assertion (`returncode == 0`), no mutation needed | Confirms still-red post-fix (same assertion, new fixture states); 4 major + 2 minor wrong-reason gaps fixed | `31fe4a16` (GREEN); `c2cec494` (code-review, report only) | `test_conventional_dirt_is_clean_and_other_dirt_is_not` present, same name/file, in `31fe4a16` | Third marker-bearing commit `4a24c0fe` applies F-1/F-2 (classifier-refused, human-applied) — flagged by the task as known context; UNFIXABLE U-DESIGN (staged exempt dirt) still open |
| 1.2/2 | Mutation-red variant: RED uses **one batched mutant** (`pre-f1.sh`) to red all 4 named tests at once, not one mutation per test | Reproduces with 4 separate per-test mutants (`m-rc.sh`, `m-quote.sh`, `m-gitstatus.sh`, `m-just.sh`), each isolated to its own test; 1 major (missing negative case) + 2 minor fixed | `2c35c093` (GREEN, no SUT edit — behaviour pre-existing per RED); `8811af35` (code-review, report only) | All 4 tests (`test_rename_out_of_exempt_path_is_dirty`, `test_quoted_exempt_path_is_clean`, `test_git_status_failure_exits_2`, `test_missing_just_exits_2`) present, same name/file, in `2c35c093` | RED's mutation proof does not meet "one mutation per test" (see Violations); third marker-bearing commit `e8179177` applies F-3 (classifier-refused, human-applied), documented in `build-leg2.md` |

## Violations

- **1.2/2 RED, mutation-proof granularity.** `plans/build-defects/reports/item-1-2-s2-red.md` §Mutation proof reds all four named tests
  (`test_rename_out_of_exempt_path_is_dirty`, `test_quoted_exempt_path_is_clean`,
  `test_git_status_failure_exits_2`, `test_missing_just_exits_2`) against a
  single mutant, `tmp/mutants/pre-f1.sh` (`git show 31fe4a16:…verify-step.sh`,
  a revert of all of F-1 and F-2 at once), rather than naming one mutation per
  test as the mutation-proof substitute requires. Each test does fail on its
  own assertion in that run, so nothing was left silently unproven, but the
  proof does not establish per-test isolation on its own — that isolation is
  supplied only by the test review's `m-rc.sh`/`m-quote.sh`/`m-gitstatus.sh`/
  `m-just.sh` (`plans/build-defects/reports/item-1-2-s2-test-review.md`
  §Mechanical check: mutation reds), each a single-change mutant that reds
  exactly its one named test while the other three stay green. Net effect:
  the slice's full RED+test-review record does prove each test independently,
  but only because test review did work the RED report should have done
  first.

- **Recurring third commit per reviewed slice (all three slices).** Every
  reviewed slice in this run carries three commits bearing its `Item N.M/k`
  marker instead of two, because the code-review dispatch's `Edit` tool was
  refused by the auto-mode classifier on every attempt against a `plugin/`
  shell script (`plugin/bin/triage-feedback.sh`,
  `plugin/skills/build/scripts/verify-step.sh`), each time forcing the fix
  text to be routed to "my human partner" and applied in a follow-up commit
  outside the dispatch: `7cc0e5c2` (1.1/1, 3 minors), `4a24c0fe` (1.2/1,
  F-1/F-2), `e8179177` (1.2/2, F-3). None of these three commits is
  unaccounted-for — each is narrated in `build-leg1.md` or `build-leg2.md`
  with the fix text traced back to the code-review report that specified it,
  and each fix was checked against a scratch copy (shellcheck, `bash -n`, a
  rebind-mutant pytest run) before being applied to the tracked file — but
  none of the three has its own report of the canonical four types, so this
  is flagged rather than silently accepted. Not scored as a critical
  violation because the task names the 1.2/1 instance as known context and
  the pattern recurred identically and transparently in the other two slices.

No other check failed: no red-suite commit, no multi-slice commit, no
scope leak into a later item's targets, no GREEN edit of a test file, no
dropped/renamed reviewed test, and no batched regression fix.

## List Revisions

- `plans/build-defects/outline.md` git history shows commit `9ccbcecc`
  ("build-defects outline: KD-7 commits by pathspec, Item 2.5 widened, slice
  1.2/2 added") as the orchestrator's revision adding slice 1.2/2.
  `plans/build-defects/reports/build-leg2.md` records the matching run-side
  note: "List revision: slice 1.2/2 was added before its RED; nothing else
  changed." Item 1.1's and 1.2/1's leg reports record "List revision: none."
  Divergence is recorded in both directions (outline diff and run summary);
  no unrecorded divergence found for these two items.

## Code Quality Observations

- `tests/test_triage_feedback.py` and `tests/test_verify_step.py` both locate
  assertions by heading/exact-line rather than substring or fixed offset
  (`item-1-1-s1-test-review.md` §Positive Observations;
  `item-1-2-s1-test-review.md` §Fixes Applied item 4's exact-block equality),
  consistent with the house `vacuous-green.md` guidance cited in both RED
  reports.
- `verify-step.sh` accreted three rounds of code-review fixes across the two
  slices (F-1/F-2 at `4a24c0fe`, F-3 at `e8179177`); each round's diff is
  reproduced verbatim in this report's Violations note and each was checked
  on a copy before landing — no fix was applied blind.
- The slice 1.2/1 code review's UNFIXABLE U-DESIGN finding (staged KD-7-exempt
  dirt can still enter a commit via a pathspec-less `git commit`,
  `item-1-2-s1-code-review.md` §UNFIXABLE) is still open as of the commits
  audited here; it is a design decision routed to "my human partner", not a
  defect in slice execution, but downstream items reading KD-7's safety
  argument (Item 2.1 §2, Item 2.6) should not be taken as resolving it.
- `tests/test_verify_step.py` is 274 lines at `2c35c093`, comfortably under
  the 400-line cap.

## Recommendations

### Important

1. **Give the mutation-proof substitute a per-test mutant before RED, not
   only at test review.** `item-1-2-s2-red.md`'s single batched
   `pre-f1.sh` mutant is cheaper to produce than four isolated mutants, but it
   defers the isolation work test review then has to redo. State in the RED
   procedure (or `genuine-red.md`) that a multi-test mutation-red slice needs
   one mutant per named test, mirroring the single-test case, so test review
   is checking isolation rather than establishing it for the first time.

### Minor

1. **Name the classifier-refusal fix-commit pattern explicitly in
   `finishing.md` or `dispatch-composition.md`.** It has now occurred three
   times in one job (`7cc0e5c2`, `4a24c0fe`, `e8179177`), always for the same
   reason (auto-mode `Edit` refusal on a `plugin/` shell script) and always
   handled the same way (route the exact fix text in the code-review report,
   apply it out-of-band, narrate it in the leg report). Since the shape is
   now recurring rather than exceptional, giving it a named procedure — e.g.
   "a classifier-refused fix is applied by the orchestrator directly from the
   routed text and recorded in the leg report, never silently" — would let a
   future audit check it mechanically instead of reconstructing intent from
   three separate leg-report paragraphs.
2. **Resolve the KD-7 staged-dirt UNFIXABLE before it is load-bearing
   elsewhere.** `item-1-2-s1-code-review.md`'s own recommendation ("Resolve
   UNFIXABLE 1 before Item 2.1 writes the §2 DIRTY bullet") — confirm this
   was settled before Item 2.1's commit, since this audit's scope does not
   cover Item 2.x.

## Process Metrics

- Slices executed: 3 (1.1/1, 1.2/1, 1.2/2); fully compliant: 2 (1.1/1, 1.2/1);
  1 with a flagged mutation-proof granularity gap (1.2/2), fully remediated by
  its own test review.
- Wrong-reason tests caught at test review: 2 major (1.1/1) + 4 major/2 minor
  (1.2/1) + 1 major/2 minor (1.2/2) = 7 major, 4 minor issue fixes, from the
  three test-review reports' own Issues Found sections.
- Dispatches per item: Item 1.1 — 4 (1 slice × RED/test-review/GREEN/
  code-review); Item 1.2 — 8 (2 slices × 4). Total 12, matching the 12 report
  files audited.
