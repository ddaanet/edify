# Item 2.3 slice 3 — RED report

Both tests pass on the unmutated SUT (13 passed across the two modules).
Each was proved red by a named mutant of `plugin/bin/triage-feedback.sh`.
The SUT is restored: `git diff -- plugin/bin/triage-feedback.sh` is empty.
Uncommitted: `tests/test_triage_feedback_behavioral.py` (222 lines),
`tests/test_triage_feedback_log.py` (254 lines), and this report.

## Tests

- `tests/test_triage_feedback_behavioral.py::test_failing_definition_grep_is_an_error_not_no`
  - Fixture: `a.py` holds `def foo():`, and `classification.md` says
    `Simple`.
  - Shim: a `grep` shim, written with `_write_shim`. On a call carrying
    `-qE` it runs the real `grep "$@"`, prints `shim: fail` to stderr and
    exits 2. Every other call execs the real `grep`.
  - Only the definition grep carries `-qE`. The classification grep takes
    `-E` alone, and `verify-step.sh`'s `grep -vE` is not run by this
    script. The script's `grep` calls were checked with `command grep`.
  - The shim runs the real grep first, so only the status carries the
    failure. The fixture is `Simple` with a `def`, so any mutant that
    swallows or continues past the failure reaches a verdict and logs a
    row.
  - Assertions:
    - `stdout.splitlines() == ["ERROR: grep failed"]`;
    - `"shim: fail"` in stderr, which shows the shim fired on this call;
    - exit 2;
    - no log file.
- `tests/test_triage_feedback_log.py::test_unwritable_log_is_an_error_not_a_usage_exit[directory]`
  - New third parameter. `plans/` is chmod 555 and holds no `reports/`.
  - Assertions:
    - `ERROR: cannot write plans/reports/triage-feedback-log.md` is in
      stdout;
    - for `directory`, that line is also the last stdout line;
    - exit 2.
  - Cleanup restores `plans/` to 755, then `plans/reports` if it exists,
    then the log, all in `finally`. The root skip is unchanged.
  - Module docstring and test docstring updated. The behavioural module
    docstring now says a failing definition grep and a failing diff are
    covered there.

## Mutation proof

Each mutation was applied by exact-string replacement with a count of 1
checked first. It was restored by applying the same replacement with the two
strings swapped. After each restore: a `command grep` for the mutant text
gave 0 hits, `git diff -- plugin/bin/triage-feedback.sh` was 0 bytes, and the
test was green.

### 1. `test_failing_definition_grep_is_an_error_not_no`

Replaced (the behavioural grep's `*)` arm, taken in with the `esac` and the
column-0 `fi` that follow it, which differ from the classification arm):

```
        *)
            echo "ERROR: grep failed"
            exit 2
            ;;
    esac
fi
```

with:

```
        *) ;;
    esac
fi
```

Red on its own assertion, at `test_triage_feedback_behavioral.py:219`
(`assert result.stdout.splitlines() == ["ERROR: grep failed"]`). Grep's
status 2 read as "no", and the run printed the full report and reached
`match`:

```
## Evidence / Files changed: 1 / Reports: 0 / Behavioral code: no /
Review artifact: none / ## Verdict / match / WARNING: No corrector report
...
shim: fail
```

The shim fired (`shim: fail` is on stderr), and the run went on to a verdict
and a row, so the fault is what the test sees.

### 2. `test_unwritable_log_is_an_error_not_a_usage_exit[directory]`

Replaced:

```
    mkdir -p "$log_dir" || {
        echo "ERROR: cannot write $log_file"
        exit 2
    }
```

with `    mkdir -p "$log_dir"`.

Red on its own assertion: `assert 'ERROR: cannot write
plans/reports/triage-feedback-log.md' in '## Evidence … ## Verdict\nmatch\n'`.
The run exited 1, with stderr `mkdir: cannot create directory
'plans/reports': Permission denied`. The mutant redded only the `[directory]`
case. `[header]` and `[row]` still passed (1 failed, 2 passed).

Both named mutants redded on an assertion, so no alternative was needed.

## Controls

An ad hoc run with no fault, using the same fixture as test 1 with no shim,
exits 0 with `Behavioral code: yes`. The verdict is `underclassified`, and a
row `| j | Simple | 1 | 0 | yes | underclassified |` is logged. So the fixture
reaches a verdict and writes a row, and the faulted run's `no row` and
`ERROR` come from the grep failure. The `[directory]` fixture (the
`_commit_reports_fixture` run) without the chmod exits 0 and logs a `match`
row. With the mkdir mutant applied, the faulted run printed its evidence and
verdict, `match`, before failing, which shows that the run reaches the log
step and the `mkdir` is what fails.

## Fixtures tried and rejected

- A shim that exits 2 without running the real `grep`. Rejected: it gives
  slice 2's weaker-guard gap. A guard that tested for emptiness or for the
  output would pass it. The shim runs the real tool first.
- A fixture with no `classification.md`. Rejected: under a swallowed grep
  failure the verdict is `no-classification`, which logs no row, so the
  no-row assertion could not discriminate. The `Simple` fixture reaches a
  row.
- Matching the shim on the pattern argument instead of `-qE`. Rejected: the
  `-qE` flag is the only thing that separates the definition grep from the
  classification grep, whose `-E` the script also passes.
- A mutant for the `directory` case that changes the message instead of
  dropping the guard. Rejected: the named mutant (guard dropped, exit 1)
  reds an assertion, so the stronger one was not needed.

## Gate

`ruff check`, `ruff format --check` and `docformatter -c` pass on both test
modules. The scratch helper was deleted from `tmp/`.
