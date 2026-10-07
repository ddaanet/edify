# Review: Item 2.3 slice 1 — code review

**Scope**: the slice commit's test code (no SUT diff, by design, under KD-5):
`tests/test_triage_feedback_failures.py` (`test_usage_error_exits_1`
[`no-args`, `stale-base`], `test_changed_files_error_is_printed_then_exit_2`,
the module docstring) and `tests/triage_feedback_helpers.py` (`_run_triage`
gained `job: str | None` and `extra_args`). The SUT
`plugin/bin/triage-feedback.sh` was read against the Interfaces these tests
pin, and mutated once in place, then restored.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The two tests and the helper change are sound. The tests read the interface
they pin: `Usage:` on stderr with empty stdout for the usage error, and the
exact `ERROR:` lines on stdout for the `changed-files.sh` arm. The helper
extension is minimal and consistent with the other keyword options. The
docstrings are accurate and within their length limits. No issue was found,
and no file was changed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Dispatch questions, answered

- **Helper API shape (`_run_triage`).**
  - `extra_args: tuple[str, ...] = ()` sits last, as a keyword option like
    `path_prepend` and `env_extra`. It uses an immutable default, so it needs
    no `None` sentinel as `env_extra` does.
  - `job: str | None` lets the `no-args` case go through the same
    `GIT_CONFIG_*` insulation as every other run. The test review introduced
    it to replace a bare `subprocess.run`.
  - Examined and accepted: `_run_triage(None, repo, extra_args=("x",))` would
    make `"x"` the first argument, so the docstring's "follow the job argument"
    is loose for that combination. No caller makes that call. A single argv
    override would cover it, but that is speculative generality, and it would
    touch the 14 existing `str` callers.
  - `_run_triage_relative` keeps `job: str` and gains no `extra_args`. That is
    minimal growth: no test runs the relative form with a non-standard argv.
- **Duplication.**
  - The no-row assertion repeats
    `repo / "plans" / "reports" / "triage-feedback-log.md"`. The same literal
    appears 13 times across the five triage modules, and no helper exists for
    it, so this follows the project pattern and is not flagged.
  - The unborn-repo fixture calls `_run_git(repo, "init", ...)` rather than
    `_init_repo`. That is deliberate: `_init_repo` makes a seed commit, and
    the test needs a repo with no commits.
- **Docstrings.**
  - Summary lengths: 67 characters ("Zero or two or more arguments exit 1 with
    the usage line on stderr.") and 69 characters ("A ``changed-files.sh``
    exit 2 prints its output, then triage's cause."). Both are within 70.
  - The module docstring now lists the usage error and the
    `changed-files.sh`-output-first arm alongside the earlier arms.
  - "the retired two-argument form" is correct. `git log -S'$# -gt 1'` shows
    the old usage line `triage-feedback.sh <job-dir> <baseline-commit>`.
  - The fixture claim in `test_usage_error_exits_1` is correct. The same commit
    adds `item-1-1.md`, `classification.md` (`Simple`) and a `def`, so the run
    base is its parent. `j` alone therefore reaches `underclassified` and logs
    a row, which the RED report's control run confirms.
  - `_run_triage`'s new sentence is accurate.
  - `command grep -n 'KD-\|slice [0-9]\|Item [0-9]\|\bm[0-9]\+\b'` over both
    files finds nothing (exit 1). `(D-90)` is a decision ID, which is allowed.
- **Naming.** `test_usage_error_exits_1` and
  `test_changed_files_error_is_printed_then_exit_2` follow the module's
  behaviour-sentence convention. The parametrize ids `no-args` and
  `stale-base` match the runbook's case names.
- **The tests read the interface they pin.**
  - The usage cases assert `returncode == 1`, then
    `stderr.strip() == "Usage: triage-feedback.sh <job>"` and `stdout == ""`.
  - The `changed-files.sh` case asserts stdout lines `==`
    `["ERROR: git log failed", "ERROR: changed-files.sh exited 2"]`, plus
    exit 2. The exact equality also pins "stops", as the test review's
    mutant E showed.
- **The SUT matches the Interfaces.**
  - `triage-feedback.sh:5-10`: `job_dir="${1:-}"`, then
    `[[ -z "$job_dir" ]] || [[ $# -gt 1 ]]`, then the usage line `>&2` and
    `exit 1`.
  - `:48-54`: the `changed-files.sh` capture uses `|| status=$?`. On
    `$status -ne 0` it prints `printf '%s\n' "$changed_output"`, then
    `ERROR: changed-files.sh exited $status`, then `exit 2`. That is "its
    output first, then the cause, then stop".

## Mutated-SUT run (once)

| Mutation (exact, single occurrence) | Result |
|---|---|
| `echo "Usage: triage-feedback.sh <job>" >&2` → `echo "Usage: triage-feedback.sh <job>"` (usage to stdout) | `[no-args]` red, `[stale-base]` red, both on `assert '' == 'Usage: triage-feedback.sh <job>'` (the stderr equality) |

This mutation differs from those in the RED report and the test review. It
confirms the stdout/stderr split itself is pinned, not just the exit code.

The SUT was restored by inverting the replacement with Edit. Proof of the
restore:

- `git diff -- plugin/bin/triage-feedback.sh` is 0 bytes;
- `command grep -c 'Usage: triage-feedback.sh <job>" >&2'` returns 1;
- `git status --porcelain` shows only the two untracked `inbox/brief-*.md`
  files.

## Fixes Applied

None. Nothing needed changing.

## Verification

- `PATH=.venv/bin:$PATH just precommit` reported:
  - version consistent 0.3.0;
  - `Tests cached (inputs unchanged)`;
  - line limits ran, warning `oversized-file` on `plugin/agents/corrector.md`
    (682), `outline-corrector.md` (450) and `design-corrector.md` (460), all
    outside this slice;
  - design links: 94 decisions, 9 nodes;
  - `Precommit OK`.
- Because tests were cached, `.venv/bin/pytest -p no:markdown_report
  tests/test_triage_feedback*.py` was also run: 29 passed.
- Recall was loaded: the recall artifact's eight memory files, plus
  `shell-scripting:shell-gotchas` and `craft:test-discipline` (SKILL.md).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m6 (usage exits 1: zero args, stale two-arg form) | Satisfied | `test_usage_error_exits_1[no-args]`, `[stale-base]`; usage-to-stdout mutant reds both |
| m5 (`changed-files.sh` exit 2: output first, cause, exit 2, no row) | Satisfied | `test_changed_files_error_is_printed_then_exit_2`; test review's mutants C/D/E red |
| KD-5 (every failure arm tested, mutation red) | Satisfied for slice 1 | RED report mutants plus the test review's A–E plus this run's stdout mutant |

## Positive Observations

- Asserting the exact stdout list in the `changed-files.sh` test pins order,
  content and termination in one assertion. No other exit site can satisfy it.
- The usage test asserts the exit code first, so a failure names the exit code
  rather than an incidental stream difference.
- The helper change kept all 14 existing callers untouched.

## Recommendations

None for this slice.
