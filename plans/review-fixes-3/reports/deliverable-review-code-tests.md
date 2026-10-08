# Deliverable Review — code and tests: review-fixes-3

## Scope

Layer 1, code and tests partition. Range `daad4769..HEAD`, judged at HEAD
against `plans/review-fixes-3/outline.md` (KD-4, KD-5, KD-6, KD-7, Items 1.1,
1.2, 2.1–2.4, the scope lists). The round-3 findings it fixes come from
`plans/review-fixes-2/reports/deliverable-review.md`.

Files:

- `plugin/bin/triage-feedback.sh`
- `plugin/skills/build/scripts/changed-files.sh`
- `tests/changed_files_helpers.py`
- `tests/test_build_prose_git_log.py`
- `tests/test_changed_files.py`
- `tests/test_changed_files_errors.py`
- `tests/test_changed_files_phase.py`
- `tests/test_triage_feedback.py`
- `tests/test_triage_feedback_behavioral.py`
- `tests/test_triage_feedback_failures.py`
- `tests/test_triage_feedback_location.py`
- `tests/test_triage_feedback_log.py`
- `tests/triage_feedback_helpers.py`
- `tests/verify_step_helpers.py`

Method:

- Read each file whole, then its range diff.
- Ran the targeted modules at HEAD: changed-files 16/16 passed, triage 33/33,
  prose `git log` 10/10.
- Mutation runs went against a copy of `tests/`, `plugin/` and `docs/` under
  `/tmp/mut`, so the repo stayed untouched. Every mutant was restored and
  `cmp`-checked against the repo file.
- Shell probes ran on throwaway repos under `/tmp/probe.eEbc`.
- Ran bash 3.2.57 (`/tmp/claude-1000/bash32/bin/bash`), shellcheck 0.10.0,
  `docformatter -c`, `ruff check` and `ruff format --check`.

Out of scope, per the dispatch, and not raised:

- the bash-3.2 `source` defect when `exempt-paths.sh` is absent;
- the missing bash-3.2 suite run;
- test D's `printf '%b'` gap;
- final-review fixes landing after triage;
- `SKILL.md`;
- the corrector-family agents.

## Critical

None.

## Major

None.

## Minor

### Minor 1. The untested repository-root `cd` arm is reachable by the suite's existing `PATH`-shim mechanism

- **File / symbol:** `plugin/bin/triage-feedback.sh`, the
  `if ! cd "$repo_root"` guard and the residual-bound comment above it.
- **Axes:** Test coverage; Code testability and error signaling.
- **Severity:** Minor. Item 2.2's interface declared this bound in advance, so
  the code conforms to the outline. The defect is the bound's justification
  and the coverage hole it leaves.

**Description.** The comment says neither `cd` has a test because "no input
provokes either without fault injection". KD-5 reversed review-fixes-2's m5
exemption on the grounds that the suite already injects faults through a
`PATH` shim. That reasoning applies to the root `cd` as well. A shim cannot
replace the builtin `cd`, but `repo_root` comes from the external
`git rev-parse --show-toplevel`. A `git` shim written with `_write_shim` and
passed through `_run_triage(path_prepend=…)` therefore drives the guard.

**Why it matters.** Without the guard, `set -e` exits 1, which is the usage
error's code, and prints no `ERROR:` line. Every other guard this job added
exists to prevent that failure class, and the suite cannot see this one go.

**Evidence:**

- **Probe (existing mechanism).** A `git` shim answers
  `rev-parse --show-toplevel` with `/nonexistent/x` and passes every other
  call through. Triage prints `ERROR: cannot change to /nonexistent/x` and
  exits 2.
- **Probe (plain input).** A repository whose root directory name ends in a
  newline. `$(git rev-parse --show-toplevel)` strips the newline, so `cd`
  fails. The output is `ERROR: cannot change to …/repo`, exit 2, with no fault
  injection. "No input provokes it" is therefore overstated. The truncation
  comes from the `$(git rev-parse …)` idiom that `changed-files.sh` also
  uses, and the new guard handles it correctly.
