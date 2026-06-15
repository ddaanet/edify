# Invariant-Guided Verify Loop — Living Design

**Status:** Living. Updated as the design evolves; supersedes the frozen spec
where they diverge.
**Verified against:** `7396bb3` (2026-06-15). FR/NFR states below were true at
this commit — `git diff 7396bb3 -- src/edify tests` to find drift.

**Origin artifacts (frozen):**
- Spec: `../specs/2026-06-08-invariant-guided-verify-loop-design.md`
- Plan: `../plans/2026-06-08-edify-check-verify-loop.md` (executed)

**Thesis (the idea being proven):** the LLM guesses properties (its strength);
an external verifier catches what it cannot deduce (its weakness). The verify
loop is the mechanism. Whether the loop is *worth building over one-shot* is the
open claim — see L5, L6.

## Now

- **Focus:** thesis unproven (L5/L6); the loop works as designed on the seed.
- **Next:** choose the proof path — run `formalize` on a *real* function
  (qualitative, in-session, free) **or** stand up the eval harness (D8,
  quantitative, plan credits). Pending decision, not blocked.
- **Do not:** re-litigate the backend (D1) or the four-state→three-state output
  (D4) — both settled. Check each decision's *Reopen-if* before reviving it.

**Status legend.** FR/NFR: `Done` = implemented + pinned by a test;
`Done (prose)` = implemented as skill instructions, not code/tested;
`Partial` = some of it; `Planned` = not built.

---

## Functional Requirements

| # | Requirement | State | Where · pinned by |
|---|-------------|-------|-------------------|
| FR1 | `edify check <target>` invokes CrossHair on a file path or dotted `module.func` and returns a structured verdict. | Done | `cli.py:check` → `check_cli.py:handle_check` · `test_cli_check.py::test_check_command_invokes_handler` |
| FR2 | Status is `verified`/`refuted`/`error`, derived from CrossHair exit 0/1/2. | Done | `check.py:parse_crosshair_output` · `test_check_parse.py::test_exit_zero_is_verified`, `::test_exit_two_is_error_with_detail` |
| FR3 | A `refuted` result parses each `file:line: error: message` line into a `Finding(location, message)`. | Done | `check.py:parse_crosshair_output` · `test_check_parse.py::test_exit_one_parses_findings`, `::test_findings_ignore_non_error_lines` |
| FR4 | Process exit codes mirror status (0/1/2) so the command composes in recipes and a future eval. | Done | `check_cli.py:_EXIT_CODES`, `handle_check` · `test_cli_check.py::test_handle_check_verified_exits_zero`, `::test_handle_check_refuted_exits_one_json`, `::test_handle_check_error_exits_two` |
| FR5 | `--json` emits `{status, target, findings, detail}`; default is human-readable. | Done | `check_cli.py:handle_check`, `_print_human` · `test_cli_check.py::test_handle_check_refuted_exits_one_json` |
| FR6 | `--timeout` sets CrossHair `--per_condition_timeout`. | Done | `check.py:build_crosshair_argv` · `test_check_argv.py::test_argv_with_timeout` |
| FR7 | A missing CrossHair executable raises an actionable `CrossHairUnavailableError`, never a silent failure. | Done | `check_cli.py:run_crosshair`, `exceptions.py:CrossHairUnavailableError` · `test_cli_check.py::test_run_crosshair_missing_binary` |
| FR8 | `formalize` drives a propose-contract → check → repair loop with the in-context agent holding intent. | Done (prose) | `plugin/skills/formalize/SKILL.md` |
| FR9 | `formalize` uses `AskUserQuestion` on genuine intent ambiguity, never inventing a spec. | Done (prose) | `plugin/skills/formalize/SKILL.md` |
| FR10 | `formalize` triages every counterexample: code bug → fix code, spec bug → fix contract, intent ambiguity → ask. | Done (prose) | `plugin/skills/formalize/SKILL.md` |
| FR11 | `formalize` caps repair iterations; on the cap it reports the honest unresolved state, never upgrading `refuted`/`error` to verified. | Done (prose) | `plugin/skills/formalize/SKILL.md` |

## Non-Functional Requirements

| # | Requirement | State | Where · pinned by |
|---|-------------|-------|-------------------|
| NFR1 | Pure core / thin shell: `check.py` does parsing + argv with no I/O; `check_cli.py` owns subprocess, formatting, exit codes. | Done | `check.py` (no imports of subprocess/sys) vs `check_cli.py` |
| NFR2 | Result shape is backend-agnostic so a later Nagini swap is local to `check_cli.py`. | Done | `check.py:CheckResult`, `CheckStatus`, `Finding` |
| NFR3 | TDD; CLI unit-tested against fixtures with known verdicts, plus a no-mock end-to-end test on the seed. | Done | `tests/test_check_e2e.py`, `tests/fixtures/check_targets/` |
| NFR4 | No "verified" claim without a `verified` result from `edify check`. | Done (prose) | `plugin/skills/formalize/SKILL.md` |
| NFR5 | Honest guarantee level: bounded path-exploration, not soundness/termination. | Done (prose) | `plugin/skills/formalize/SKILL.md` |
| NFR6 | Python 3.14, ruff ALL, mypy strict, docformatter; `just precommit` green. | Done | `just precommit` |

