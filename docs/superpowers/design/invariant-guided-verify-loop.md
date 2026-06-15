# Invariant-Guided Verify Loop — Living Design

**Status:** Living. Updated as the design evolves; supersedes the frozen spec
where they diverge.

**Origin artifacts (frozen):**
- Spec: `../specs/2026-06-08-invariant-guided-verify-loop-design.md`
- Plan: `../plans/2026-06-08-edify-check-verify-loop.md` (executed)

**Thesis (the idea being proven):** the LLM guesses properties (its strength);
an external verifier catches what it cannot deduce (its weakness). The verify
loop is the mechanism. Whether the loop is *worth building over one-shot* is the
open claim — see L5, L6.

---

## Functional Requirements

| # | Requirement | State |
|---|-------------|-------|
| FR1 | `edify check <target>` invokes CrossHair on a Python file path or dotted `module.func` and returns a structured verdict. | Done |
| FR2 | Verdict status is one of `verified` / `refuted` / `error`, derived from CrossHair exit codes 0 / 1 / 2. | Done |
| FR3 | A `refuted` result parses each `file:line: error: message` line into a `Finding(location, message)`. | Done |
| FR4 | Process exit codes mirror status (0 verified, 1 refuted, 2 error) so the command composes in `just` recipes and a future eval. | Done |
| FR5 | `--json` emits structured `{status, target, findings, detail}`; default output is human-readable. | Done |
| FR6 | `--timeout` sets CrossHair `--per_condition_timeout`. | Done |
| FR7 | A missing CrossHair executable raises an actionable `CrossHairUnavailableError`, never a silent failure. | Done |
| FR8 | The `formalize` skill drives a propose-contract → check → repair loop with the in-context agent holding intent. | Done |
| FR9 | `formalize` uses `AskUserQuestion` when intent is genuinely ambiguous, rather than inventing a specification. | Done (prose) |
| FR10 | `formalize` triages every counterexample explicitly: code bug → fix code, spec bug → fix contract, intent ambiguity → ask. | Done (prose) |
| FR11 | `formalize` caps repair iterations and, on hitting the cap, reports the honest unresolved state — never upgrades `refuted`/`error` to verified. | Done (prose) |

## Non-Functional Requirements

| # | Requirement | State |
|---|-------------|-------|
| NFR1 | Pure core / thin shell split: `check.py` does parsing + argv with no I/O; `check_cli.py` owns subprocess, formatting, exit codes. | Done |
| NFR2 | Result shape is backend-agnostic so a later Nagini swap is local to `check_cli.py`. | Done |
| NFR3 | TDD throughout; the CLI is unit-tested against fixtures with *known* verdicts, plus a no-mock end-to-end test on the seed. | Done |
| NFR4 | No "verified" claim without a `verified` result from `edify check` (verification-before-completion discipline). | Done (prose) |
| NFR5 | Honest guarantee level: bounded path-exploration, not a soundness or termination proof. The skill states this. | Done (prose) |
| NFR6 | Python 3.14, ruff ALL, mypy strict, docformatter; `just precommit` green. | Done |

## Decisions

| # | Decision | Rationale | Supersedes |
|---|----------|-----------|------------|
| D1 | Backend = CrossHair, not Nagini or Lean. | Concrete counterexamples are CrossHair's core output and the signal the loop feeds on; pure Python, no JVM. Nagini's counterexample output is an experimental flag and concentrates annotation burden where LLMs are weakest. Lean verifies Lean, not Python. | — |
| D2 | Contract style = icontract `@require`/`@ensure`. | Clean pre/post seam, maps to Requires/Ensures, first-class CrossHair support. Plain `assert` is the zero-dep fallback, unused in v0. | — |
| D3 | Command shape = positional `TARGET`, not `<file> --target`. | CrossHair already accepts a file path or dotted `module.func` directly. | Spec §3 |
| D4 | `unknown` is folded into `verified`. | CrossHair has no distinct exit code for "couldn't decide"; a timeout returns 0 — which is exactly the honest definition of verified (no counterexample within budget). | Spec §3 (four-state output) |
| D5 | Seed = integer `head(xs)`, not `average(xs)`. | Floats make `average` a flaky *verifier* target (CrossHair tries `nan`/`inf` and float-rounding), breaking the "fixed verifies" claim. `head` is deterministic and still exercises the spec-refinement branch (fix = add `@require len(xs) > 0`). | Spec §5 |
| D6 | Agent locus = in-context, not an isolated API loop. | Intent lives in project context and sometimes needs *asking*; an isolated agent can converge on a verified answer to the wrong question. | — |
| D7 | `build_crosshair_argv` must NOT pass `--report_verbose`. | Discovered at implementation: `--report_verbose` emits a full traceback, not the parseable `file:line: error:` line. The default output is the machine line we parse. | Spec §3 (which assumed `--report_verbose`) |
| D8 | Eval harness deferred. | Not the primary artifact; a hand-rolled API-key harness is pay-per-token and ToS-disallowed on a subscription. The blessed path is the Agent SDK / `claude -p` on plan credits. | — |

## Limitations

| # | Limitation | Disposition |
|---|------------|-------------|
| L1 | No-contract / vacuous-`verified` detection is not enforced by the CLI; a target with no pre/post-condition is analyzed by nothing. | Deferred to `formalize` skill discipline (it tells the agent to add a contract on `error`). |
| L2 | `unknown` (timeout / unsupported construct) is indistinguishable from `verified` at the CLI boundary. | Accepted for v0 per D4; honest because both mean "no counterexample within budget." |
| L3 | Single-function only; no module / multi-function verification. | Out of scope for v0. |
| L4 | Bounded path-exploration — no soundness or termination guarantee. | Inherent to CrossHair; stated honestly per NFR5. |
| L5 | **The repair loop's advantage over one-shot is unproven.** The spec stakes the loop on closing the paper's ~35–39% one-shot bug-reveal rate; no eval has been run. | Open. Requires the D8 eval harness to measure. |
| L6 | **Human-in-loop > isolated is unproven.** The validation-vs-verification claim has no measurement. | Open. |
| L7 | The `formalize` skill is exercised manually only; its value (in-context judgment) is not automated or measured. | Accepted for v0 per spec §6. |

## History

| Date | Event |
|------|-------|
| 2026-06-08 | Spec approved (CrossHair backend chosen over Nagini/Lean; two differentiators named: repair loop + human-in-loop validation). Prior-art honesty: the core generate-verify-repair pattern is published research, not novel; the unfilled niche is the CLI/skill wrapping with human-in-loop intent disambiguation. |
| 2026-06-09 | Plan executed end-to-end (Tasks 1–9, ten commits). `check.py`, `check_cli.py`, four test files, `head` seed fixtures, `formalize` skill, CLAUDE.md updates all committed. Divergences recorded as D3–D5, D7. |
| 2026-06-15 | Plumbing proven on the seed (CrossHair refutes empty-list `head`, verifies the guarded version; e2e green). Thesis (L5, L6) remains unproven — the loop works as designed but is not yet shown to beat one-shot. This living design extracted from the frozen spec + plan. |