- **Mutant.** The guard was replaced with a bare `cd "$repo_root"`. On the
  trailing-newline repo the script exits 1 with empty stdout.
- **Surviving mutants.** With both `cd` guards dropped together, all five
  triage modules pass: 33/33.

**Pin it with one test in `tests/test_triage_feedback_failures.py`:**

- set up `_underclassified_repo`;
- add a `git` shim that prints a missing directory for
  `rev-parse --show-toplevel`;
- expect exit 2, stdout exactly one `ERROR: cannot change to …` line, and no
  log row.

The comment then narrows to the script-directory `cd`. That arm's bound
stands: it is a builtin with no external input, and no mechanism in the suite
reaches it.

**Bound on the bound.** An exported bash function (`BASH_FUNC_cd%%`) did
reach the script-directory arm here. With the guard, the script exited 2
under both bash 5 and bash 3.2.57. Without it, it exited 1; that run was made
under bash 5 only. That would be a new mechanism
whose environment format depends on the bash version, not an existing one, so
it is not raised as a finding.

## Checked clean

### Round-3 findings, code side

- **m1 (KD-6).** The root `cd`, absolute `script_dir` before it,
  `unset CDPATH` and the `rev-parse` exit-2 arm all behave as specified:
  - Outside a work tree: one `ERROR:` line, git's own message on stderr,
    nothing created.
  - Subdirectory run through a relative `BASH_SOURCE` and the `CDPATH` decoy
    run are both correct.
- **Whitespace.** A run from `sub dir` of `my repo`, through a symlink under
  `link dir`, with a changed file `a b.py`, gives `Files changed: 1`,
  `Reports: 1`, `Behavioral code: yes`, `underclassified` and one root log row.
- **Bash 3.2.57.** `bash -n` passes on both scripts. The subdirectory-with-
  spaces probe and the `CDPATH` probe give the same results under it.
- **macOS.** No GNU-only flag was added. The tests assert only paths, not
  wording, from `mkdir` and `grep` diagnostics, and their docstrings state the
  BSD bound.
- **m2 / m18 (KD-4).** `changed-files.sh` builds the list in a capture with an
  `x` sentinel and prints `BASE:` and the paths only after it succeeds. Every
  failure exit prints `ERROR:` before anything else. The only exceptions are
  the two final stdout-write failures (`printf … || exit 2`), where stdout
  cannot be written at all.
  - `test_late_diff_failure_prints_error_alone` passes at HEAD.
  - Against `daad4769`'s script it fails with `BASE: <sha>` first: a genuine
    red.
  - The header comment states the order. Every line over 80 columns in either
    script is code, not comment.
- **m4–m6 (KD-5).** Each new triage failure test was killed by its named
  mutant, on the intended assertion:
  - `test_usage_error_exits_1[no-args]` (drop `[[ -z "$job_dir" ]] ||`):
    `assert 2 == 1`, with `changed-files.sh`'s "not a job name".
  - `[stale-base]` (drop `|| [[ $# -gt 1 ]]`): `assert 0 == 1`, a verdict
    printed.
  - `test_changed_files_error_is_printed_then_exit_2` (`-ne 0` → `-eq 1`):
    stdout `['ERROR: git diff failed']` against the expected two lines.
  - `test_failing_label_sed_is_an_error` (sed guard dropped): stdout `[]`,
    exit 4.
  - `test_unreadable_classification_is_an_error` (classification grep `*)`
    arm dropped): `## Evidence` printed.
  - `test_failing_definition_grep_is_an_error_not_no` (behavioural grep `*)`
    arm dropped): `## Evidence` printed.
  - `test_unwritable_log_is_an_error_not_a_usage_exit[directory]` (`mkdir`
    guard dropped): exit 1, no `ERROR:` line.
  - `test_cdpath_does_not_move_the_script_dir` (`unset CDPATH` dropped):
    stdout `['', 'ERROR: changed-files.sh exited 127']`.
- **Permission fixtures.** They skip as root and restore modes in `finally`,
  including `plans/` in the `directory` case.
