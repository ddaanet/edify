# Review: build-fixes §5 review gate, `review-code` group

**Scope**: `git diff d415f22daf94eb5ae5424a927e126f4010ff7a21 HEAD` over
`plugin/skills/build/scripts/{verify-step,changed-files,exempt-paths}.sh`,
`plugin/bin/triage-feedback.sh`, `tests/{verify_step_helpers,test_verify_step,test_verify_step_exemption,changed_files_helpers,test_changed_files,test_changed_files_phase,test_triage_feedback}.py`,
`justfile`, `plugin/portable.just`, `plugin/README.md`. Read against
`plans/build-fixes/outline.md` Items 1.1–1.4, 2.11, 2.15, KD-1, KD-2, KD-6 and
the KD-7 addendum, the slice and item reports, and leg reports 1–3.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The four scripts implement KD-1, KD-2 (as `--phase`), KD-6 and the KD-7
addendum as the outline and the Item 1.4 ruling describe. They are
NUL-safe, use bash-3.2 constructs only, and depend on nothing GNU-specific.
`plugin/README.md` §Scripts matches the scripts, `SKILL.md` §2/§4.4 and
`finishing.md` §1–§3. `just lint` and `precommit` now agree on PLR0913.

The main gap was test coverage. Six behaviours that code reviews added had
no pinning test, because each of those reviews had the test files out of
scope. They are: the KD-1 `:(glob)` magic, the job-name guard, the
`git log`-failure/`NO-BASE:` split, `--no-renames` on the diff, and
`triage-feedback.sh`'s `--no-color` and failing-diff handling. Each now has a
test, and each test was proven red by an in-place mutation. One script
comment gave a false reason for `--no-renames` on the logs; it is corrected.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **KD-1's `:(glob)` `item-*` query was unpinned** (known finding 1)
   - Location: `changed-files.sh:83`; `tests/test_changed_files.py`
   - Problem: without `:(glob)`, git's pathspec `*` crosses `/`, so
     `plans/j/reports/item-x/notes.md` counts as an item report. The base
     then moves to that commit's parent, and the list gains that commit's
     files. No test noticed if the magic was removed. The 1.4/3 reviewer
     left this to the gate.
   - Fix: `test_base_is_parent_of_first_item_report_commit` gains the
     reviewer's decoy. Before P, a commit adds `plans/j/reports/item-x/notes.md`
     together with `notes.txt`. The asserted `BASE:` and list are unchanged,
     and the docstring names what the decoy catches.
   - Red: replaced `-- ":(glob)plans/$job/reports/item-*")` with
     `-- "plans/$job/reports/item-*")` (`grep -cF` = 1). The test failed on
     its assertion: wrong `BASE:`, plus `notes.txt` in the list. Restored by the
     inverse replacement: `grep -cF` on the original = 1, `:(glob)` count back
     to 3, and `git diff HEAD` on the script shows only Minor 1's comment.
   - **Status**: FIXED

