# Deliverable Review — tests

Scope: `tests/test_verify_step.py`, `tests/test_verify_step_exemption.py`,
`tests/verify_step_helpers.py`, `tests/test_changed_files.py`,
`tests/test_changed_files_phase.py`, `tests/changed_files_helpers.py`,
`tests/test_triage_feedback.py` at HEAD. Baseline:
`plans/build-fixes/outline.md` (Items 1.1–1.4, KD-1, KD-2, KD-6).

Targeted run (foreground):
`just test tests/test_changed_files.py tests/test_changed_files_phase.py tests/test_verify_step.py tests/test_verify_step_exemption.py tests/test_triage_feedback.py`
gave `**Summary:** 23/23 passed`, `Tests OK`.

Vacuity was checked by mutation. Each mutant was a copy of
`plugin/skills/build/scripts/` (or of `plugin/bin/triage-feedback.sh`) under
`$TMPDIR/mut/`, and a pytest plugin rebound each helper module's `SCRIPT` to
the copy. No tracked file was touched. To confirm the rebinding took effect,
an identity copy ran 18/18 green, and a copy of `changed-files.sh` that exits 0
at the top failed all 9 changed-files tests.

## Critical

None.

## Major

### M-1 — No test pins the NUL-delimited read; a whitespace-splitting `changed-files.sh` stays green

- **File / test:** `tests/test_changed_files.py` and
  `tests/test_changed_files_phase.py`: the whole changed-files suite.
- **Axis:** coverage of a specified scenario, vacuity.
- **Description:** Item 1.2's Interfaces block says: "Paths are read from a
  NUL-delimited diff, never split on whitespace." No fixture path in either
  module holds a space or a non-ASCII byte, so no test can tell the specified
  read from a broken one. The item reviews checked this property only with
  hand-run probes (`item-1-2-s1-code-review.md` probe D). The suite does not
  encode it.
- **Evidence:** I ran two mutants against all 18 changed-files and verify-step
  tests, and both stayed green:
  - c12 replaces the `git diff -z … | while IFS= read -r -d '' path` loop with
    `for path in $(git diff --name-only …)`. In a probe repo it prints
    `my file.txt` as two lines, `my` and `file.txt`.
  - c11 keeps a newline `read` but drops `-z`. In the probe it prints
    `"caf\303\251.txt"` instead of `café.txt`. It also lists an exempt
    `inbox/é.md` brief as `"inbox/\303\251.md"`, which the exempt regex then
    fails to drop.

  The real script prints `café.txt` and `my file.txt` and drops `inbox/é.md`.
  The fix is one fixture: commit `my file.txt` and an `inbox/é.md` in a run
  commit, and assert the exact list.

## Minor

### m-1 — Item 1.1 tests are not in the file the outline names, and the moved files do not say why

- **File / test:** `tests/test_verify_step_exemption.py`:
  `test_exempt_paths_clean_in_any_porcelain_state` and
  `test_nested_path_under_exempt_dir_is_dirty`.
- **Axis:** conformance (placement).
- **Description:** The outline places Item 1.1 in `tests/test_verify_step.py`,
  and its Scope lists three test files. Both slices now live in
  `tests/test_verify_step_exemption.py`, after the 1.4/4 line-cap split, which
  also created `tests/verify_step_helpers.py`. Item 1.4 slices 1–3 likewise sit
  in `tests/test_changed_files_phase.py`, not in `tests/test_changed_files.py`.
  That move is explained in `test_changed_files_phase.py`'s module docstring
  ("to keep each module under its line cap"), as the repo's other splits do,
  e.g. `test_review_range_no_prior.py`. The verify-step split is explained only
  in `plans/build-fixes/reports/item-1-4-s4-red.md` §Split. The docstrings of
  `test_verify_step.py` and `test_verify_step_exemption.py` say where the tests
  live, but not why. The outline was not revised for either move.
- **Evidence:** `test_verify_step.py` docstring: "The exemption-pattern tests
  live in `tests/test_verify_step_exemption.py`". It gives no reason.
  `git log` shows `88ef264e` (Item 1.4/4) splitting 370 lines out of
  `test_verify_step.py`.

### m-2 — The `test_verify_step_exemption.py` module docstring still states the pre-KD-7 `memory` exemption

- **File / test:** `tests/test_verify_step_exemption.py`, module docstring.
- **Axis:** functional correctness of documentation, clarity.
- **Description:** The docstring lists "`` M memory``" as the exemption. Under
  KD-7 / D-91, `memory` is exempt in any porcelain state.
  `test_memory_gitlink_is_clean_and_a_sibling_name_is_not` in the same module
  pins `MM memory`. `review-code.md` §Considered, not raised notes this text
  and leaves it unfixed, so it is still wrong at HEAD.

### m-3 — `test_no_item_report_exits_1` also pins two exit-2 branches its name does not claim

- **File / test:** `tests/test_changed_files.py`,
  `test_no_item_report_exits_1`.
