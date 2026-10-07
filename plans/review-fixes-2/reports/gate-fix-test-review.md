# Review: gate-fix-test-review — test review of the gate-fix RED

**Scope**: the RED's four tests (A `tests/test_changed_files.py::test_pipeline_record_under_plans_reports_is_dropped`, B `tests/test_triage_feedback.py::test_reports_exclude_the_tdd_audit_report`, C `tests/test_triage_feedback_log.py::test_rerun_after_the_closing_commit_appends_no_row`, D `tests/test_changed_files.py::test_paths_with_space_and_non_ascii_bytes_are_listed_whole`, amended), the `tests/test_changed_files.py` module docstring, and `plans/review-fixes-2/reports/gate-fix-red.md`. Other uncommitted tests in those modules and both scripts are out of scope; I only mutated and restored the scripts.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The RED pins my human partner's ruling on review-code.md Major Issue 1. `changed-files.sh` must drop every path under `plans/reports/`, and triage's Reports count must exclude `tdd-audit.md`. D gains `back\slash.txt`.

- A, B and C each fail on an assertion against the unchanged scripts.
- D's mutation proof reproduces with a mutation of my own.
- Two fixes were applied:
  - C now pins the first run's evidence, so its first-versus-second comparison can no longer pass vacuously.
  - The module docstring now cites D-numbers instead of `build-fixes` outline KDs.

**Overall Assessment**: Ready

## Mechanical check

All tests were run in the foreground, before and after the fixes, against the unchanged scripts:

| Test | Result | Failing assertion |
|---|---|---|
| A | FAILED on assertion | `At index 4 diff: 'plans/reports/explore-x.md' != 'plans/reportsx.md'`; the list carries all three `plans/reports/` paths |
| B | FAILED on assertion | `'- Reports: 0' in [...]` with `- Reports: 1`, verdict `underclassified` |
| C | FAILED on assertion (after the fix, line 234) | `At index 1 diff: '- Files changed: 2' != '- Files changed: 1'`. The second run reads Reports 1 and verdict `match`. The new first-run pins pass. |
| D | PASSED (mutation-proven) | — |

Nothing PASSED among A, B and C, and nothing ERRORed.

## Mutation proof of D (my own mutation)

None of the RED's four mutations was reused: it covered the `core.quotepath=off` newline read, `read` without `-r`, the word-split, and dropping `-z`. My mutation removes the backslash on the output side instead of the read side.

- **Mutation:** in `plugin/skills/build/scripts/changed-files.sh` (line 125), I replaced `    printf '%s\n' "$path"` with `    printf '%s\n' "${path//\\/}"`, which strips every backslash. The old string occurs once, which I asserted.
- **D's result:** red on its assertion, `At index 1 diff: 'backslash.txt' != 'back\\slash.txt'`. `café.txt` and `my file.txt` were still listed whole.
- **Restore:** inverse exact replacement, with the count asserted as 1.
  - `grep -c 'path//'` gives 0 hits.
  - `git diff -- plugin/skills/build/scripts/changed-files.sh | sha256sum` gives `2e30796fa1a4942767faab9c39551463fbfd89e6bb393317ca9f091bc5d2d4c6`, equal to the expected hash.
  - D is green (1/1).
- `plugin/bin/triage-feedback.sh` was never mutated. Its diff hash is still `f8e5f9e896804df9ae430109ca90e89cf89303fd90ec6f639ab8d75fa7b5b141`.

## Wrong-reason hunting

**A — `plans/reports/` dropped.** Each wrong fix below reds A:

- dropping `plans/reports/triage-feedback-log.md` by name: `explore-x.md` and `sub/x.md` stay listed;
- a `plans/reports` prefix without the slash: `plans/reportsx.md` is dropped;
- an unanchored match: `docs/plans/reports/x.md` is dropped;
- dropping all of `plans/`, or every `plans/*/reports/`: `plans/other/reports/item-1-1.md` is dropped;
- a one-component `:(glob)plans/reports/*` exclusion: `sub/x.md` stays.

The expected list is in git's bytewise order, confirmed by the actual output. The test does not distinguish the case where the drop is placed in `exempt-paths.sh` instead of `changed-files.sh`; see Recommendations. The docstring is accurate. Its D-90 citation matches D-90's amended argument in `docs/references/build-run-state.md`, which drops `plans/reports/` as "the pipeline's record across jobs".

**B — `tdd-audit.md` excluded from the count.** The list already drops `plans/<job>/`. "Excluding `tdd-audit.md` from the list rather than the count" therefore changes nothing, and B still reds. The test fails today only because of the `tdd-audit.md` count, since `item-1-1.md` is already excluded. A count stuck at 0 would pass B, but `test_reports_exclude_the_per_item_report` pins a counted slice report in the same module, so the suite catches that. An over-broad exclusion such as `tdd-*.md` or `*-audit.md` would pass B. No report name in the pipeline is exposed to those patterns, so I added no decoy. The docstring is accurate and cites D-90, whose argument lists `tdd-audit.md` among the review reports.

