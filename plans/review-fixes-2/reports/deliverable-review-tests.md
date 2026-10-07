# Deliverable Review — tests

Scope: the triage modules `tests/test_triage_feedback.py`,
`tests/test_triage_feedback_behavioral.py`, `tests/test_triage_feedback_log.py`
and `tests/triage_feedback_helpers.py`. The changed-files modules
`tests/test_changed_files.py`, `tests/test_changed_files_phase.py` and
`tests/changed_files_helpers.py`. The verify-step modules
`tests/test_verify_step.py`, `tests/test_verify_step_exemption.py` and
`tests/verify_step_helpers.py`. Also `tests/test_line_limits_wc_padding.py`.
All are judged at HEAD over `d444630c..HEAD`, with the review-fixes-2 delta
from `79d0b687`. Baseline: `plans/review-fixes-2/outline.md` Items 1.1–1.4 and
1.6, and `docs/references/build-run-state.md` D-88..D-94. Every module was read
whole.

**Test run (foreground).**
`just test tests/test_triage_feedback.py tests/test_triage_feedback_behavioral.py tests/test_triage_feedback_log.py tests/test_changed_files.py tests/test_changed_files_phase.py tests/test_verify_step.py tests/test_verify_step_exemption.py tests/test_line_limits_wc_padding.py`
gave `**Summary:** 51/51 passed` and `Tests OK`. uid is 1000, so the
permission tests ran rather than skipped. The quotePath test skips only on
darwin.

**Mutation method.** Each mutant was a copy of `plugin/bin/triage-feedback.sh`
and `plugin/skills/build/scripts/*.sh`, with the tree layout kept, under
`/tmp/claude/rf2-tests-review/<mutant>/`. A pytest plugin rebound the three
helpers' `SCRIPT`, the `_run_script` keyword default and the test modules'
`SCRIPT`, which the load-guard tests copy, to point at the copy. No tracked
file was touched. Two checks confirmed the rebinding: an identity copy ran
50/50 green, and a copy whose three scripts exit 0 at the top failed 50/50.

## Round-2 findings status

- **C1 (tests): resolved.** `test_simple_with_review_reports_matches` is gone,
  and `rg` finds no trace of it. `test_reports_exclude_the_per_item_report`
  pins Simple → `match` with 0 reports, Complex → `overclassified`, which is
  reachable again, and a slice report → `Reports: 1`, `underclassified`. The
  mutant that widens `item_report_re` to `^item-.*\.md$` reds that test alone.
- **M1 (tests): resolved.**
  - `test_files_changed_is_the_review_gates_list` asserts 2, where the raw
    diff gives 6.
  - `test_behavioral_code_reads_the_lists_paths_only` covers the empty list,
    a non-empty list beside the exempt and report `def`/`class` lines, and a
    file named `*.md`.
  - Each of these mutants reds that test alone: diffing on an empty list (no
    `[[ -n $changed_list ]]` guard), and dropping `:(literal)`.
- **m4: resolved.** The `head-file` case of
  `test_odd_names_and_labels_do_not_derail_triage` covers it. Dropping `--`
  from both triage diffs reds 2 tests.
- **m5: no test, by design** (outline KD-1). The ≥2 arm at
  `triage-feedback.sh:129` is still unpinned: the mutant that drops it stays
  green, 23/23. This is known, leg 4 open item 4.
- **m6: resolved.** The `apostrophe-label` and `colon-label` cases cover it.
  Dropping the trailing-space trim from `sed` reds only
  `test_odd_names_and_labels_do_not_derail_triage`.
- **m7 (tests): resolved.** The tests are `test_rerun_appends_no_duplicate_row`,
  `test_unterminated_last_row_is_compared_and_kept_whole` and
  `test_rerun_after_the_closing_commit_appends_no_row`. Two mutants red 3 tests
  each: one always appends, the other compares the whole row with its date.
  Removing `tdd-audit.md` from the exclusion reds 2 tests.
- **N-1: resolved.** `test_unrecognised_label_is_no_classification` covers it,
  and three mutants each red that test alone:
  - dropping `Defect` from the class list;
  - the original fall-through to `match` (3 tests red);
  - taking the last `Classification:` line instead of the first.
- **M6: resolved.** Each mutant below reds
  `test_paths_with_space_and_non_ascii_bytes_are_listed_whole`, and it is the
  only test that reds (10/10 green with that test deselected):
  - `for path in $(git diff --name-only …)`;
  - a newline `read` without `-z`;
  - `git -c core.quotepath=off diff` with a newline `read`;
  - `read` without `-r`.

  Leg 4 open item 1 (an output-side `printf '%b'` or `echo -e`) was not
  re-probed and stands as ruled.
- **m20: resolved.** The docstrings of `test_verify_step.py` and
  `test_verify_step_exemption.py` both say that the split keeps each module
  under its line cap.
- **m21: resolved.** The `test_verify_step_exemption.py` docstring states
  D-91: `memory`, `.claude/handoff-*.md` and `inbox/*.md` are exempt in any
  porcelain state but a rename or copy.
- **m22: resolved.** `test_git_failure_is_error_not_no_base` holds the unborn
  case and the root-commit case. `test_no_item_report_exits_1` holds only the
  outline's scenario. Each docstring states its own reason.
- **m23: resolved.** Both load-guard tests exist, parametrized `absent`,
  `defines-nothing` and `defines-nothing-inherited`:
  - `test_unloadable_exempt_paths_is_an_error_not_no_base`;
  - `test_unloadable_exempt_paths_is_an_error_not_dirty`.

  A bare `source` with no guard reds 3/3 in each script. Dropping
  `unset EXEMPT_PATHS_ALTERNATION` reds the `inherited` case in each script.