## Decisions

| # | Decision | Rationale | Supersedes / Reopen-if |
|---|----------|-----------|------------------------|
| D1 | Backend = CrossHair, not Nagini or Lean. | Concrete counterexamples are CrossHair's core output and the signal the loop feeds on; pure Python, no JVM. Nagini's counterexample output is experimental and piles annotation burden where LLMs are weakest. Lean verifies Lean, not Python. | **Reopen if:** Nagini's counterexample flag leaves experimental, or a Python-native static prover with reliable counterexamples appears. |
| D2 | Contract style = icontract `@require`/`@ensure`. | Clean pre/post seam, maps to Requires/Ensures, first-class CrossHair support. Plain `assert` is the zero-dep fallback, unused in v0. | **Reopen if:** a target class needs contracts icontract can't express. |
| D3 | Command shape = positional `TARGET`. | CrossHair already accepts a file path or dotted `module.func` directly. | Supersedes spec §3 (`<file> --target`). |
| D4 | `unknown` is folded into `verified`. | CrossHair has no distinct exit code for "couldn't decide"; a timeout returns 0 — exactly the honest definition of verified (no counterexample within budget). | Supersedes spec §3 four-state output. **Reopen if:** CrossHair exposes a distinct unknown/timeout signal. |
| D5 | Seed = integer `head(xs)`, not `average(xs)`. | Floats make `average` a flaky verifier target (CrossHair tries `nan`/`inf`/float-rounding), breaking the "fixed verifies" claim. `head` is deterministic and still exercises the spec-refinement branch (fix = add `@require len(xs) > 0`). | Supersedes spec §5. |
| D6 | Agent locus = in-context, not an isolated API loop. | Intent lives in project context and sometimes needs *asking*; an isolated agent can converge on a verified answer to the wrong question. | **Reopen if:** the eval harness needs an isolated runner — keep validation in-context regardless. |
| D7 | `build_crosshair_argv` must NOT pass `--report_verbose`. | Discovered at implementation: `--report_verbose` emits a full traceback, not the parseable `file:line: error:` line. | Supersedes spec §3 (which assumed `--report_verbose`). |
| D8 | Eval harness deferred. | Not the primary v0 artifact; a hand-rolled API-key harness is pay-per-token and ToS-disallowed on a subscription. | **Reopen if:** on Agent-SDK / `claude -p` plan credits — this is the path to prove L5/L6. |

## Limitations (inherent — can't, not won't)

| # | Limitation | Disposition |
|---|------------|-------------|
| L1 | No-contract / vacuous-`verified` detection is not enforced by the CLI; a target with no pre/post-condition is analyzed by nothing. | Deferred to `formalize` discipline (add a contract on `error`). Could move into the CLI later. |
| L2 | `unknown` (timeout / unsupported construct) is indistinguishable from `verified` at the CLI boundary. | Accepted per D4; honest because both mean "no counterexample within budget." |
| L4 | Bounded path-exploration — no soundness or termination guarantee. | Inherent to CrossHair; stated honestly per NFR5. |
| L5 | **The repair loop's advantage over one-shot is unproven.** The spec stakes the loop on closing the paper's ~35–39% one-shot bug-reveal rate; no eval has run. | Open. Needs the D8 eval harness to measure. |
| L6 | **Human-in-loop > isolated is unproven.** The validation-vs-verification claim has no measurement. | Open. |

## Non-goals (deliberate — won't, for now)

| # | Non-goal | Note |
|---|----------|------|
| N1 | Module / multi-function verification. | Single function first (was L3). Revisit after the loop is proven. |
| N2 | Autonomous Agent-SDK eval harness as a shipped feature. | Deferred per D8; it's a measurement tool, not the primary artifact. |
| N3 | Nagini backend. | Later, stronger backend; result shape kept backend-agnostic per NFR2. |
| N4 | Touching the old `requirements` skill / pipeline redesign. | Intent-capture now lives inside this loop; the rebuild thread is superseded, not pursued. |

## History (design-significant changes only)

| Date | Event |
|------|-------|
| 2026-06-08 | Spec approved (CrossHair over Nagini/Lean; two differentiators: repair loop + human-in-loop validation). Prior-art honesty: generate-verify-repair is published research, not novel; the unfilled niche is the CLI/skill wrapper with human-in-loop intent disambiguation. |
| 2026-06-09 | Plan executed end-to-end (Tasks 1–9, ten commits). Divergences recorded as D3–D5, D7. |
| 2026-06-15 | Plumbing proven on the seed (refutes empty-list `head`, verifies the guarded version; e2e green). Thesis (L5/L6) still open. Living design extracted from the frozen spec + plan; added traceability, freshness stamp, Now/Reopen-if, Non-goals split from Limitations. |
