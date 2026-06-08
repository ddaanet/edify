# Invariant-Guided Verify Loop — Design

**Date:** 2026-06-08
**Status:** Approved design, pre-implementation
**Mission link:** First concrete step of Edify's empirical-formal direction
(`../ddaanet/drafts/brief-invariant-guided-agent.md`)

## 1. Context

Edify's direction is **invariant-guided agentic code generation**: the LLM
explores and *guesses properties* (its strength), an external verifier catches
what doesn't hold (the LLM's weakness — multi-step deduction). This design is
the first concrete, useful artifact on that path.

The brief's loop:

```
prototype -> observe what holds -> formulate invariants -> verify (external) -> extend
```

This design builds the smallest *useful* slice of that loop: verify a single
Python function against a contract, feed counterexamples back, repair — with an
in-context agent holding intent.

### Backend decision: CrossHair (not Nagini, not Lean)

- **CrossHair** (`crosshair-tool`, PyPI) — symbolic execution for Python via
  Z3. Returns concrete counterexamples as its *core* function. Pure Python, no
  JVM. Chosen for v0.
- **Nagini** rejected for v0: static proofs are stronger, but it needs a JVM +
  Viper, concentrates an annotation burden (permission/separation logic) onto
  the LLM exactly where research says LLMs are weakest, and its counterexample
  output — the signal this loop feeds on — is an experimental flag. Deferred as
  a later, stronger backend. The CLI result shape is backend-agnostic so the
  swap is local.
- **Lean** rejected: Lean verifies Lean, not Python. Its value (mathlib, a huge
  manual-proof library) cashes out for *proving mathematics*, not verifying the
  behaviour of Python functions. Using Lean would mean generating Lean as the
  product — a different mission. The brief cites Leanstral as architectural
  prior art (LLM + perfect verifier + pass@N), not as a tool to adopt.

### Prior art (honest)

The core combination is **published research, not novel**:

- *Beyond Postconditions: Can LLMs infer Formal Contracts…?* (arXiv 2510.12702,
  Oct 2025) — LLM generates contracts (tool: **NL2Contract**), CrossHair
  verifies, finds real Python bugs (14/19 findable). **One-shot, no repair
  loop, no human-in-the-loop, no released developer tool.**
- SpecPylot (arXiv 2604.16560), arXiv 2601.12845 — more LLM spec-generation.
- Generate-verify-repair with counterexamples is a saturated *research* pattern
  (loop-invariant repair, Verus/Dafny proof repair, CEGIS, VeriAct, AgentCoder).

