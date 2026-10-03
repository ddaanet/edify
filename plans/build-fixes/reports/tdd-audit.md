# TDD Process Review: build-fixes

**Date:** 2026-10-03T22:03:56+02:00
**Runbook:** plans/build-fixes/outline.md. The job has no `runbook.md`; its
items and slice lists live in the outline.
**Commits analyzed:** b0e71862^..cb91e977 (27 commits). That is 22
slice-marker commits and five others: `755d5269` and `2aa3e000` (Item 2.1/2.2
prose), `75d3ccee` and `ed3a3364` (leg reports), and `2f84d013`, which is also
a marker commit and is counted among the 22.

**Inputs used:** the 44 slice reports
`plans/build-fixes/reports/item-1-{1,2,3,4}-s<k>-{red,test-review,green,code-review}.md`.
Git was used to resolve each report to the commit that added it, to diff that
commit, and to read `outline.md`'s history. The leg reports, the
`review-*.md` gate reports and the `item-2-*.md` reports fall outside this
dispatch's inputs, so they were not read. The reports directory holds no
`phase-*-corrector.md` and no `final-review.md`.

## Executive Summary

All 11 slices across Items 1.1–1.4 show the four-dispatch shape. Each has a
genuine assertion red (7 slices) or a per-test mutation proof that the test
review reproduced with a different mutation (4 slices, plus one passing guard
test in 1.4/2). Each has exactly one GREEN commit carrying its tests, its
implementation and its own three reports, and a separate code-review commit
carrying its code-review report. Every test id the test reviews list is
present, under the same name and in the same file, in its slice commit and at
the end of the range. No GREEN edited a test.

There are no critical violations. The findings fall into three groups:

- Two GREENs (1.2/1, 1.4/1) implemented argument-validation branches that no
  slice test reached.
- The outline revision that added Item 1.4 was committed after that item's
  first GREEN, and inside a code-review commit. Two later list revisions
  (1.4/2, 1.4/3) never reached the outline.
- Code reviews repeatedly landed production behaviour with no pinning test.

Test review was highly effective. It caught a wrong-reason or
under-discriminating test in 9 of 11 slices.

## Per-Slice Compliance

| Item/slice | RED evidence | Test review | One slice commit | Tests unmodified | Issues |
|------------|--------------|-------------|------------------|------------------|--------|
| 1.1/1 | Mutation proof: 1 test, 1 mutant (`[ M?]` on a copy), red on `returncode == 0` | Different mutant (`[^RCU]`) plus a 4-state table, red on its assertion | `b0e71862` (code review `69d0d5ea`, report only) | Yes | Mutant on a copy with `SCRIPT` rebound, as the outline prescribes (known deviation 3) |
| 1.1/2 | Mutation proof: 1 test, 3 mutants, each red on its assertion | Different mutants (`[^ ]+`, `noexempt`); fixed a bare negative | `0aab33f3` (code review `ae24979f`) | Yes | Code review changed `verify-step.sh` (quotePath) with no test; pinned later in 1.4/4 |
| 1.2/1 | Genuine red vs inert stub (`assert [] == [...]`) | Still red after the fixture rebuild | `22998e19` (code review `df07e4b5`) | Yes at id level | GREEN added an untested usage check (minor scope); orchestrator edited a test docstring after review |
| 1.2/2 | Genuine red (exempt paths listed) | Still red after 3 near-misses added | `e489ccf2` (code review `4229525e`) | Yes | — |
| 1.2/3 | Genuine red (`assert 2 == 1`) | Still red, `(2,'ERROR: c') == (1,'NO-BASE:')` | `f7febe05` (code review `7dd2059d`) | Yes | — |
| 1.3/1 | Genuine red (`Files changed: 3` vs 1) | Still red (5 vs 3) | `c8b347aa` (code review `8e771850`) | Yes | Expected value changed from 1 to 3 at test review; outline still says 1 |
| 1.3/2 | Genuine red (`Behavioral code: yes`) | Still red | `95f67f7c` (code review `1e6625cb`) | Yes | — |
| 1.4/1 | Genuine red, on the usage exit (`assert 2 == 0`) | Still red; decoy fixed | `721af548` (code review `2f84d013`) | Yes | GREEN added an untested arity guard (minor scope); outline gained Item 1.4 only after this GREEN, in `2f84d013` |
| 1.4/2 | Main test: genuine red. Guard test: mutation proof (arity-guard mutant) | Main still red; guard: different mutant (`case` pattern) | `2a2bbafb` (code review `ed039ba5`) | Yes; slice-1 test relocated by test review (listed there) | Guard test added beyond the outline slice; not recorded in the outline |
| 1.4/3 | Mutation proof: 1 test, 3 in-place mutants, restore verified | Two different mutants (`**/`, dropped `$`) | `8365eb53` (code review `7ace9cc5`) | Yes | Slice "list-revised" to also pin `:(glob)`; not recorded in the outline. RED claimed ruff clean; D205 failed |
| 1.4/4 | Mutation proof: 1 test, 1 mutant on a copy | Different mutant (`quotePath=false`); fixed a locale-dependent red | `88ef264e` (code review `cb91e977`) | Yes; test moved files at test review (listed there) | — |

