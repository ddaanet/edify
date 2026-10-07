# TDD Process Review: review-fixes-2

**Date:** 2026-10-07
**Runbook:** none. The hosting file is `plans/review-fixes-2/outline.md`, an
outline routed to `/build`.
**Commits analyzed:** `bb058555..94c0f6c4`. Slice commits run from `2a0a3ffa`
(Item 1.1/1 GREEN) to `6789908e` (Item 1.4/2 code review). The two review-gate
TDD amendments are in `94c0f6c4`.

## Executive Summary

Discipline held on the outline's nine tdd slices (Items 1.1–1.4). Each slice
has all four reports. Each resolves to exactly one GREEN commit, which carries
the slice's tests, its implementation and its RED, test-review and GREEN
reports. An orchestrator commit follows, carrying the code-review report. No
reviewed test was dropped, renamed or relocated by GREEN, and no GREEN report
records a test edit. The mutation-proven slices (1.1/5 partly, 1.3/1, 1.4/1,
1.4/2) prove every named test and have it reproduced by a different mutation.

The recurring finding is scope inside Item 1.1 and Item 1.2. Five GREENs
(1.1/1, 1.1/2, 1.1/3, 1.1/5, 1.2/1) implemented failure arms of the item
interface that no slice test reaches:

- three were pinned later, at code review;
- three arms of `triage-feedback.sh` are still unpinned today;
- one (1.2/1's unreadable-log arm) was dead code that the code review rated
  Critical.

The two review-gate amendments ran without slice commits, by ruling, and both
record their deviations.

Recommendations:

- Give slice lists a slice per interface failure clause.
- Have GREEN report, rather than write, contract that its batch does not
  reach.

## Per-Slice Compliance

Commit columns give the GREEN commit, then the code-review commit. "RED
evidence" is genuine (assertion red), mutation (`Mutation proof`), or mixed.

| Item/slice | RED evidence | Test review | One slice commit | Tests unmodified | Issues |
|------------|--------------|-------------|------------------|------------------|--------|
| 1.1/1 | genuine: 5/5 red on assertion | still red 5/5 after fixes | `2a0a3ffa` + `d52b3fa7` | yes; all 5 ids present | V1: untested `changed-files.sh` exit-1/2 arm |
| 1.1/2 | genuine: 1/1 red on `- Reports: 0` | still red after fixture fix | `787349b0` + `7a385b10` | yes | V1: untested reports-diff failure arm |
| 1.1/3 | genuine: 1/1 red on `Behavioral code: no` | still red after 2 fixture fixes | `e4b3f5b4` + `6ebbc205` | yes | V1: untested grep ≥2 arm (still unpinned) |
| 1.1/4 | genuine: 1/1 red on verdict | still red after fixes | `32a9767b` + `52a1c42b` | yes | none |
| 1.1/5 | mixed: `[apostrophe-label]` genuine; `[head-file]` and `[no-label-line]` by mutation, one each | own mutation per passing case; still red | `1e4b91cf` + `46ff16a0` | yes; 3 parametrised ids present | V1: untested sed and classification-grep failure arms (still unpinned) |
| 1.2/1 | genuine: 1/1 red on `rows == [first_row]` | still red after 2 fixes | `ce22286e` + `72b7fdef` | yes | V1: untested unreadable-log arm, dead at GREEN |
| 1.3/1 | mutation: both named mutants red the one test | own mutant C reds it | `3124b3ee` + `354db053` | yes | none (no implementation change) |
| 1.4/1 | mutation: bare `source` reds `[absent]` and `[defines-nothing]`, each shown | own M1/M2/M3 per case | `31d2bb03` + `14154267` | yes | none (no implementation change) |
| 1.4/2 | mutation: same, per case | own M1–M4 per case | `a80ffde3` + `6789908e` | yes | none (no implementation change) |
| gate-fix (amendment) | A, B, C genuine; D by 4 mutations | D reproduced by own mutation; C strengthened | no slice commit, by ruling (`94c0f6c4`) | ids present; A later renamed by the narrow RED | D1: test file reformatted during GREEN |
| gate-fix-narrow (amendment) | genuine: A red on assertion; the orchestrator re-ran it | none, by plan (recorded) | no slice commit, by ruling (`94c0f6c4`) | yes | recorded deviation |

## Violations

### V1. GREEN implemented interface clauses its slice's tests do not reach (scope compliance)

Item 1.1's interface puts `ERROR:` and exit 2 on every git, grep or
`changed-files.sh` failure. Item 1.2's comparison inherits that interface. No
slice in either list tests a failure arm, so each GREEN that wrote one went
beyond its batch.

- **1.1/1, `2a0a3ffa`.** The GREEN report self-discloses: "Also implemented
  per the interface, untested in this slice: `changed-files.sh` exit 1/2 …
  `ERROR: changed-files.sh exited <n>`, exit 2". The code review
  (`item-1-1-s1-code-review.md`, Major 1) pinned it in `d52b3fa7`, adding
  `test_no_base_is_an_error_with_no_log_row`, proven by two mutations.
- **1.1/2, `787349b0`.** The GREEN added the reports-diff capture, "failure ->
  `ERROR: git diff failed` on stdout, exit 2". No test reached it. The code
  review (Major 3) pinned it in `7a385b10` with
  `test_failing_reports_diff_is_an_error_not_none`.
- **1.1/3, `e4b3f5b4`.** The GREEN wrote "grep exit 1 is 'no', any other
  non-zero exits 2 with `ERROR: grep failed`". The code review records "No
  test pins the ≥ 2 case" and only fault-injected it by hand. This is
  `plugin/bin/triage-feedback.sh:129`, still unpinned.
- **1.1/5, `1e4b91cf`.** The GREEN wrote grep "above 1 prints `ERROR: grep
  failed`" and "A failing `sed` prints `ERROR: sed failed`". The test review's
  Residual section says neither is reachable by the slice's cases. These are
  `triage-feedback.sh:152` and `:158`, still unpinned (`rg 'sed failed' tests/`
  finds nothing).
- **1.2/1, `ce22286e`.** The GREEN wrote "an unreadable log gives `ERROR:` on
  stdout and exit 2", untested. The code review (`item-1-2-s1-code-review.md`,
  Critical 1) found it dead: `if ! while …; done < "$log_file"` never applies
  `!` to a failed redirection, so the script appended blindly and exited 0.
  `72b7fdef` fixed it, adding `test_unreadable_log_is_an_error_and_appends_nothing`.

No later slice was stranded, because none of the slices covered these arms.
The root cause is shared with planning: the outline's slice lists omit the
interface's failure clauses.

### D1. gate-fix GREEN: the test file changed during the GREEN dispatch (recorded)

`gate-fix-green.md`:

- "`just lint` … rewrote … `tests/test_changed_files.py`";
- "First `just precommit` failed on ruff D205 in the test docstring
  (`tests/test_changed_files.py:133`); the docstring was fixed outside this
  dispatch".

`build-leg3.md` §Deviations records the orchestrator's form-only docstring fix.
Both edits are formatting, and no assertion changed. This still breaches the
rule that GREEN never touches a test, here through a recipe and an
orchestrator hand-edit.

### Recorded deviations (not counted as violations)

- **gate-fix and gate-fix-narrow: no slice commit.** By my human partner's
  ruling, every test, implementation and report rides `94c0f6c4`, alongside
  the review-gate corrector's own behavioural fixes. Per-slice git analysis is
  therefore limited to the reports for these two.
- **gate-fix-narrow: no test-review dispatch.** This was by plan. The
  orchestrator re-ran the red. `gate-fix-narrow-code-review.md` covers the
  test, with six per-near-miss mutations each shown red, including the two
  near-misses the RED report says could not red against the old script.

## List Revisions

- No slice list changed during execution. `build-leg2.md:54` records "List
  revision: none for every slice". The executed slices match the outline: 5
  for Item 1.1, 1 for 1.2, 1 for 1.3 and 2 for 1.4.
- Item 1.3/1's fixture was amended after the fact, at the review gate. The
  amendment added `back\slash.txt` and two further named mutants. It is
  recorded in the hosting file's diff within `94c0f6c4`
  (`plans/review-fixes-2/outline.md`, Item 1.3) and executed as gate-fix
  test D. The 1.3/1 test review raised the gap first (Minor 2, OUT-OF-SCOPE),
  and so did the code review.

## Code Quality Observations

- **Test reviews killed wrong implementations, not only checked reds.** In
  1.1/2, 1.1/3, 1.1/4, 1.1/5 and 1.2/1 the test review probed named mutants
  against scratch copies of the SUT and strengthened fixtures that let a
  plausible wrong GREEN pass. For example, `item-1-1-s2-test-review.md` M4–M6
  and `item-1-2-s1-test-review.md` (substring, job-agnostic and last-row
  skips).
- **Mutation proofs are restore-verified.** Each proof is verified by a grep
  for the mutant text and by `git diff --exit-code` or a sha256 of the diff.
  The gate-fix RED records before and after hashes.
- **Code reviews found real defects behind green suites.** Examples:
  - 1.1/2: a C-quoted name read and a here-string;
  - 1.1/3: SIGPIPE under `pipefail`, measured on GNU grep 3.11;
  - 1.1/5: a greedy `.*:` trim;
  - 1.2/1: a dead error path and an unterminated last row.

  Each fix has a test and an in-place mutation red.
- **A test was relocated at code review, not at GREEN.** `6ebbc205` moved four
  tests, `test_behavioral_code_reads_the_lists_paths_only` among them, to the
  new `tests/test_triage_feedback_behavioral.py` to stay under 400 lines. The
  report states an AST comparison showing them byte-identical. The outline
  said "The tests stay in `tests/test_triage_feedback.py`", with a helpers
  split. A second test module is a further split the outline did not name.
- **A code-review recommendation was not carried forward.**
  `item-1-1-s4-code-review.md` recommended that slice 5 add a backslash label
  case run under `BASHOPTS=xpg_echo`, to pin the `printf` form. Neither
  slice 5 report mentions it, and `rg xpg_echo tests/` finds nothing.
- **Some suite evidence rests on a sentinel cache hit.** `item-1-4-s1-green.md`
  gives only a `-k unloadable` run plus a `just precommit` reporting "Tests
  cached (inputs unchanged)", with no full-suite count. `item-1-4-s2-green.md`
  gives the module 5/5 plus the same cache hit. A cache hit implies a passing
  run on identical inputs, but the reports do not say who ran it.
- **A mutation run was blocked.** In `item-1-4-s1-code-review.md`, the
  auto-mode classifier denied the reviewer's fail-open mutation run, so that
  mutant has no result. The slice's red rests on the RED and test-review
  mutations, which are sufficient.

## Recommendations

### Critical

None.

### Important

1. **Slice the interface's failure clauses.**
   - Issue: Items 1.1 and 1.2 carry an `ERROR:`/exit 2 interface with no
     slices covering it.
   - Impact: five GREENs wrote untested arms. One was dead, and three remain
     unpinned.
   - Action: when an item's Interfaces block lists failure exits, give the
     slice list one slice per failure clause that a test can reach, for
     example with a `PATH` shim as `_run_triage(path_prepend=…)` now allows.
     Where it cannot be reached, state that in the item.
   - Where: `plugin/skills/runbook/references/runbook-format.md` (slice
     authoring), and the outline route's equivalent guidance.
2. **Pin the three open arms.**
   - Action: add shim-driven tests for `triage-feedback.sh:129` (behavioural
     grep ≥2), `:152` (sed failure) and `:158` (classification grep ≥2), each
     proven by a mutation that drops the arm.
   - Where: `tests/test_triage_feedback_behavioral.py` and
     `tests/test_triage_feedback.py`.

### Minor

1. **GREEN reports, rather than writes, out-of-batch contract.**
   - Issue: 1.1/1's GREEN disclosed its overreach, but the others did not
     flag theirs.
   - Action: GREEN's instructions should say that interface clauses its tests
     do not reach go in the report as "left for review", not into the code.
   - Where: the GREEN mode of `plugin/agents/test-driver.md`.
2. **Keep formatters off test files during GREEN.**
   - Issue: `just lint` reformats in place, so a GREEN that runs it edits
     tests.
   - Action: have the RED or test review leave tests lint-clean (the 1.1/1
     test review did this), and have GREEN run a check-only lint.
   - Where: `plugin/skills/build/references/tdd-slice.md`.
3. **Carry code-review recommendations into the next slice's dispatch.** The
   1.1/4 recommendation for slice 5 was lost.
   - Where: `plugin/skills/build/references/dispatch-composition.md`.
4. **Require a full-suite count in GREEN reports** whenever precommit
   reports a cache hit.
   - Where: `tdd-slice.md`, GREEN report contents.

## Process Metrics

- Slices executed: 9 outline slices plus 2 review-gate amendments.
- Fully compliant: 4 of 9 outline slices (1.1/4, 1.3/1, 1.4/1, 1.4/2). The
  other five carry V1.
- Amendments: both carry recorded deviations, and gate-fix also carries D1.
- Wrong-reason tests caught at test review: 0 tests redding for the wrong
  reason (every RED failed on an assertion, none ERROR).
- Tests strengthened at test review against a surviving wrong implementation:
  7 tests across 6 dispatches:
  - 1.1/1, the failing-diff `ERROR:` line;
  - 1.1/2, 1.1/3, 1.1/4, 1.1/5 and 1.2/1;
  - gate-fix test C.

  One more gap was deferred: 1.3/1, mutants A and B. It closed at the review
  gate as test D.
- Dispatches per item:
  - Item 1.1: 20 (5 slices × 4)
  - Item 1.2: 4
  - Item 1.3: 4
  - Item 1.4: 8
  - gate-fix: 4
  - gate-fix-narrow: 3, plus the orchestrator's red re-run
- Commits per slice: 2 (GREEN, then code review) for all nine. There are no
  refactor commits, and no `item-*-refactor.md` exists.
