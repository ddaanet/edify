# Item 1.1 slice 4 GREEN: unrecognised label is no-classification

## Tests and order

1. `tests/test_triage_feedback.py::test_unrecognised_label_is_no_classification`
   (the only failing test) — failed before; passes after one growth step: a
   branch in the verdict chain, ahead of the Simple branch, that sets
   `unrecognised_label` and leaves the verdict `no-classification` when the
   value is not exactly `Simple`, `Moderate`, `Complex` or `Defect`. Four
   `!=` comparisons in one `[[ ]]`, not an `@(...)` extglob, which bash 3.2
   needs `shopt -s extglob` to parse.
2. Full suite: 390/391 passed, 1 xfail (pre-existing).

The log append already skips `no-classification`, so no row needed no change.

## Placement

`unrecognised classification: <label>` prints after the verdict line, behind
a blank line, ahead of the Triage and WARNING lines. `## Verdict` still
carries the verdict as its first line. Printed only when the label was
unrecognised.

## Out of scope, untouched

The classification parse line (`grep | head | sed | xargs || true`) is
unchanged; the test passes without touching it.

## Gate

- `just lint`: Lint OK
- `just precommit`: `Precommit OK`
- Precommit warnings (not acted on): oversized-file
  `plugin/agents/corrector.md` 682 > 400, `plugin/agents/outline-corrector.md`
  450 > 400, `plugin/agents/design-corrector.md` 460 > 400.
- `tmp/.test-sentinel`: `661560632 636079`
