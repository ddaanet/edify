# Review: Item 1.4 slice 1 — code review (tdd-slice step (d))

**Scope**: the commit adding `plans/review-fixes-2/reports/item-1-4-s1-green.md`,
diffed against its parent. Reviewed: the new
`test_unloadable_exempt_paths_is_an_error_not_no_base` in
`tests/test_changed_files.py`; the `_run_script(script=…)` change in
`tests/changed_files_helpers.py` and every caller; and the load guard in
`plugin/skills/build/scripts/changed-files.sh`, read against the test. The
slice changed no implementation.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The test and the guard agree. The guard's two halves are `! source` and
`-z ${EXEMPT_PATHS_ALTERNATION:-}`, and each one maps onto one of the two
parametrized cases. The ERROR line the test asserts is the one the guard
echoes. Exit 2 is the guard's exit code. The committed item report means a
script that carried on would print `BASE:` and exit 0, so carrying on is
visible to the test. The helper change keeps every existing caller's
behaviour. I found no issues and edited nothing.

**Overall Assessment**: Ready

## Test against guard (three surfaces)

- **What the rule says.** Outline Item 1.4 slice 1 / m23 says: absent, or
  present but defining nothing, gives exit 2, the exact ERROR line, and no
  `NO-BASE:`.
- **What the guard does.** `changed-files.sh` lines 67–71 implement it.
  `script_dir` comes from `BASH_SOURCE[0]`. The copy runs by absolute path,
  so the `*/*` branch picks the tmp `scripts/` directory. The test-review
  report showed this: the absent case's own output names the tmp file.
- **What the test checks.** It asserts all three clauses. The ERROR line is
  matched as a whole line (`in result.stdout.splitlines()`), not as a
  substring. The negative is paired with a positive on the same fixture.
- **Item 1.5 robustness.** Item 1.5 will drop `exec 2>&1`. After that,
  bash's `No such file or directory` goes to stderr, but the guard's
  `echo` stays on stdout. All three assertions keep holding, so the test
  will not need to change when Item 1.5 lands.

## Helper change: callers

`_run_script` in `tests/changed_files_helpers.py` gained a keyword-only
`script: Path = SCRIPT`, placed after `*args`. Callers:

- `tests/test_changed_files.py`: 10 existing calls, all positional. They get
  the default.
- `tests/test_changed_files_phase.py`: all calls positional. They get the
  default.
- The new test is the only caller that passes `script=`.
- `tests/test_verify_step*.py` import a different `_run_script` from
  `tests/verify_step_helpers.py`, which this commit did not touch.

Because `script` is keyword-only, no positional argument can bind to it by
accident. Result: 12/12 tests pass across `test_changed_files.py` and
`test_changed_files_phase.py` against the script as committed.

## Mutated-SUT run

I attempted one mutation run, with a different mutant from the RED and
test-review runs. It was a fail-open guard: `source … || true` followed by
`EXEMPT_PATHS_ALTERNATION=${EXEMPT_PATHS_ALTERNATION:-}`. I applied it to
`changed-files.sh` by exact replacement. The auto-mode classifier then
**denied the pytest command** ("Security Test Removal"), so I have **no
result for this mutant**. I did not retry it in any form.

I restored the script immediately by the inverse replacement, and checked
the restore two ways:

- `grep '|| true'` on the script found no hit.
- `git diff --exit-code -- plugin/skills/build/scripts/changed-files.sh`
  exited 0.

The slice's red evidence therefore rests on the earlier reports:

- RED: the bare-`source` mutant reds both cases on `returncode == 2`.
- Test review, three more mutants, each red on its own assertion:
  - M1 changes the message.
  - M2 adds a `NO-BASE:` line.
  - M3 drops the `-z` half. Only the defines-nothing case reds on M3, as
    intended.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None. No file was changed. The mutation was applied and fully reverted, as
shown above. `just precommit` was not run, because the dispatch requires it
only after a change.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m23, `changed-files.sh` half | Satisfied | `tests/test_changed_files.py` lines 277–312: both doctored states give exit 2, the exact ERROR line, and no `NO-BASE:`. The guard is at `changed-files.sh` lines 67–71. |
| Item 1.4: run a copy beside a doctored `exempt-paths.sh` | Satisfied | `shutil.copy2(SCRIPT, scripts / SCRIPT.name)` (keeps the exec bit), run through `_run_script(..., script=...)`. |
| 400-line cap on test modules | Satisfied | `tests/test_changed_files.py` has 312 lines; `tests/changed_files_helpers.py` has 88. |

The `verify-step.sh` half of m23 belongs to slice 2, which is out of scope.

## Positive Observations

- Parametrizing over the two cases maps one case onto each half of the
  guard, and the readable ids (`absent`, `defines-nothing`) make each half
  addressable as a node id.
- The docstring states the failure mode the test exists to catch: a bare
  `source` exits 1, which is `NO-BASE:`'s code. The RED output confirms it.
- The helper extension adds one keyword argument, not a second run
  function. This avoids duplicating the git-config insulation.

## Recommendations

- **Not a finding (pre-existing, not touched by this commit, and spans
  slice 2's script):** neither guard unsets the variable before sourcing.
  Both guards read `${EXEMPT_PATHS_ALTERNATION:-}`, so a value exported into
  the caller's environment would satisfy the `-z` check when
  `exempt-paths.sh` defines nothing. The script would then run with the
  inherited alternation and not exit 2. The test inherits `os.environ`, so
  this would make the test fail rather than pass falsely. The test is safe,
  but the guard could fail open in such an environment. The fix would be
  `unset EXEMPT_PATHS_ALTERNATION` before the `source` in both
  `changed-files.sh` and `verify-step.sh`, plus a case that pins it. Whether
  that is worth an item is the orchestrator's call; I made no change.
- The fail-open mutant above is still unrun. If my human partner wants that
  evidence, it needs a permission rule for the mutation run, or a manual
  run.
