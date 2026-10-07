# Item 2.3 slice 1 — RED (mutation proof)

Files (uncommitted): `tests/test_triage_feedback_failures.py` (195 lines),
`tests/triage_feedback_helpers.py` (193 lines; `_run_triage` gained
`extra_args: tuple[str, ...] = ()`, appended after the job argument). The
failures module docstring now names the usage error and the `changed-files.sh`
failure. `ruff check` and `ruff format --check` pass. The SUT has no lasting
edit: `git diff -- plugin/bin/triage-feedback.sh` is empty.

All three cases pass against the unmodified SUT (6 passed in the module); the
behaviour exists, so each is proven by a named mutant, one at a time.

## Control

`stale-base` fixture (item report committed with `module.py` holding a `def`
and `classification.md` = Simple), run as `j` alone: exit 0 and the log gains
`| 2026-10-07 | j | Simple | 1 | 0 | yes | underclassified |`. So `j HEAD`
reaching a verdict is a real failure of the guard, not a fixture that logs
nothing anyway.

## Mutation proof

Each exact string occurs once in the file (replacement script asserts
`count == 1`).

1. `test_usage_error_exits_1[no-args]` — replace
   `[[ -z "$job_dir" ]] || [[ $# -gt 1 ]]` with `[[ $# -gt 1 ]]`.
   Red on its assertion: `assert 2 == 1` (returncode; stdout
   `ERROR: usage: changed-files.sh <job> [--phase]; not a job name:` then
   `ERROR: changed-files.sh exited 2`). `[stale-base]` stays green under this
   mutant. Restored by swapping `if [[ $# -gt 1 ]]; then` back to
   `if [[ -z "$job_dir" ]] || [[ $# -gt 1 ]]; then`; `command grep -c` of
   `if [[ $# -gt 1 ]]; then` = 0; `git diff` empty; both cases green.

2. `test_usage_error_exits_1[stale-base]` — replace
   ` || [[ $# -gt 1 ]]; then` with `; then`. Red on its assertion: the
   returncode assert fails (exit 0) with stdout the full `## Evidence` ...
   `underclassified` verdict report; the log row is written. `[no-args]`
   stays green. Restored by swapping the strings back
   (the first attempt at the restore used context
   `"$job_dir" ]]; then\n    echo "Usage` -> `... ]] || [[ $# -gt 1 ]]; then\n    echo "Usage`);
   grep of the mutated line = 0 hits; `git diff` empty; both cases green.

3. `test_changed_files_error_is_printed_then_exit_2` — replace
   `"$job_dir") || status=$?\nif [[ $status -ne 0 ]]; then` with the same text
   but `[[ $status -eq 1 ]]` (the context line takes in the `changed-files.sh`
   call, so it is not the `rev-parse` guard's identical line). Red on its
   assertion: `assert 'ERROR: git log failed' in ['ERROR: git diff failed']`
   — the run falls through with exit 2's output read as a base (`fatal: bad
   revision 'ERROR: git log failed'`). Restored by swapping back;
   `command grep -c 'status -eq 1'` = 0; `git diff` empty; test green.

After the last restore: module 6 passed; `git status` shows only the two test
files modified plus the untracked inbox briefs.

## Per-test output

- `test_usage_error_exits_1[no-args]`: green on SUT; red under mutant 1
  (`assert 2 == 1`).
- `test_usage_error_exits_1[stale-base]`: green on SUT; red under mutant 2
  (returncode 0, verdict report on stdout).
- `test_changed_files_error_is_printed_then_exit_2`: green on SUT; red under
  mutant 3 (`'ERROR: git log failed' in ['ERROR: git diff failed']`).

The test asserts returncode first so the `no-args` and `stale-base` reds name
the exit code the slice cites, not an incidental stderr difference.

## Fixtures tried and rejected

- `stale-base` with a fixture that logs nothing (no `def`, no reports): rejected,
  since the mutant's run would then exit 0 with `no-classification` or a
  `match` row-less report and the guard's absence would be less visible; the
  chosen fixture logs a row under `j` alone (control above).
- `no-args` run through `_run_triage(JOB, ...)` with an empty job string:
  rejected; `_run_triage` always passes the job, and `""` would test the same
  `-z` clause only via a different argv (one argument, empty). `no-args` calls
  the script with no argv at all, as the slice says.
- Mutant 1 as the dispatch states it reds with exit 2 (as predicted), so no
  alternative was needed. Mutant 3's mutation string alone
  (`[[ $status -ne 0 ]]`) is not unique, hence the context line.
- An unborn repo with `classification.md` untracked: fine (no commit needed);
  a repo with a seed commit was rejected because `changed-files.sh` then
  reaches `NO-BASE:` (exit 1), not the `git log` failure.
