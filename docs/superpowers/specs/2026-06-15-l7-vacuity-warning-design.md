# L7 Vacuity Warning for `edify check` — Design

**Date:** 2026-06-15
**Status:** Approved design, pre-implementation
**Living-design link:** Hardens L7 in `../design/invariant-guided-verify-loop.md`

## 1. Context

L7 (living design): when `--timeout` is omitted, `edify check` passes no
`--per_condition_timeout` to CrossHair, so CrossHair uses its own unspecified
internal default. On a target whose interesting paths need specific synthesized
input (D10: two matching backticks), that default may never reach them —
CrossHair returns `verified` while the contract holds only emptily. D10
demonstrated this concretely: a contract-violating off-by-one passed `verified`
at the default budget and was refuted only at `--timeout 30`.

The lesson, stated honestly: **a `verified` is only as strong as the budget that
produced it.** This design encodes that lesson into the tool's output.

## 2. Decision: surface, don't fix or detect

Three mechanisms were considered (handoff open decision, 2026-06-15):

- **Inject an explicit default floor** — rejected. Any fixed value is
  ungrounded; D10 established only that 30s flipped *one* target, not that 30
  (or any number) is a sound universal floor. Baking one in violates the
  project's no-confabulation rule (ungrounded operational threshold).
- **Auto-probe vacuity guard** — rejected for the CLI. Detecting non-exploration
  has no native CrossHair signal (D4: no distinct unknown exit code), so it would
  require an automatic second pass / falsification probe. That doubles run cost
  and belongs in the `formalize` discipline, not the `check` primitive.
- **Surface + warn, no number** — chosen. Make the budget visible on every
  `verified` result and warn when the budget was CrossHair's unspecified default.
  No invented number, no second run.

## 3. Behavior

Scope is **verified-only.** The warning attaches only to `VERIFIED`. `REFUTED`
(a counterexample was found) and `ERROR` are never vacuous and are untouched.
Exit codes are unchanged (0 verified / 1 refuted / 2 error).

| Case | Human output (stdout) | Warning (stderr) |
|------|-----------------------|------------------|
| `verified`, `--timeout=N` given | `verified: TARGET (no counterexample within N s per-condition budget)` | none |
| `verified`, no `--timeout` | `verified: TARGET (no counterexample within CrossHair's default budget)` | a vacuity warning (see below) |
| `refuted` / `error` | unchanged | unchanged |

**Vacuity warning text (stderr, verified-without-timeout only):** states that the
verdict used CrossHair's unspecified internal default budget and may be vacuous —
the contract's interesting paths may never have been synthesized — and that
re-running with `--timeout` hardens it. The warning does **not** assert any
specific default value (we don't know CrossHair's internal default; asserting it
would be confabulation).

Warnings go to **stderr** so stdout stays the clean, composable result.

## 4. JSON output

Two fields are added to the existing `{status, target, findings, detail}` object:

- `"budget"`: the `--timeout` value as passed (float), or `null` when omitted.
- `"vacuity_warning"`: boolean — `true` only for `verified`-without-`--timeout`,
  `false` otherwise.

This lets the `formalize` loop and a future D8 eval harness read the vacuity flag
programmatically rather than scraping stderr. (Extends FR5.)

## 5. Where the logic lives

- `check.py` (`CheckResult`, `parse_crosshair_output`, `build_crosshair_argv`) —
  **unchanged.** It owns the exit-code→status parse contract (CrossHair-verified,
  D9) and does not know the budget. Keeping it untouched preserves NFR1 (pure
  core) and NFR2 (backend-agnostic result shape).
- `check_cli.py` (`handle_check`, `_print_human`) — **changed.** Both already
  receive `per_condition_timeout`. The budget-reporting line, the stderr warning,
  and the two new JSON fields are derived here from
  `(result.status is VERIFIED, per_condition_timeout is None)`.

## 6. Testing (TDD, per NFR3)

Unit tests in `tests/test_cli_check.py` against the existing fixture pattern:

- verified + no timeout → stderr contains the vacuity warning; JSON
  `vacuity_warning == true`, `budget == null`.
- verified + `--timeout=N` → no stderr warning; human line reports `N s`; JSON
  `vacuity_warning == false`, `budget == N`.
- refuted + no timeout → no vacuity warning (verified-only scope); JSON
  `vacuity_warning == false`.
- error → unchanged; JSON `vacuity_warning == false`.

Exit-code tests (FR4) must continue to pass unchanged.

## 7. Out of scope (explicit)

- No minimum-budget floor / injected default number (rejected, §2).
- No auto-probe / second-pass vacuity detection (rejected, §2; lives in
  `formalize`).
- No change to `parse_crosshair_output` or `build_crosshair_argv`.
- This does not close L5 (catch-rate vs the one-shot baseline) — that still needs
  the D8 eval harness. It hardens L7 only.

## 8. Living-design updates (on implementation)

- New FR: "`edify check` reports the budget on a `verified` result and warns
  (stderr + JSON `vacuity_warning`) when the verdict used CrossHair's default
  budget."
- FR5 amended: JSON includes `budget` and `vacuity_warning`.
- L7 disposition updated from "deferred" to resolved-by-surfacing (the warning
  ships; a floor/auto-probe remains a deliberate non-goal).
