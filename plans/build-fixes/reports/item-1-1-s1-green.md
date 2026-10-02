# Item 1.1 / Slice 1 — GREEN

The SUT (`plugin/skills/build/scripts/verify-step.sh`) already implements the
behaviour this slice's test pins (RED's red came from a mutant copy, never from
editing or reverting the tracked script per the item text). No implementation
change was made: `verify-step.sh` carries no diff for this slice.

## Tests run, in order

1. `pytest tests/test_verify_step.py::test_exempt_paths_clean_in_any_porcelain_state -v`
   → **1/1 passed**, against the unmodified `verify-step.sh`, confirming the
   single test this slice contributes passes with no code growth.
2. `pytest tests/test_verify_step.py -v` (full module)
   → **7/7 passed** (the six pre-existing tests plus the new one).
3. `just test` (full suite, `PATH=.venv/bin:$PATH`)
   → **368/369 passed, 1 xfail**, `✓ Tests OK`.

No implementation step was needed beyond test 1, so there is no "one test at a
time, growing the implementation" sequence for this slice — the batch already
passes against the current SUT.

## Pre-existing, out-of-scope lint note

`just lint` fails on `tests/line_limits_helpers.py:32:30: RUF100 Unused `noqa`
directive (non-enabled: `PLR0913`)`. This is unrelated to this slice:
`tests/line_limits_helpers.py` is untouched by this diff (only
`tests/test_verify_step.py` is modified), and the test-review report already
flagged this exact failure under "Observed outside scope" as pre-existing and
not fixed.

The failure is structural, not a regression: `just lint` (`run-lint-checks` in
`justfile`) runs `ruff check -q --ignore=$ruff_ignores`, and `$ruff_ignores`
includes `PLR0913` — with that rule disabled, the file's
`# noqa: PLR0913` reads as unused (RUF100). `just precommit`
(`run-checks` in `justfile`, overriding `plugin/portable.just`'s stub) runs
plain `ruff check -q` with no ignore list, so `PLR0913` stays active there and
the same `noqa` is legitimately used — confirmed by `just precommit` passing
clean below. `just check` (the recipe precommit calls into) is the gate; `just
lint`'s complexity-rule exclusion is a narrower, stricter-looking but
differently-configured check that false-positives on this pre-existing
directive. Not fixed here: the file is untouched by this slice and editing a
test file is prohibited in GREEN mode regardless.

## Gate verdict

`just precommit` (`PATH=.venv/bin:$PATH`, `dangerouslyDisableSandbox: true`):

```
# version consistency
Version consistent: 0.3.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Recap line: `✓ Precommit OK`.

`tmp/.test-sentinel` hash: `849977611 568258`.

The three `oversized-file` warnings (`corrector.md`, `outline-corrector.md`,
`design-corrector.md`) are pre-existing and out of this slice's scope (none of
the three is touched by this diff); recorded per the gate-warnings-go-in-the-
report rule, not acted on.

## Scope discipline

No implementation code touched (`verify-step.sh` carries no diff). No test
file edited in this dispatch. `tests/test_verify_step.py` is 373 lines, under
the 400-line hard cap.