- **m14 (KD-7), `tests/test_build_prose_git_log.py`.**
  - The extraction is non-vacuous. Each scanned file adds a failing
    `<file>:missed` case, not a skip, when it yields no command or fewer
    commands than its `--format=%H` count. At HEAD the counts match:
    phase-boundary 1, tdd-slice 1, escalation 1, tdd-auditor 1,
    build-run-state 2, pipeline-contracts 1, finishing 3.
  - The placeholder table matches the outline.
  - A leftover `<…>` fails the test.
  - It skips only when `ssh-keygen` is absent or git is older than 2.34, and
    both skip messages give the reason.
  - The fixture asserts its own discriminating state: every commit is
    `%G?` = `G`, and a bare `git log -1 --format=%H` prints a non-hash line.
  - `SCANNED` includes `docs/references/pipeline-contracts.md`. Stripping
    `--no-show-signature` from its D-86 query fails
    `pipeline-contracts.md:1` with the `Good "git" signature …` line.
  - No other `git log … --format=%H` exists under `plugin/`, `docs/` or
    `agents/` outside the scanned set and the two scripts.
- **m10 (Item 1.1).**
  - `grep -rn 'KD-' tests/` finds nothing in the changed-files modules or
    their helpers.
  - The one hit among the changed triage files, `*KD-3*` in
    `test_triage_feedback.py`, is fixture data for the unrecognised-label
    test, not a citation.
  - The remaining hits are in modules outside this job.
- **Docstring summaries.** An AST pass found no summary line over 70
  characters that this range added or changed. The ones over 70 predate the
  range. `docformatter -c`, `ruff check` and `ruff format --check` are clean on
  all twelve test files.
- **Split modules.** Each split module states what it holds and that it was
  split to keep each module under its line cap. Both hubs point at all their
  siblings. All modules are at or under 308 lines.
- **Test counts.**
  - Changed-files: 15 before, counted at `daad4769` from test functions and
    parametrize cases rather than collected, and 16 collected after. The
    difference is the one new test.
  - Triage: 33 collected at HEAD, of which 10 are new in this range.
  - The four moved changed-files tests are unchanged apart from the KD →
    D-ID citation edits.
  - The two moved triage tests were moved unchanged at the split
    (`34f40fcf`). The 2.3/2 refactor (`e83f26b8`) later rewrote
    `test_failing_reports_diff_is_an_error_not_none`'s shim through
    `_write_shim`, as the outline's list revision after 2.3/2 sanctions.
- **m7, m8, m9 (Item 1.2).** All three are satisfied:
  - m7: the hub names all four siblings, each with what it holds.
  - m8: `verify_step_helpers.py` points at `triage_feedback_helpers.py`.
  - m9: the log docstring says the append is skipped and the run still prints.
- **Shims.** `_write_shim` embeds the real path with `shlex.quote`. Every shim
  written in the range goes through it: the `git` shims in the
  late-diff-failure and reports-diff tests, the `sed` shim and the `grep`
  shim. Each shim passes every other call through.
- **shellcheck.** It is clean on both scripts. The only output is SC1091,
  info-level, on `changed-files.sh`'s `source`, which predates the range.

### Observed and not raised

`tests/triage_feedback_helpers.py`'s module docstring says
`_run_triage_relative` runs the script "from a subdirectory". The `CDPATH`
test uses it with the repository root as CWD. The function's own docstring
("relative to `cwd`") is accurate.

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| Major | 0 |
| Minor | 1 |

The code and tests resolve m1, m2, m4–m10, m18 and the code side of m14 as
the outline's item contracts state.

The one finding is about the residual bound on triage's two `cd` arms. The
repository-root `cd` guard is reachable by the existing `git` `PATH` shim, and
also by a plain input: a root directory name ending in a newline. That is the
mechanism KD-5 used to reverse a test exemption. Dropping the guard exits 1,
the usage code, and the suite stays green. The script-directory `cd` bound is
acceptable: it is a builtin, and nothing in the suite reaches it.
