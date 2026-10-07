# Review: Item 2.3 slice 2 — test review

**Scope**: uncommitted changes in `tests/test_triage_feedback_failures.py`
(the `_underclassified_repo` helper and two tests), plus the RED report
`item-2-3-s2-red.md`. The SUT `plugin/bin/triage-feedback.sh` was out of
scope except for in-place mutation runs, each one restored.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

Both tests carry a mutation proof. I reproduced each one with a different
mutation of my own, and each reds on its own assertion. The sed test had a
wrong-reason gap: its shim printed nothing, so a guard that tested the
captured label for emptiness, not sed's status, also passed it. That is fixed
by having the shim print the real tool's output and then exit 4. Both stdout
assertions are now exact-equality, and the grep test now ties its error to the
classification grep.

**Overall Assessment**: Ready

## Mechanical first check — mutation proofs reproduced

The run uses uid 1000, so the mode-000 test ran and was not skipped. Each
mutation was an exact-string replacement, with a count of 1 checked before it
was applied. Each was restored by applying the same replacement with the two
strings swapped. After each restore, `command grep -c <mutant text>` returned
0 and `git diff -- plugin/bin/triage-feedback.sh` was 0 bytes.

- **A, for `test_unreadable_classification_is_an_error`.** The RED report's
  mutant swallowed the `*)` arm. This one widens the no-match arm instead,
  changing `            ;;\n        1) ;;` to `            ;;\n        1|2) ;;`.
  The leading `;;` line belongs only to the classification case, because the
  behavioural case's `1) ;;` follows `0) behavioral_code="yes" ;;`. Grep's
  status 2 then reads as "no Classification line".
  - Result: red at `test_triage_feedback_failures.py:228`, on the stdout
    assertion. The run printed `## Evidence … Behavioral code: yes …
    no-classification` and exited 0.
  - `Behavioral code: yes` also shows that the behavioural grep did not fail
    in this fixture.
- **B, for `test_failing_label_sed_is_an_error`.** The RED report's mutant
  dropped the guard. This one keeps the guard but swallows sed's status
  inside the substitution, changing `s/[[:space:]]+\$//"); then` to
  `s/[[:space:]]+\$//" || true); then`.
  - Result: red at `:271`, on the stdout assertion.
  - After the shim fix, the run reaches `underclassified` and its row-logging
    branch, with `Triage: predicted Simple …`.
- **C (extra), for `test_failing_label_sed_is_an_error`.** An emptiness
  guard, changing `s/[[:space:]]+\$//"); then` to
  `s/[[:space:]]+\$//" || true); [[ -z $classification ]]; then`.
  - Result: red at `:271`, on the stdout assertion, reaching
    `underclassified`.
  - Against the pre-fix shim, which printed nothing, this mutant leaves the
    label empty, so the guard prints `ERROR: sed failed` and exits 2. Every
    pre-fix assertion would have held. I reasoned this from the code path; I
    did not run it against the old shim.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The sed test cannot tell a status guard from an emptiness guard**
   - Location: `tests/test_triage_feedback_failures.py`, the
     `test_failing_label_sed_is_an_error` shim.
   - Problem: the shim exited 4 without printing anything. Under any mutant
     that loses sed's status, `classification` stays empty and the run ends
     at `no-classification`: exit 0 and no row. A guard that tests
     `[[ -z $classification ]]` instead of the pipeline status prints the
     same `ERROR: sed failed` and exits 2, so the test passed against a wrong
     implementation (mutant C). This also meant the no-row and `## Evidence`
     assertions could not discriminate, as the RED report itself noted.
   - Fix: on the matching call, the shim now runs the real `sed` (the
     `shlex.quote`d path) and then exits 4. The label `Simple` is printed and
     only the status carries the failure. A mutant that loses the status now
     reaches `underclassified` and logs a row, so exit 2, the stdout line and
     no-row all discriminate. The docstring names that state of the world.
   - **Status**: FIXED

### Minor Issues

1. **Stdout pinned by membership, not equality**
   - Location: both tests, `"ERROR: … failed" in lines` plus a
     `## Evidence` negative.
   - Note: nothing writes to stdout before either arm, and the clean faulted
     run prints exactly one line. A mutant that printed the `ERROR:` line but
     did not exit would still be caught by the `## Evidence` negative, but
     extra output of any other kind would not be. Equality pins the interface
     (`ERROR: <cause>` on stdout) and includes the negative. This matches
     slice 1's `test_changed_files_error_is_printed_then_exit_2`.
   - **Status**: FIXED. Both tests now assert
     `result.stdout.splitlines() == ["ERROR: … failed"]`, and the separate
     `## Evidence` negatives are gone.
