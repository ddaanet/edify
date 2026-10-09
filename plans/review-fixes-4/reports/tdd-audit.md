# TDD Process Review: review-fixes-4

**Date:** 2026-10-09
**Hosting file:** plans/review-fixes-4/outline.md
**Commits analyzed:** 35d470b1..9ef44a97 (slice commits e0165b25 and 8e706975;
54d03996 and 9ef44a97 are Item 1.2 and the review gate, read only for scope
and cross-checks)

## Verdict: PASS WITH RECOMMENDATIONS

No violation of checks 1-4 or of the cross-slice checks. The one slice is a
genuine mutation-red slice: the mutation proof is named, red on assertion,
restore-verified, and the test review reproduced it with three different
mutations that also prove the second assertion. The recommendations concern
gaps in the pipeline's description of a mutation-red slice, not defects in
this run.

## Executive Summary

Item 1.1 has one slice, executed as four dispatches in two commits: e0165b25
(GREEN commit: test, comment edit, RED, test-review and GREEN reports) and
8e706975 (code-review report alone). Every report resolves to exactly one
adding commit, the suite was green at the GREEN commit (432/433 passed, 1
xfail, precommit OK), and the single test id the test review lists is present
in the committed file under the same name. The GREEN dispatch's change was a
comment-only edit, which is what the outline specified, and its report says so
plainly. Recommendations: describe the no-implementation GREEN in
`tdd-slice.md`, make a mutation-red test review re-run the RED's own
mutation after its fixture changes, and require a mutation per assertion
rather than per test.

## Per-Slice Compliance

| Item/slice | RED evidence | Test review | One slice commit | Tests unmodified | Issues |
|------------|--------------|-------------|------------------|------------------|--------|
| 1.1/1 | Mutation proof: bare `cd` replaces the guard, test reds on stdout assertion (line 144), restore proven by diff, grep and 9 passed | Reproduced with 3 different mutations (message text, `exit 2` to `exit 3`, unquoted `$repo_root`), each red on assertion; restore proven; 2 minor fixes applied | Yes: e0165b25 adds red, test-review, green reports; code review alone in 8e706975 | Yes: `test_root_cd_failure_is_one_error_line` present in `tests/test_triage_feedback_failures.py` with the review's fixes (`missing root`, `printf '%s\n'`); GREEN report records no test edit | None blocking; see Recommendations |

Resolution (all `git log --diff-filter=A --no-show-signature --format=%H`):
red, test-review and green reports each return e0165b25 (one hash each);
code-review report returns 8e706975. The gate's `review-code.md` is added by
9ef44a97.

## Check-by-check findings

### 1. Genuine red, reviewed

- **Mutation named against the test it reds:** RED report, `Mutation proof`
  heading: old text is the whole `if ! cd "$repo_root"; then ... fi` block,
  new text is bare `cd "$repo_root"`; reds
  `test_root_cd_failure_is_one_error_line`. One test, one mutation: the count
  matches.
- **Red on the test's own assertion:** `assert '' == 'ERROR: canno...issing-root\n'`
  at test line 144 (pre-review numbering; the committed file has the assertion
  at line 145 after the review added a docstring line). An assertion failure,
  not an ERROR. Bash's `cd:` diagnostic went to stderr, so stdout was empty,
  as the report states.
- **Restore proven:** `git diff --stat` empty, grep shows the guard at line 43,
  no bare `cd` line, 9 passed. Restored by inverting the Edit, per `tdd-slice.md`
  §Mutation proof.
- **Test review reproduced it with a different mutation, per test:** three
  mutations of the reviewer's own choosing, none the RED's bare `cd`. The
  `exit 2` to `exit 3` mutation reds the exit-code assertion alone (`assert 3 == 2`,
  stdout assertion passed), which the RED could not show: under the RED's
  mutation the test dies at the first assertion, so the second assertion's
  discrimination was first evidenced by the test review (the situation
  `genuine-red.md` describes: a red is evidence for the one assertion it
  landed on). Restore proven by diff, grep for residue and 9 passed.
- **Wrong-reason hunt:** the shim is what fires the guard (the earlier
  `rev-parse` guard prints a different line), the asserted line exists only in
  the `cd` guard, the stdout check is exact equality, and `missing root` is
  never created. The fixture runs as production does: `_run_triage` invokes the
  script by absolute path with CWD at the repo root, `GIT_CONFIG_*` insulated,
  the shim directory prepended to `PATH`; `_init_repo` builds the fixture
  before the shim is on `PATH`. Verified by reading `tests/triage_feedback_helpers.py:109-136`
  and `tests/changed_files_helpers.py:99-114`. I re-ran the module on the
  current tree: 9 passed.