- **Item 1.6, wc-padding docstring: resolved.** It now names the triage sites
  by what they count: the list count (`wc -l`) and the report count
  (`wc -c`), each through `tr -d ' '`, and the `review-*.md` count feeding
  only `-eq`. That matches `triage-feedback.sh:39`, `:69` and `:198`.

**Leg 4 open items 3–5, confirmed and refined.**

- **Item 4.** The three arms are unpinned at the cited lines. Mutants that
  drop the `sed failed` arm (`:152`) or the classification `grep failed` arm
  (`:158`) each stay 23/23 green.
- **Item 3, refined.** Two more interface clauses have no slice and no test
  (Minor 1 and 2 below): the exit-2 pass-through of `changed-files.sh`, and the
  usage exit.
- **Item 5, refined.** The lost `xpg_echo` recommendation is confirmed: a
  mutant that prints the unrecognised-label line with `echo -e` stays 23/23
  green, because no label carries a backslash. A second module the outline did
  not name also exists: `tests/test_triage_feedback_log.py`, created in
  `ce22286e` (Item 1.2/1) (Minor 3).

## Critical

None.

## Major

None.

## Minor

### 1. `changed-files.sh`'s `ERROR:` exit 2 is never passed through triage under test

- **File / symbol:** `tests/test_triage_feedback.py`,
  `test_no_base_is_an_error_with_no_log_row`.
- **Axis:** coverage.
- **Description:** Item 1.1's Interfaces block says exit 2 covers `NO-BASE:`
  and an `ERROR:` from `changed-files.sh`, and KD-1 says to print that output,
  then exit 2. Only the exit-1 (`NO-BASE:`) arm is exercised.
- **Evidence:** the mutant `if [[ $status -eq 1 ]]` (for `-ne 0`) stays green,
  23/23. Probed on an unborn repo:
  - real script: `ERROR: git log failed`, then
    `ERROR: changed-files.sh exited 2`, exit 2;
  - mutant: `fatal: bad revision 'ERROR: git log failed'`, then
    `ERROR: git diff failed`, exit 2. The cause line is lost from stdout, and
    the `ERROR:` string goes into git as a revision.

  It still fails closed, which keeps this Minor. An unborn-repo case in this
  test would pin it.

### 2. Triage's usage exit is untested, including the retired `<job> <base>` call

- **File / symbol:** none. The arm is `triage-feedback.sh:7–10`.
- **Axis:** coverage.
- **Description:** The interface says exit 1 and
  `Usage: triage-feedback.sh <job>` on stderr. KD-1 removed the `<base>`
  argument, so a stale caller passing a sha is the realistic misuse. No triage
  test invokes the script with zero or two arguments: `rg 'Usage|returncode == 1'`
  over the triage modules finds nothing. A mutant dropping `[[ $# -gt 1 ]]`
  would silently ignore a passed base and go green. That is reasoned from the
  grep, not run. The real script gives `Usage: triage-feedback.sh <job>`, exit
  1, for `j HEAD` (probed).

### 3. The triage split is three modules, and the hub docstring names one

- **File / symbol:** the `tests/test_triage_feedback.py` module docstring and
  `tests/test_triage_feedback_log.py`.
- **Axis:** conformance (placement), clarity.
- **Description:** The outline names `test_triage_feedback.py` plus a
  `triage_feedback_helpers.py`. HEAD adds `test_triage_feedback_behavioral.py`
  (known, item 5) and also `test_triage_feedback_log.py`, which holds Item 1.2's
  slice and the log-failure tests. The two split modules each say they were
  split "to keep each module under its line cap". The hub's docstring points
  only at the behavioural module, never at the log module, and gives no reason
  for the split, unlike `test_changed_files.py`'s pointer to the phase module.

### 4. `verify_step_helpers.py` points at a pattern that moved

- **File / symbol:** the `tests/verify_step_helpers.py` module docstring.
- **Axis:** functional correctness (documentation).
- **Description:** It says "following the subprocess-run pattern in
  ``tests/test_triage_feedback.py``". Item 1.1 moved `_run_triage` and every
  `subprocess.run` into `tests/triage_feedback_helpers.py`, so
  `test_triage_feedback.py` no longer holds a subprocess call. The pointer
  should name the helpers module.

### 5. The log module docstring says the run is skipped

- **File / symbol:** the `tests/test_triage_feedback_log.py` module docstring.
- **Axis:** clarity.
- **Description:** "a run is skipped when the log already holds a row equal to
  the new one". KD-2 and the script skip the *append*; the run still prints
  its evidence and verdict, and
  `test_rerun_after_the_closing_commit_appends_no_row` asserts that output.

### 6. `test_changed_files.py` sits 9 lines under the hard cap, with mixed citation schemes

- **File / symbol:** `tests/test_changed_files.py`, the module and
  `test_paths_with_space_and_non_ascii_bytes_are_listed_whole`.
- **Axis:** clarity, maintainability.
- **Description:**
  - **Size.** The module is 391 lines (`wc -l`), against the 400-line hard
    gate. It grew +197 in review-fixes-2. Per `memory/line-caps.md`, a file
    near 400 is already due for a split, and the next test added here breaks
    the build.
  - **Citations.** The older docstrings cite `KD-1` and `KD-6` (build-fixes
    outline), and `changed_files_helpers.py` cites "KD-1, KD-2 and KD-6 in
    `plans/build-fixes/outline.md`". The module docstring and the new tests
    cite D-88/D-90.
  - **Ambiguous item reference.** The Item 1.3 test's docstring opens "Item
    1.2 reads the diff NUL-delimited", which is build-fixes' Item 1.2. In
    review-fixes-2, whose test this is, Item 1.2 is triage's idempotent
    append. Citing D-90 would remove the ambiguity.