2. **Nothing in the grep test ties `ERROR: grep failed` to the
   classification grep**
   - Location: `test_unreadable_classification_is_an_error`.
   - Note: the behavioural grep's `*)` arm prints the identical line. In this
     fixture it does not fail (mutant A shows `Behavioral code: yes`), but
     nothing in the test said which grep the line came from.
   - **Status**: FIXED. The test adds
     `assert "classification.md" in result.stderr`: grep's own diagnostic
     names the file. The behavioural grep reads a pipe and cannot name it.
     The assertion does not check the `Permission denied` wording, which may
     differ on BSD/macOS. The docstring states the reason.

## Wrong-reason hunting — answers to the dispatch's questions

- **Is "no row" discriminating?**
  - The grep test: no, and it cannot be. At mode 000 grep yields no label,
    so every way of swallowing the error ends at `no-classification`, which
    logs no row. The assertion stays as an interface pin. Exit 2 and the
    exact stdout are what discriminate.
  - The sed test: yes, now. After the shim fix, mutants B and C reach
    `underclassified`, which appends a row.
- **Could `ERROR: grep failed` come from the behavioural arm?** Not in this
  fixture. The behavioural grep reads `git diff` output between commits,
  which the file mode does not affect, and mutant A's output shows it
  succeeded. The stderr assertion now pins the attribution in the test.
- **Root skip and mode restore**: `skipif(os.geteuid() == 0)` is present, and
  `chmod(0o644)` runs in `finally` before `tmp_path` cleanup. No finding.
- **The sed shim's pass-through**: the `shlex.quote`d real-tool path is now
  exercised in-band. Under mutants B and C the label `Simple` reached the
  verdict, so the embedded real `sed` ran. The `exec` branch for non-matching
  calls has no caller: `triage-feedback.sh` has one `sed`, and
  `plugin/skills/build/scripts/changed-files.sh` has none (checked with
  `command grep -n '\bsed\b'`). That branch is unexercised by construction.
  It only matters if a second `sed` call is added. I accept this as a stated
  residual, not a defect.

## Fixes Applied

- `tests/test_triage_feedback_failures.py`, unreadable-classification test:
  - stdout is now exact equality `["ERROR: grep failed"]`;
  - a new assertion requires `classification.md` in stderr;
  - the docstring gains a sentence on why the stderr assertion is there.
- `tests/test_triage_feedback_failures.py`, failing-sed test:
  - the shim's matching arm runs `{quoted_sed} "$@"`, then prints
    `shim: fail` and exits 4;
  - `quoted_sed` is bound once and used in both arms;
  - stdout is now exact equality `["ERROR: sed failed"]`;
  - the docstring is rewritten to name the status-versus-output state of the
    world.
- No helper or SUT change. The module is 273 lines. Docstring summaries are
  unchanged, and none was shortened.

## Final run

- `.venv/bin/pytest -p no:markdown_report tests/test_triage_feedback_failures.py -v`:
  8 passed. Both slice tests passed on the unmutated SUT and red under
  mutants A, B and C.
- `ruff check`: all checks passed. `ruff format --check`: already formatted.
- `uv run --frozen docformatter -c`: rc 0.
- `git diff -- plugin/bin/triage-feedback.sh`: 0 bytes.
- The scratch mutation helper `tmp/s2-test-review-mut.py` has been deleted.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Interfaces: exit 2, `ERROR: <cause>` on stdout, no row, unreadable `classification.md` | Satisfied | `test_unreadable_classification_is_an_error` |
| Interfaces: the same, for a failing sed | Satisfied | `test_failing_label_sed_is_an_error` |
| Slice notes: shim passes other calls through, `shlex.quote`, root skip, mode restore | Satisfied | see the answers above |

## Positive Observations

- The mode-000 test's `try/finally` restore and its root skip follow the
  existing `test_unreadable_log_is_an_error_and_appends_nothing` pattern.
- The RED report recorded its own non-discriminating assertions and a control
  run instead of claiming coverage. That is what pointed this review at the
  sed shim.
- The RED report's mutation for the identical `grep failed` arms took in a
  context line that differs between the two arms, as the item notes require.