- **Independent check of an unmeasured claim:** the test docstring (committed)
  says a bare `cd` under `set -e` "exits 1 with empty stdout". RED and test
  review both state they did not measure the exit code under the bare-`cd`
  mutation (the stdout assertion fires first); the figure traces to the
  round-4 probe cited in the outline. I ran a standalone `set -euo pipefail`
  script doing a `cd` to a nonexistent path containing a space: exit 1. The
  claim holds. (The gate's `review-code.md` line 43 cites "mutation 1" as
  evidence for exit 1, but that mutation's recorded failure is the stdout
  assertion only, so the exit code was not read from it.)

### 2. One green commit per slice

- GREEN commit e0165b25: 5 files, all slice-owned (test file, SUT comment,
  RED, test-review and GREEN reports). No report of another slice, no Item 1.2
  file, no `.claude/` or `inbox/` file (RED report's `.claude/*` entries were
  left alone and are absent from the commit).
- Marker-bearing commits are exactly two, both accounted for by reports:
  e0165b25 (`review-fixes-4 Item 1.1/1 — pin triage's repository-root cd failure`)
  and 8e706975 (`review-fixes-4 Item 1.1/1 — code-review fixes`, adds
  `item-1-1-s1-code-review.md` only, which is the "report alone where it
  changed nothing" shape of `tdd-slice.md` §After the slice). No list-revision
  commit, no refactor commit.
- Suite never left red: GREEN report records `Summary: 432/433 passed, 1 xfail`
  and `Precommit OK`; 8e706975 changes no code. The three `oversized-file`
  warnings in the GREEN output concern agent files outside this slice and did
  not fail precommit.

### 3. GREEN dropped no reviewed test

The test review lists one id, `test_root_cd_failure_is_one_error_line`; it is
at `tests/test_triage_feedback_failures.py:120` in e0165b25 with the review's
fixes in place (diff matches the review's "Fixes Applied"). The GREEN report
records no test-file edit. Test-at-a-time order: the GREEN report states "No
test went from red to green in this slice", which is accurate.

### 4. Refactoring separation

Code review reports no `REFACTOR-NEEDED` and no fixes; no refactor report
exists and none was owed.

### Cross-slice checks

- **Scope compliance:** the GREEN diff is a 7-line comment change (+4/-3) in
  `plugin/bin/triage-feedback.sh`, which is exactly the outline's stated GREEN.
  No code line changed. No Item 1.2 work product appears in e0165b25 or
  8e706975.
- **List revisions:** `git log -- plans/review-fixes-4/outline.md` returns one
  commit (35d470b1, the creation). One slice, unrevised; no divergence, so no
  revision owed.
- **Regression handling:** no regressions occurred.

## Violations

None.

## List Revisions

None recorded and none owed (single slice; outline history is creation only).

## GREEN as a comment-only edit: fit and honesty

**Fit.** The outline's GREEN text ("narrow the residual-bound comment") is
documentation of a residual bound, not behaviour the test demands, so for a
mutation-red slice the GREEN dispatch has no implementation to write. The edit
is legitimately coupled to the slice, though: the new comment's last line cites
the test by name, and the old comment's claim ("no input provokes either") was
made false by the test. So the commit shape (test + comment + three reports,
one commit) is defensible. The pipeline text does not describe this case
(see Recommendation 1); the auditor does anticipate a slice with no GREEN
report (`plugin/agents/tdd-auditor.md:94`), but `tdd-slice.md` (c) describes only
a GREEN that makes tests pass.

**Honesty.** The GREEN report is accurate and does not dress the edit up: it
says "GREEN grows no implementation", "No code line changed", and that the
test "passed before and after the comment edit". One imprecision: it measured
comment widths for "lines 40-42" (80, 76, 78) but the comment is now four
lines, 40-43; the fourth (75 columns) was not measured by GREEN. The code
review measured all four. No effect on the result.

## Code Quality Observations

- Assertions discriminate on both contracts: stdout by exact equality
  (red under the message-text, bare-`cd` and unquoted mutations), exit code
  separately (red under `exit 3`; the gate also reds `exit 1`).
- The space in `missing root` makes the guard's quoting observable; this was a
  test-review fix, not in the original RED test, and is proven by the unquoted
  mutation.
- The shim echoes the path through `printf '%s\n'` and `shlex.quote`; reuse of
  `_write_shim` is correct (passes all other git calls through).
- The comment now names the test (`triage-feedback.sh:43`). Nothing mechanical
  keeps that name current if the test is renamed; minor, unlikely to matter.
- Test module is 283 lines (cap 400); ruff and docformatter clean per RED and
  test-review reports.
- Observed state, not filtered: the current tree has `M plans/reports/triage-feedback-log.md`
  (one added row, `review-fixes-4 ... yes | match`, the gate's triage log) and
  three untracked `inbox/*.md` files. Neither is part of the slice commits.

## Recommendations

These are for the pipeline and skill text. Each states its grounding; the
two marked ungrounded are not supported by data in these reports.

### Important

1. **Describe the no-implementation GREEN in `plugin/skills/build/references/tdd-slice.md`
   §(c).**
   Grounding: the GREEN report's "Order of tests made to pass" section reads
   "No test went from red to green"; the whole dispatch was a four-line
   comment edit plus a full `just precommit` run. `tdd-slice.md` (c) defines
   GREEN as making tests pass and committing "tests and implementation
   together", and (a) calls mutation proof "the fallback when the behaviour is
   already implemented", with no sentence on what GREEN does then. Action: state
   whichever the pipeline intends: (i) a mutation-red slice still dispatches
   GREEN, and the outline's non-behavioural GREEN text (comment, docs) rides the
   slice commit, with the report stating there is no red-to-green; or (ii) a
   slice with no GREEN text skips the GREEN dispatch and the RED dispatch's or
   test review's report is what the slice commit resolves from (the auditor
   already accepts this at `tdd-auditor.md:94`); in that case say who commits.
   Whether (ii) saves anything is ungrounded: these reports carry no cost data.

2. **Make the test review of a mutation-red slice re-run the RED's own
   mutation after its fixes.**
   Grounding: the test review changed the fixture after RED proved the bare-`cd`
   mutation (path renamed to `missing root`, shim `echo` to `printf`). The test
   review's three mutations are all different from RED's, as `tdd-slice.md` (b)
   requires, so the bare-`cd` mutation was not re-run against the final test
   until the code review's optional mutated-SUT run. Had the code review not
   chosen to run it, the committed test would never have been shown to red under
   the proof the RED recorded. Here that run happened and was red, so no harm
   resulted. Action: in `tdd-slice.md` (b), where the reviewer applies fixes to
   a test that carries a mutation proof, require re-running the RED's recorded
   mutation after the last fix, in addition to the different mutation. This is
   the "behaviour whose fixture changed between RED and GREEN" category of the
   untracked inbox brief `brief-slice-code-review-mutation-runs.md` (which I
   read; its sandbox-lies evidence I did not verify), solved one step earlier.

3. **Require a mutation per asserted contract, not per test, where a test
   makes more than one assertion.**
   Grounding: RED's single mutation reds only the first assertion (stdout), the
   exit-code assertion below it never ran red until the test review's
   `exit 3` mutation. `tdd-slice.md` says "one mutation per named test" and
   "red on its own assertion"; `genuine-red.md` says a red is evidence for the
   one assertion it landed on. The test review met the standard on its own
   initiative. Action: word `tdd-slice.md` §Mutation proof and (b)'s mechanical
   check to count assertions a test makes, so that the review's check does not
   depend on the reviewer thinking of it. Whether a second mutation in RED
   itself (rather than in the review) is better is ungrounded; the review
   placement worked here.

### Minor

4. **Do not cite a figure in a docstring that no dispatch measured.** The
   committed docstring says a bare `cd` "exits 1 with empty stdout";
   the RED and test review both disclaim measuring the exit code, and
   `review-code.md:43` cites mutation 1 for it though that run recorded only
   the stdout assertion. I measured exit 1 independently, so the claim is true;
   the process gap is that three dispatches passed it on without measuring it.
   Action: a line in the RED/test-review corrector criteria (`plugin/agents/corrector.md`
   test review section): "a number in a test docstring is either measured in
   this dispatch or attributed to its source". Ungrounded as a general rate:
   one instance.

5. **Reconcile `plugin/agents/corrector.md:418` with `tdd-slice.md`.**
   Grounding: `corrector.md` §Code review item 2 says "save the SUT, mutate
   ... restore" while `tdd-slice.md` (d) says never restore from a copy. The
   gate's `review-code.md:29` reports the SUT "restored byte-for-byte from a
   saved copy" and the tree was clean afterwards, so no harm occurred, but the
   two texts disagree and `genuine-red.md` (craft:test-discipline) sides with
   inverting the edit. The inbox brief raises the same conflict. Action: edit
   `corrector.md` to say restore by inverting the edit.

6. **GREEN width check should cover the whole comment block it writes.** The
   GREEN report measured lines 40-42, the comment now spans 40-43. Trivial;
   the code review caught it. Action: none beyond noting it; no pipeline change
   recommended.

## Process Metrics

- Slices executed: 1; fully compliant: 1 (Item 1.2 is a general item, not
  audited).
- Wrong-reason tests caught at test review: 0 outright. The review's two
  fixes were hardening (a path without a space could not detect an unquoted
  `$repo_root`; `echo` of a path under dash), not a test passing for a wrong
  reason.
- Dispatches for Item 1.1: 4 (RED, test review, GREEN, code review), 2
  commits. Models per the outline's ruling: RED and GREEN haiku, reviews
  sonnet (`tdd-slice.md` says opus for reviews; the outline's ruling governs
  this job and keeps the reviewer one rung above the implementer).
- Mutations observed against the final committed test: test review 3, code
  review 1 (bare `cd`, same as RED), gate 3 (bare `cd`, unquoted `printf`,
  `exit 1`); all red on assertion.