**C — re-run after the closing commit.** C needs both fixes:

- with only the list fix, it reads Files 1, Reports 1 and verdict `match`, which differs from `overclassified`;
- with only the count fix, it reads Files 2, which differs from Files 1.

Triage dropping its own log path (option (c)) passes C, but A reds it. Before my fix, C compared two derived outputs and never pinned the first run (Major Issue 1 below). The closing-commit fixture commits the log as triage wrote it, plus `tdd-audit.md`. This matches `finishing.md` §3's closing commit, so the fixture can be produced by the real write path. The docstring is accurate and cites D-90.

**D — `back\slash.txt`.** All four mutants named in the docstring red, per the RED report, and so does my fifth. The docstring is accurate and is a raw string, so `\s` is literal. One limitation remains; see Recommendations.

**Line counts:**

- `tests/test_changed_files.py`: 381
- `tests/test_triage_feedback.py`: 366
- `tests/test_triage_feedback_log.py`: 244 after the fix

All are under 400 and no docstring was shaved. `ruff check` is clean and `ruff format --check` passes.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **C compared two derived outputs without pinning either**
   - Location: `tests/test_triage_feedback_log.py`, `test_rerun_after_the_closing_commit_appends_no_row`
   - Problem: C asserted only that the second run's `## Evidence` and `## Verdict` lines equal the first run's. The docstring claims the first run reads 1 file, 0 reports and `overclassified`, but nothing asserted that. A triage whose evidence did not depend on the range at all would pass the comparison, which is the "two derived states compared" shape. The row-count half had a non-emptiness guard (`len(first_lines) == 3`). The evidence half had none.
   - Fix: assert `- Files changed: 1`, `- Reports: 0` and verdict `overclassified` on the first run before the closing commit, with `_verdict` imported from `tests.triage_feedback_helpers`.
   - **Status**: FIXED

### Minor Issues

1. **Module docstring credited the new `plans/reports/` drop to `build-fixes` outline KDs**
   - Location: `tests/test_changed_files.py`, lines 3–9
   - Problem: the amended sentence put the shared `plans/reports/` drop under "KD-1 and KD-6 in `plans/build-fixes/outline.md`". Those decisions never covered it, so the attribution was wrong. The docstring also mixed outline-KD and D-number citations, and the `--phase` pointer cited `KD-2`. The dispatch asks for D-numbers, never outline KDs.
   - Fix: the first paragraph now cites D-88 for the base and D-90 for the list, including both drops. The `--phase` pointer cites D-89. This is the mapping Item 1.5 gives for the scripts.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_triage_feedback_log.py`, import block: added `_verdict`.
- `tests/test_triage_feedback_log.py`, `test_rerun_after_the_closing_commit_appends_no_row`: three assertions pinning the first run's Files changed, Reports and verdict.
- `tests/test_changed_files.py`, module docstring: D-88, D-90 and D-89 citations replace the `build-fixes` KD-1, KD-6 and KD-2 citations. The content is unchanged and the line count is unchanged.

After the fixes, A, B and C still fail on their assertions and D passes. See the Mechanical check table.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Ruling: `changed-files.sh` drops every path under `plans/reports/` | Satisfied (pinned by A) | Anchored-prefix, slash and sibling-job near-misses; sub-directory path |
| Ruling: `tdd-audit.md` joins the Reports count's review-report exclusions | Satisfied (pinned by B) | Reads 0 reports and `match` |
| m7 / KD-2 across the closing commit | Satisfied (pinned by C) | Same evidence and verdict, rows unchanged; first run now pinned |
| Item 1.3 amendment: `back\slash.txt` reds the `core.quotepath=off` newline read and `read` without `-r` | Satisfied (D) | RED report's mutations 1–2, plus my output-side strip mutation |

## Positive Observations

- A covers each plausible wrong boundary with its own near-miss: anchoring, the trailing slash, a sibling job and a nested path. Its docstring names which wrong implementation each near-miss catches.
- C is built so that each of the two fixes alone still reds it. C checks the evidence before the rows, so a failure shows its cause and does not end in a bare row-count mismatch.
- C's closing commit carries the log exactly as triage wrote it, so the fixture can be produced by the real write path.

## Recommendations

- **For the code review:** A cannot distinguish putting `plans/reports/.*` into `exempt-paths.sh` from dropping it in `changed-files.sh`. The exempt-paths route would also exempt uncommitted `plans/reports/` files from `verify-step.sh`'s dirt check, which changes D-91. The ruling places the drop in `changed-files.sh` beside the `plans/<job>/` prefix, so the GREEN code review should confirm that `exempt-paths.sh` is untouched.
- **For my human partner:** D does not catch an output-side `printf '%b\n' "$path"` or `echo -e "$path"`. In bash, `\s` is not an escape, so both print `back\slash.txt` unchanged (probed). A name whose backslash precedes an escape letter, such as `back\tslash.txt`, would catch them, and the four existing mutants would still red. The outline's Item 1.3 rules on the name and the expected stdout exactly, so this review leaves both unchanged.