2. **The job-name guard was unpinned, and its failure is a silent wrong base**
   - Location: `changed-files.sh:50-55`
   - Problem: the 1.2/1 code review added a `case` that rejects names with
     pathspec glob syntax (`*?[\`), and also `/`, `.` and `..`. Without it,
     `j*` matches job `jj`'s item report and prints `jj`'s base with exit 0.
     No test reached the guard.
   - Fix: `test_unsafe_job_name_is_a_usage_error`. The repo holds a committed
     `plans/jj/reports/item-1-1.md`. Each of `j*`, `j?`, `[j]j`, `j\`, `''`,
     `.`, `..` and `jj/sub` must exit 2 with `ERROR:`.
   - Red: dropped `| *[*?[\\]*` from the `case`. `j*` printed
     `BASE: <jj's base>`, `a.txt`, `plans/jj/reports/item-1-1.md` with exit 0,
     and the test failed `(0, 'BASE: ') == (2, 'ERROR:')`. Restored and
     grep-proven.
   - **Status**: FIXED

### Minor Issues

1. **The `--no-renames` comment gave a false reason for the logs**
   - Location: `changed-files.sh:22-27`
   - Problem: the comment said `--no-renames` on the logs makes "a report
     renamed into place count as added". It does not need to. A path-limited
     `git log` pairs no rename source from outside its pathspec, so such a
     report is an `A` with or without the flag. Probed on git 2.47.3 twice:
     `plans/j/draft.md` → `reports/item-1-1.md`, and `reports/draft.md` →
     `reports/item-1-1.md`. Both forms of the pathspec gave the same result.
     The record (`item-1-2-s3-code-review.md` Major 1) makes the same log-side
     claim, so the record and the code disagree on why the flag is there. The
     diff-side claim holds: the rename test below pins it.
   - Fix: the comment now gives the diff's reasons (both paths listed, no
     rename warning in stdout). It says the logs carry the flag for
     uniformity only, and why that is harmless. The flags stay. The plans
     record is outside this review (Scope OUT).
   - **Status**: FIXED

2. **`git log` failure versus `NO-BASE:` was unpinned**
   - Location: `changed-files.sh:83-86`
   - Problem: exit 1 means exactly "no committed item report". If `git log`
     fails, the result must be exit 2. The 1.2/3 code review's mutant survived
     the suite.
   - Fix: `test_no_item_report_exits_1` gains an unborn-HEAD repo. It expects
     exit 2, `ERROR: git log failed`, and no `NO-BASE:`. The docstring
     paragraph on exit 1 was extended.
   - Red: replaced the branch's `echo "ERROR: git log failed"` / `exit 2` with
     `first_commit=""`. The result was exit 1 with `NO-BASE:`, and the test
     failed `1 == 2`. Restored and grep-proven.
   - **Status**: FIXED

3. **`--no-renames` on the diff was unpinned**
   - Location: `changed-files.sh:115`
   - Problem: the 1.2/3 review added the flag and pinned nothing. Under
     git's default `diff.renames`, a renamed file lists only its new path.
   - Fix: `test_renamed_file_lists_both_paths`. The run renames the
     pre-run `b.txt` to `c.txt`, and the list must be `b.txt`, `c.txt`.
   - Red: removed `--no-renames` from the diff. The list was `c.txt` only,
     and the test failed. Restored and grep-proven.
   - **Status**: FIXED

4. **`triage-feedback.sh`'s `--no-color` and its failing-diff handling were
   unpinned**
   - Location: `plugin/bin/triage-feedback.sh:42-50`
   - Problem: the 1.3/2 code review fixed both and wrote that "a regression
     back to the piped form would pass the suite".
   - Fix: `test_forced_color_does_not_hide_definitions` (repo-local
     `color.ui always` plus a committed `def` → `yes`), and
     `test_failing_diff_is_an_error_not_no`. The second deletes the committed
     blob, so `--name-only` succeeds and the patch fails. It expects a
     non-zero exit, git's `unable to read <blob>` on stderr (which ties the
     failure to the patch, not to the count), and no `Behavioral code:` line.
     `_triage_lines` now delegates to a new `_run_triage`, so the failure
     test can inspect a non-zero exit.
   - Red: (a) dropped `--no-color`, and the test read `Behavioral code: no`.
     (b) appended `|| committed_diff=""`, which gave exit 0 and
     `Behavioral code: no`, the pre-fix failure mode. Each was restored by the
     inverse replacement, and `git diff HEAD -- plugin/bin/triage-feedback.sh`
     is empty.
   - **Status**: FIXED

5. **Stale fixture reference**
   - Location: `tests/changed_files_helpers.py:6`
   - Problem: it cited `_init_repo` in `tests/test_verify_step.py`, which
     moved to `tests/verify_step_helpers.py` in the 1.4/4 split.
   - **Status**: FIXED

6. **Process narration in a test docstring**
   - Location: `tests/test_changed_files_phase.py`
     `test_phase_flag_only_as_exact_second_argument`
   - Problem: "The guard already holds, so this test is red-neutral against
     the current script". This describes the test's history, will go stale,
     and says nothing the test pins. Its red is in `item-1-4-s2-red.md`.
   - **Status**: FIXED (sentence removed)

## Known finding 2: `printf '%s\n'` DIRTY listing — no test

**Decided: not warranted.** `printf` replaced `echo "$status"` at the 1.4/4
code review. It guards against an inherited `BASHOPTS=xpg_echo`, under which
`echo` expands git's C-quoted escapes (`\t`, `\nnn`) in the listing. Three
facts make a test poor value:

- the verdict and exit code are the same either way;
- the listing is read, not parsed: the KD-3 revert takes its paths from
  `git status -z`, never from this listing;
- the trigger is an exported `BASHOPTS`, which nothing in the pipeline sets.

The change follows a project rule (`shell-scripting:shell-gotchas` rule 5:
`printf` for data). It is not a behaviour with a consumer that would notice
a regression.

## Considered, not raised

- `triage-feedback.sh:48` uses a here-string. `verify-step.sh` avoids
  here-strings because a temp-file failure exits 1. Here that failure would
  read as "no". Bash falls back from an unwritable `TMPDIR` to `/tmp`, and
  the stake is one triage log line, so this is a guard against a state that
  does not arise in practice.
- `changed-files.sh`'s `cd "$top"` (subdirectory CWD) is untested. Without
  it the pathspecs match nothing, so the script prints `NO-BASE:`, which
  every call site treats as STOP. That failure is closed, and `/build`
  runs from the root.