## Violations

No critical violations. In particular:

- No reviewed test was dropped, renamed or relocated by GREEN. Every test-review
  id resolves to `def <id>(` in the slice commit's named file, and all 16 slice
  tests are present at `cb91e977`.
- No GREEN edited a test. Only the 11 GREEN commits touch `tests/`
  (`git log b0e71862^..cb91e977 -- tests/`).
- No slice spans commits. No commit carries another slice's report.
- No marker-bearing commit is left unaccounted for.

Minor violations:

1. **1.2/1, scope: GREEN implemented contract its slice's test does not
   reach.** `22998e19` `changed-files.sh` adds
   `if [[ $# -ne 1 ]]; then echo "ERROR: usage: …"; exit 2; fi`. The GREEN
   report lists it ("Usage check: exactly one argument … exit 2"). No slice of
   Item 1.2 exercises it. The 1.2/3 test review's Recommendations say so:
   "Usage errors … are pinned by no slice of Item 1.2". No later slice was
   stranded by it: 1.2/3 still redded, through the parent-lookup branch.
2. **1.4/1, scope: same shape.** `721af548` rejects any second argument other
   than an exact `--phase` (`changed-files.sh:40` at range end). The slice test
   only shows that `--phase` is accepted. The 1.4/1 code review's mutated-SUT
   run removed the `$2 != --phase` clause and got 4/4 green, so the mutant
   survived. 1.4/2's RED later pinned the guard with a mutation proof.
