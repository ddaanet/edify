# Item 2.3 slice 2 — RED report

Tests added to `tests/test_triage_feedback_failures.py` (now 267 lines; module
docstring updated to name the two cases). A helper `_underclassified_repo`
builds the shared fixture: a run commit holding a `def` under a `Simple`
classification. Both tests pass against the unchanged SUT, as the behaviour
exists. No SUT edit remains: `git diff -- plugin/bin/triage-feedback.sh` is
0 bytes. ruff check/format and `docformatter -c` pass.

## Tests

- `test_unreadable_classification_is_an_error`: `classification.md` at mode
  000 (skipped as root; mode restored in `finally`). Asserts
  `ERROR: grep failed` as a stdout line, no `## Evidence` line, exit 2, no log
  file.
- `test_failing_label_sed_is_an_error`: a `sed` shim, the real path embedded
  with `shlex.quote`. It exits 4 when any argument contains `Classification`
  and `exec`s the real `sed` otherwise. `triage-feedback.sh` runs `sed` once
  (line 180; `changed-files.sh` runs none: `command grep -n '\bsed\b'` found
  only that site), so the failure is the guarded one. Asserts
  `ERROR: sed failed` as a stdout line, no `## Evidence` line, exit 2, no log
  file.

Final run: `tests/test_triage_feedback_failures.py` 8 passed.

## Mutation proof

Mutations applied by exact string replacement in `plugin/bin/triage-feedback.sh`
(count checked to be 1 before each), restored by the swapped replacement.

### `test_unreadable_classification_is_an_error`

Replaced (the trailing context, `esac` then `if [[ -z "$classification" ]]`,
exists only after the classification arm; the behavioural arm is followed by
`fi`):

```
        *)
            echo "ERROR: grep failed"
            exit 2
            ;;
    esac

    if [[ -z "$classification" ]]; then
```

with

```
        *) ;;
    esac

    if [[ -z "$classification" ]]; then
```

So the `*)` arm no longer exits on a grep status of 2 or more. Red on its own
assertion:

```
tests/test_triage_feedback_failures.py:227: in test_unreadable_classification_is_an_error
    assert "ERROR: grep failed" in lines, output
E   AssertionError: ## Evidence
E     - Files changed: 1 ... - Behavioral code: yes ...
E     ## Verdict
E     no-classification
E     grep: plans/j/classification.md: Permission denied
E   assert 'ERROR: grep failed' in ['## Evidence', ...]
1 failed
```

Restore: swapped replacement applied; `command grep -c '^        \*) ;;$'` = 0;
`git diff` 0 bytes; test green (1 passed).

Discrimination: under this mutant the run ends at `no-classification`, which
logs no row. So the "no row" assertion does not discriminate for this mutant;
the `ERROR:` line, the `## Evidence` negative and exit 2 do (the mutant prints
an evidence report and exits 0). The no-row assertion is a pin of the
interface only.

### `test_failing_label_sed_is_an_error`

Replaced the guard (unique; `command grep -c 'if ! classification=\$(printf'`
was 1):

```
            if ! classification=$(printf '%s\n' "${label_lines%%$'\n'*}" |
                sed -E "s/${label_prefix_re}[[:space:]]*//;s/[[:space:]]+\$//"); then
                echo "ERROR: sed failed"
                exit 2
            fi
```

with the bare assignment

```
            classification=$(printf '%s\n' "${label_lines%%$'\n'*}" |
                sed -E "s/${label_prefix_re}[[:space:]]*//;s/[[:space:]]+\$//")
```

Red on its own assertion (under `set -e` the run dies at the shim's exit 4
with no stdout):

```
tests/test_triage_feedback_failures.py:264: in test_failing_label_sed_is_an_error
    assert "ERROR: sed failed" in lines, output
E   AssertionError: shim: fail
E   assert 'ERROR: sed failed' in []
1 failed
```

Restore: swapped replacement applied; `command grep -c 'if ! classification='`
= 1 (the original line is back); `git diff` 0 bytes; full module 8 passed.
(`classification=$(printf` also counts 1, as a substring of the restored
line.) The mutant run also reaches no verdict, so "no row" and "no
`## Evidence`" are not what discriminate here; the `ERROR:` line and exit
code are.

## Controls

Control run through `_underclassified_repo`, mode 644, no shim:

```
rc 0
## Evidence ... - Behavioral code: yes
## Verdict
underclassified
row: | 2026-10-07 | j | Simple | 1 | 0 | yes | underclassified |
```

So the fault-free fixture reaches a verdict and logs a row; the two tests'
`## Evidence` and no-log-file assertions are the ones the fault changes. The
sed shim's pass-through was exercised by every other call in the run
(`changed-files.sh` and git calls do not use `sed`; the shim only sees the one
label call). Not separately probed: the shim's `exec` branch has no call to
take in this fixture, so it is unproven beyond its construction.

## Fixtures tried and rejected

- A `sed` shim failing every call: rejected for the argument match, so a
  later `sed` added elsewhere would not be hit blindly; as the script has one
  `sed` call today, the two forms behave the same here.
- A mutant leaving `*)` but changing `exit 2` to `exit 1` for the grep test:
  not run; the named mutant (arm swallowed) was sufficient and reds on its
  assertion.
- Running the control and the faulted run in one repo: rejected, since the
  log's row dedupe would skip the second append and make "no row" meaningless.
