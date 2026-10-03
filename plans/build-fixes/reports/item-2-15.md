# Item 2.15 — `just lint` agrees with `precommit` on PLR0913

Requirements: my human partner's leg-2 ruling (`build-leg2.md`, answer 2).
Executed in session by the leg-3 orchestrator; self-reviewed.

## Changes

- `plugin/portable.just` `run-lint-checks`: `PLR0913` removed from
  `ruff_ignores`. The rest of the list is unchanged. RUF100 stays enabled.
- `justfile` `run-lint-checks`: the same removal. **Deviation from the ruling's
  literal scope**, which named `plugin/portable.just` only. `justfile`
  imports `portable.just` but its prolog redefines `run-lint-checks`, and that
  copy wins. Measured: with only `portable.just` edited, `just lint` still
  failed with `tests/line_limits_helpers.py:32:30: RUF100 [*] Unused noqa
  directive (non-enabled: PLR0913)`. With both copies edited, it passes.
- `plans/build-fixes/outline.md`: Item 2.15 added after Item 2.14, and Scope IN
  gains `plugin/portable.just` and `justfile`.

## The stop condition

PLR0913 was checked for hits it might newly surface: `ruff check -q --select
PLR0913 src tests` exited 0, and `just lint` came back `Lint OK`. No
suppression was added.

## Verification

- `just lint`: `Lint OK` (it was failing at the baseline and at HEAD before
  this item).
- `just format` then `just precommit`: `Precommit OK`. Its output names three
  `oversized-file` lines for the allowlisted `*-corrector.md` agents, and
  design-links reports 87 decisions and 8 nodes.

## Judgement calls for review

- Two copies of `run-lint-checks` remain, one in each file. Removing the
  `justfile` duplicate falls outside this item. The `justfile` comment at its
  `fail ()` definition already notes that the prolog overrides `portable.just`
  on import.