The brief's claim that "nobody has published this pattern" does **not** hold as
of mid-2026. What is **not** shipped anywhere found (PyPI, GitHub, the CrossHair
author's own work): a **CLI / skill / MCP** that wraps CrossHair in an
**iterative repair loop with human-in-the-loop intent disambiguation** for an
in-context coding agent. That is the free niche this fills.

Two differentiators — both are gaps the literature explicitly names as missing:

1. **The repair loop.** The paper's own number is the argument: one-shot specs
   reveal the bug only ~35–39% of the time. Closing that gap *is* the loop.
2. **Validation, not just verification.** Human-in-the-loop intent
   disambiguation. Unbuilt as a product.

Net: not novel science — research-validated approach (de-risked), productized
into an unfilled niche. The contribution is engineering + the human-in-loop
discipline.

## 2. Load-bearing principle

**Separate validation from verification, and place each where it belongs.**

A verifier proves *code satisfies its contract*. It says nothing about whether
the *contract is the right one*. An isolated agent that writes both code and
contract can converge on a self-consistent pair that is functionally wrong — a
verified answer to the wrong question. Intent lives in the broader project
context and sometimes requires *asking*. Therefore:

- **Verification (deduction)** — offloaded to CrossHair, external.
- **Validation (intent)** — owned by the **in-context** agent, which has
  project context and can ask the user when intent is ambiguous. Never an
  isolated API loop.

```
   in-context agent (Claude, in session)
   holds INTENT · has project context · ASKS when intent is ambiguous
       1. establish intent (ask if unclear)
       2. write/refine contract (icontract Requires/Ensures)
       4. judge result:  code bug -> fix code
                         spec bug -> fix contract
                         intent unclear -> ASK
                          |
                          v
       3. edify check <target>  ->  CrossHair (external)
          structured result: verified / refuted(+input) / unknown / error
```

## 3. Component A — `edify check` CLI

The reusable, testable verification oracle. New command in `edify-cli` (Click,
`src/edify/`, same patterns as `tokens` / `markdown`). Knows nothing about LLMs
or intent.

- **Input:** a Python file; optional `--target <module.func>` to scope to one
  function.
- **Action:** invokes CrossHair on the target with verbose counterexamples
  enabled. (CrossHair emits machine-readable `<file>:<line>: error: <message>`
  on stdout; `--report_verbose` adds the counterexample input. Exact flags
  pinned against the installed `crosshair --help` during implementation.)
- **Output — one structured result**, default human-readable, `--json` for the
  machine path / future eval:
  - `verified` — no counterexample found within budget
  - `refuted` — falsifying input, violated condition, `file:line`
  - `unknown` — CrossHair could not decide (timeout / unsupported construct)
  - `error` — target missing, **no contract present**, CrossHair crashed
    (surfaced, never swallowed — project error-handling rule)
- **Contract style:** **icontract** `@require` / `@ensure` (decorator-based,
  clean pre/post split, maps to the brief's Requires/Ensures vocabulary,
  first-class CrossHair support). `crosshair-tool` and `icontract` become
  dependencies. Plain `assert` is the zero-dependency fallback, not used in v0.
- **Exit codes:** `0` verified / nonzero refuted, so it composes in `just`
  recipes and the future eval.
- **Note (CrossHair gate):** CrossHair only analyzes a function that has at
  least one pre/post-condition. A target without a contract is an `error`
  result, not `verified`.

The CLI is unit-tested against fixture functions with *known* CrossHair verdicts
(verified / refuted / unknown / error) — no LLM involved — so its normalization
is pinned independently.

## 4. Component B — `formalize` skill

Working name `formalize` (changeable). The in-context agent's procedure; owns
intent, orchestrates the loop. Has project + conversation context; the CLI does
not.

**Procedure:**

1. **Establish intent.** Derive what the target function *should* guarantee from
   conversation + project context. If genuinely ambiguous, **`AskUserQuestion` —
   do not guess.** (The discipline an isolated agent structurally cannot honor.)
2. **Write the contract.** icontract `@require` / `@ensure` capturing that intent.
3. **Verify.** Run `edify check --target … --json`.
4. **Interpret — the core judgment:**
   - `verified` → report and stop.
   - `refuted` → decide *why*: **code bug** → fix code; **spec bug** → fix
     contract; **intent ambiguity exposed** → stop and ask the user. Then loop.
   - `unknown` → report honestly; **never upgrade `unknown`/`refuted` to
     "verified."** Optionally narrow the contract and note the limitation.
   - `error` → surface it.
5. **Loop with a cap** (max repair iterations) so it cannot thrash. On hitting
   the cap, **stop and report the honest state** (last counterexample, what is
   unresolved) — not a false success.

Embedded disciplines: ambiguity → ask; counterexample → explicit
code-vs-spec triage; no success claim without a `verified` result
(verification-before-completion).

## 5. Seed / validation

One Python function with a *known, subtle* bug that CrossHair finds *fast*, so
the loop demonstrably catches something. Preferred shape: a function where the
naive postcondition is refuted on an edge input, exercising the
**spec-refinement** branch (a missing `@require`) rather than only a code fix —
e.g. `average(xs)` with `@ensure min(xs) <= result <= max(xs)`, refuted on the
empty list, fixed by adding `@require len(xs) > 0`. Exact seed pinned at
implementation time. Criterion: subtle real bug, fast counterexample, exercises
the code-vs-spec judgment.

## 6. Testing

TDD. The CLI is unit-tested against fixtures with known CrossHair verdicts. The
skill is exercised manually against the seed in v0 (its value is the in-context
judgment, not yet automated). `just precommit` stays green throughout.

## 7. Non-goals (v0)

- **Autonomous Agent-SDK eval harness** (brief step 4) — later, on plan credits,
  to *measure* convergence across many functions. Note on billing: a hand-rolled
  API-key harness is both pay-per-token *and* (on a subscription) ToS-disallowed;
  the official Agent SDK / `claude -p` is the blessed, plan-credit path. Not now.
- **Nagini** backend — later upgrade; result shape kept backend-agnostic.
- **Module / multi-function** verification — single function first.
- **Pipeline redesign** (brief step 5) and touching the old `requirements`
  skill — out of scope. Intent-capture now lives *inside* this loop, so the
  "rebuild requirements" thread is superseded, not pursued here.
- No claims of **soundness / termination** — CrossHair is bounded
  path-exploration; the skill states its guarantee level honestly.

## 8. Decisions made

| Decision | Choice | Why |
|----------|--------|-----|
| Backend | CrossHair | reliable counterexamples, no JVM, executes brief step 3 |
| Contract style | icontract `@require`/`@ensure` | clean pre/post seam, CrossHair-native |
| Command shape | `edify check <file> --target …` | fits existing `edify-cli` |
| Agent locus | in-context, not isolated API loop | intent needs context + ability to ask |
| Eval harness | deferred | not the primary artifact; demote to measurement |