- **Axis:** specificity, naming.
- **Description:** The test runs three repos:
  - an unborn repo, which must give exit 2 with `ERROR: git log failed`;
  - a root commit carrying the item report, which must give exit 2 with
    `ERROR:`;
  - the outline's scenario, which must give exit 1 with `NO-BASE:`.

  The exit-2 checks run first. A regression in either error branch therefore
  fails under a name that says "exits 1", and the outline's own scenario never
  runs. The docstring states the ordering on purpose, so that a `NO-BASE:`
  answered from a failure branch reds. Splitting the exit-2 cases into their own
  test, e.g. `test_git_failure_is_error_not_no_base`, would keep that
  discrimination and let each name say what it proves.

### m-4 — The fail-closed `exempt-paths.sh` load guard is untested in both scripts

- **File / test:** none. The guard is in `verify-step.sh` and
  `changed-files.sh`.
- **Axis:** coverage.
- **Description:** Both scripts exit 2 with
  `ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh`. Their
  comments argue that the code matters: without the guard, `set -u` exits 1,
  which `verify-step.sh` callers read as DIRTY and `changed-files.sh` callers
  read as `NO-BASE:`. The outline does not specify the guard, which is why this
  is Minor. No test greps for `cannot load`. The only `exempt-paths` mention
  under `tests/` is a docstring in `test_changed_files.py`. Unverified by
  mutant: reasoned from the grep and the script text.

## Checked and found sound

- **Conformance, Item 1.1/1.**
  `test_exempt_paths_clean_in_any_porcelain_state` builds:
  - `A  .claude/handoff-new.md`;
  - ` D .claude/handoff-task.md`;
  - `UU inbox/conflict.md`, from a real two-branch merge;
  - `D  inbox/old.md`.

  It asserts the exact porcelain before running the script, then exit 0,
  `CLEAN:`, and one `precommit` call. The outline's mutant (`[ M?][ M?]`) fails
  it, and only it (m1: 1 failed).
- **Conformance, Item 1.1/2.** `test_nested_path_under_exempt_dir_is_dirty`
  covers both nested paths, with single-level siblings as decoys and an exact
  DIRTY listing. Widening both `[^/]+` to `.+` in `exempt-paths.sh` fails it
  (m2). The same mutant also fails the two changed-files filter tests and the
  quotePath test, which shows that both scripts read the shared file.
- **Conformance, Item 1.2/1–3.** Each slice's fixture contains the outline's
  scenario, plus decoys that each rule out one wrong derivation. All the
  mutants failed the expected test:
  - an unglobbed item pathspec (c1);
  - a working-tree diff (c5);
  - a `reports/`-only job filter (c6);
  - an unanchored exempt regex (c14).
- **Conformance, Item 1.3/1–2.** Files changed asserts 3, not the outline's 1.
  That is a strengthening: 3 differs from the count of every neighbouring
  range. The behavioural test pairs the outline's negative with a committed
  positive. All six range mutants failed the expected test:
  - working tree, index, or `HEAD~1` for the count (t1, t1b, t1c);
  - the same three ranges for the patch (t2, t2b, t2c).
- **Conformance, Item 1.4/1–3.** All four mutants failed the expected test:
  - `--phase` ignored (c2);
  - `--diff-filter=A` on the phase query (c3);
  - the `<base>..HEAD` range dropped (c4);
  - oldest-first selection (c10).

  The `:(glob)` magic on the phase pathspec (c7) is pinned. The filters under
  `--phase` are pinned for both the exempt match (c8) and the `plans/<job>/`
  drop (c9).
- **Conformance, Item 1.4/4.** `test_quotepath_false_does_not_hide_dirt` sits
  in `tests/test_verify_step.py`, the verify-step tests, as the outline asks.
  Dropping `-c core.quotePath=true` fails it (m3). It still discriminates
  without the `C.UTF-8` locale. Under `LC_ALL=C` the mutant prints the raw
  `\377` byte, which cannot equal the expected quoted line (probed).
- **Platform skip.** Only the quotePath test is skipped, on `darwin`, for a
  correct reason: APFS rejects a non-UTF-8 name, so the fixture cannot exist.
- **Excess.** Every test beyond the outline states its hazard in its
  docstring, and each traces to a review fix:
  - `test_unsafe_job_name_is_a_usage_error`;
  - `test_renamed_file_lists_both_paths`;
  - `test_phase_flag_only_as_exact_second_argument`;
  - `test_forced_color_does_not_hide_definitions`;
  - `test_failing_diff_is_an_error_not_no`.

  The two helper modules exist for the line-cap splits.
- **Independence.** Each test builds its own repo under `tmp_path`, nulls
  global and system git config, and keeps its `just` stub and marker per test.
  `GIT_DIR` inheritance is F-5 and out of scope.
- **Line caps.** Every file is at or under 256 lines.
- **Subdirectory CWD.** Removing `cd "$top"` survives the suite (c13). From a
  subdirectory the mutant prints `NO-BASE:` and exits 1, which call sites treat
  as STOP. I agree with `review-code.md` that this fails closed. Not raised.