3. **Item 1.4, list revision recorded late and bundled.** `outline.md` gained
   Item 1.4 and its slice list in `2f84d013` ("Item 1.4/1 — code-review fixes;
   outline gains Item 1.4 and --phase base", 19:45:44). That is after
   `721af548`, the 1.4/1 GREEN at 19:42:02. So the item's first slice ran
   before its text was committed, and the revision shares a commit with a code
   review (348-line outline diff alongside `changed-files.sh`).
4. **1.4/2 and 1.4/3, list divergence not in `outline.md`.**
   - 1.4/2 added `test_phase_flag_only_as_exact_second_argument`, which comes
     from the 1.4/1 code review's deferred Minor 2.
   - 1.4/3's RED is titled "(list-revised)", and it pins the 1.4/2
     code-review `:(glob)` fix as well as the filters. Its code review cites
     "Item 1.4/3 list revision: pin the slice-2 `:(glob)` fix".

   The outline's Item 1.4 slices 2–3 (outline.md:265-268) still describe
   neither. `outline.md` has no commit after `2f84d013` within the range.
   Whether the leg reports record these revisions was not checked, since they
   are outside the inputs.

## List Revisions

From `git log -- plans/build-fixes/outline.md`: `b5b1b30c` (draft),
`d415f22d` (proofed, before the run), `2f84d013` (mid-run, adds Item 1.4) and
`7ab55c09` (Item 2.15, after the range).

- **Item 1.4 added (all four slices):** recorded in `2f84d013`. It names "added
  at Item 2.3 by my human partner's ruling", and slice 4 explicitly carries the
  1.1/2 code-review recommendation. Late and bundled (Violation 3).
- **1.4/2:** gained a guard test. Not recorded (Violation 4).
- **1.4/3:** gained the `:(glob)` pin, and became a mutation red because the
  filters are shared code from Item 1.2. Not recorded (Violation 4). The
  outline marks only slice 4 as a mutation red (outline.md:270-271).
- **1.3/1:** the expected value went from `Files changed: 1` to `3` after the
  test review rebuilt the fixture. The test review records that the dispatch
  allowed it. The outline (outline.md:249-251) still states `1`.
- **1.1/2:** the test review added exempt siblings to the slice's fixture.
  That is a fixture change within the slice's assertion, not a list change.

## Code Quality Observations

- **Code reviews landed untested behaviour, slice after slice.** Each review
  below flags its own change as unpinned. The orchestrator absorbed three of
  them later: quotePath via 1.4/4, the lone-`--phase` rejection via 1.4/2's
  guard test, and the phase `:(glob)` via 1.4/3. The rest are unpinned as of
  `cb91e977`, as far as these slice reports show. The §5 `review-code` gate's
  later tests are outside this audit.
  - `ae24979f`: `git -c core.quotePath=true` (`verify-step.sh:40`). Item 1.1's
    target is the test file only.
  - `df07e4b5`: job-name rejection (`changed-files.sh:51`), `cd` to the
    toplevel, `--` after `HEAD`, `--no-show-signature`.
  - `7dd2059d`: `--no-renames` (`changed-files.sh:83,115`) and
    `printf … || exit 2` (`:111`).
  - `1e6625cb`: the capture-then-grep, plus `--no-color --no-ext-diff`
    (`triage-feedback.sh:46-48`).
  - `2f84d013`: lone `--phase` rejected.
  - `ed039ba5`: phase `:(glob)` (`changed-files.sh:101`).
  - `7ace9cc5`: item `:(glob)` (`:83`).
  - `cb91e977`: `printf '%s\n' "$status"` (`verify-step.sh:60`).
- **Test-file restructuring rode slice commits.**
  - The 1.1/2 RED added `_status`, and its test review changed the
    `_stub_just`/`_init_repo` signatures and added `_assert_dirty` across 6-7
    pre-existing call sites (`0aab33f3`, 159 lines of churn in
    `tests/test_verify_step.py`).
  - The 1.4/2 test review split `tests/test_changed_files.py` into
    `changed_files_helpers.py` and `test_changed_files_phase.py`. That moved
    the already committed 1.4/1 test.
  - The 1.4/4 RED split `tests/test_verify_step.py` into three files
    (`88ef264e`, 370 lines changed).

  The reviews report byte-identical or AST-identical bodies, and the id-level
  check above agrees no test was lost. Even so, these slice commits mix
  line-cap refactoring of reviewed tests with the slice's own test.
- **A reviewed test was edited after its review.** During the 1.2/1 GREEN,
  docformatter rewrapped the `_commit` docstring and caused D205. GREEN
  correctly stopped with `blocked:`. The orchestrator then edited
  `tests/test_changed_files.py:76` itself (item-1-2-s1-green.md, "D205
  interruption"). The edit is docstring-only, but nothing re-reviewed it.
- **RED reports were amended by test review before commit.** 1.4/1 and 1.4/4
  have appended "Test review revision" / "Moved at test review" notes. Both are
  clearly labelled and keep the original figures. Because the report rides the
  GREEN commit, git has no record of the unamended RED.
- **RED self-report accuracy.** The 1.4/3 RED claimed `ruff check` clean, but
  `ruff check -q tests/` failed D205 (item-1-4-s3-test-review.md, Major 1).
- **1.4/1's red sits on argument parsing.** The red is the usage exit, not the
  base value. Its test review measured that "accept and ignore `--phase`"
  passes the slice, and accepted this as briefed: slice 2 pins the boundary.
- **Test quality is strong where reviewed.** Exact-list assertions are used
  throughout. Decoys are each shown load-bearing by variant matrices (1.2/1:
  11 candidates; 1.4/2: 13 variants). Positive/negative pairs share one
  fixture (1.3/2 `_def_edits_pending`), and errexit ordering is handled (1.2/3
  tuple assertion; 1.3/2 negative first).
- **Locale dependence caught.** The 1.4/4 test review found the mutant red was
  a `UnicodeDecodeError` under `LC_ALL=C`. It pinned `LC_ALL=C.UTF-8`
  (`tests/test_verify_step.py::test_quotepath_false_does_not_hide_dirt`).

## Recommendations

### Critical

None.

### Important

1. **Route code-review behaviour changes to a pinning slice.**
   - Issue: eight code-review commits added production behaviour with no test.
     Only three were later pinned within Item 1.4.
   - Impact: a reversion of any unpinned fix passes the suite, and the reviews'
     own mutated-SUT runs show it for `git log` failure → exit 2 (1.2/3) and
     the arity guard (1.4/1).
   - Action: when a code review reports an unpinned fix, the orchestrator adds
     a slice and records it in the outline, as was done for 1.4/4.
   - Where: `plugin/skills/build/references/tdd-slice.md`, §After the slice.
2. **Commit list revisions before the slices they govern, on their own.**
   - Issue: Item 1.4 entered `outline.md` after its first GREEN, inside a
     code-review commit. The 1.4/2 and 1.4/3 revisions never entered it.
   - Action: commit the outline revision as an orchestrator commit before the
     first dispatch of the revised slice.
   - Where: the list-revision step in the build references.

### Minor

1. **Hold GREEN to the slice's tests.** The 1.2/1 usage check and the 1.4/1
   arity guard were unreached contract. Prefer leaving such branches for a
   slice that reds them.
2. **Keep test-file splits out of slice commits where practical.** A line-cap
   split driven by RED or test review could land as its own commit before the
   slice's RED, so the GREEN diff shows only the slice.
3. **Re-review orchestrator edits to reviewed tests.** Even docstring-only
   edits like the 1.2/1 D205 fix should go through review, or the resumed
   GREEN dispatch should report them as deviations.
4. **Bring the outline's slice text in line with the executed tests.**
   - 1.3/1: expected count 3.
   - 1.4/2: the guard test.
   - 1.4/3: the `:(glob)` pin and the mutation red.

## Process Metrics

- Slices executed: 11.
- Fully compliant: 9. 1.2/1 and 1.4/1 carry minor scope violations. The
  item-level list-revision gaps (Violations 3–4) attach to Item 1.4, not to
  per-slice discipline.
- Wrong-reason tests caught at test review: 9 of 11 slices (1.1/2, 1.2/1,
  1.2/2, 1.2/3, 1.3/1, 1.3/2, 1.4/1, 1.4/2, 1.4/4). 1.1/1 had minor fixes
  only, and 1.4/3's Major was a lint failure.
- Mutation-proof slices: 1.1/1, 1.1/2, 1.4/3 and 1.4/4, plus the guard test
  in 1.4/2. Every proven test has a RED mutation and a different test-review
  mutation.
- Dispatches per item (RED, test review, GREEN, code review): Item 1.1: 8;
  Item 1.2: 12, plus 1 resume of the 1.2/1 GREEN after `blocked:`; Item 1.3: 8;
  Item 1.4: 16.
- Refactor commits: 0. No code review flagged `REFACTOR-NEEDED`, and no
  `item-*-refactor.md` exists.
- Suite state: every GREEN report records a green suite and
  `✓ Precommit OK`. Two code-review reports record no full-suite run for
  their commit:
  - `ae24979f` (1.1/2): module 8/8 and shellcheck; "`just precommit` was not
    run".
  - `8e771850` (1.3/1): module 2/2 and shellcheck.

  No report or commit message indicates a red suite.