- `--no-ext-diff` and `--no-show-signature` are untested. Each needs a
  configured external program or a signing setup to exercise. Not raised.
- `test_verify_step_exemption.py`'s module docstring still says
  `` M memory``. The text moved with the 1.4/4 split and predates this run.

## Fixes Applied

- `plugin/skills/build/scripts/changed-files.sh:22-27` — the `--no-renames`
  comment is corrected (Minor 1). No code change.
- `tests/test_changed_files.py` — `item-x/notes.md` decoy and docstring in
  `test_base_is_parent_of_first_item_report_commit` (Major 1). Unborn-HEAD
  case in `test_no_item_report_exits_1` (Minor 2). New
  `test_unsafe_job_name_is_a_usage_error` (Major 2) and
  `test_renamed_file_lists_both_paths` (Minor 3). 172 → 236 lines.
- `tests/test_triage_feedback.py` — new `_run_triage`, `_triage_lines`
  delegates to it, and two new tests (Minor 4). 212 → 256 lines.
- `tests/changed_files_helpers.py:6` — reference corrected (Minor 5).
- `tests/test_changed_files_phase.py` — narration sentence removed (Minor 6).

**Files changed by this review:**

- `plugin/skills/build/scripts/changed-files.sh`
- `tests/test_changed_files.py`
- `tests/test_triage_feedback.py`
- `tests/changed_files_helpers.py`
- `tests/test_changed_files_phase.py`

Nothing is staged or committed. The index and `.claude/handoff-todo.md` are
untouched.

**Gates with the fixes in the tree:**

- `just format`: no further changes.
- `just precommit`: version consistency, tests 383/384 passed with 1 xfail,
  line limits (only the three allowlisted `*-corrector.md` agents), design
  links (94 decisions, 9 nodes). `Precommit OK`.
- `just lint`: `Lint OK`.
- `shellcheck -x` on the four scripts: clean.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Item 1.1 (Major 6, F-4): porcelain states, single-level globs | Satisfied | `test_exempt_paths_clean_in_any_porcelain_state` (`A `, ` D`, `UU`, `D `); `test_nested_path_under_exempt_dir_is_dirty`. Mutation reds in the 1.1 RED reports |
| Item 1.2 (Major 1, m1, m2, m18): `changed-files.sh`, `exempt-paths.sh`, `verify-step.sh` sources it | Satisfied | Interface exits 0/1/2 as specified; NUL loop; three slice tests plus this review's job-name, rename and unborn tests |
| Item 1.3 (m18): both triage diffs `"$baseline_commit" HEAD` | Satisfied | `triage-feedback.sh:15`, `:46`; slice tests, plus this review's two |
| Item 1.4: `--phase` | Satisfied | `changed-files.sh:100-108`; four tests in `test_changed_files_phase.py`; `test_quotepath_false_does_not_hide_dirt` (slice 4) |
| Item 2.11 (m17): README §Scripts | Satisfied | Call sites match `SKILL.md` §2, §4.4 and `finishing.md` §1, §3; both new scripts described accurately |
| Item 2.15: `lint` agrees with `precommit` on PLR0913; RUF100 not ignored | Satisfied | One-token removal in `justfile:154` and `plugin/portable.just:45`; `just lint` OK |
| KD-1 | Satisfied | Shipped query adds `:(glob)` and `--no-renames`/`--no-show-signature`, recorded in the 1.2/3 and 1.4/3 reviews; `:(glob)` now pinned (Major 1). Reasons for `--no-renames` corrected (Minor 1) |
| KD-2 | Satisfied as amended by Item 1.4 | `phase-*-corrector.md` path, no `--diff-filter`, `-1`, range from the run base; subject decoy pinned |
| KD-6 | Satisfied | One sourced alternation; `<base> HEAD`; `plans/<job>/` and exempt paths dropped |
| KD-7 addendum | Satisfied (code side) | `verify-step.sh:169-171` comment; `test_rename_out_of_exempt_path_is_dirty` reds if `R` leaves the class. The design record is Item 2.14's, in another group |

**Gaps:** none.

## Positive Observations

- `--phase` changes only `base_sha` and feeds the same print-and-filter
  path, so the two lists cannot drift apart.
- Every fallible command in `changed-files.sh` has an explicit exit-2
  branch. Exit 1 is reachable only from the `NO-BASE:` test, and the
  comments explain each guard.
- The decoy fixtures in the base and phase tests each rule out a named wrong
  derivation, and the pinned values are mutually distinct.
- The README bullet narrows "review scopes" to the phase-boundary and
  review-gate scopes. That is correct, because §4.1's corrector uses the
  working-tree form.
