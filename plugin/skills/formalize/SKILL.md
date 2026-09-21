---
name: formalize
description: >-
  Verify a Python function against its intended behavior by writing an icontract
  contract and checking it with `edify check` (CrossHair), repairing in a loop.
  Triggers on "formalize", "verify this function", "add a contract and check it",
  or after writing a function whose correctness matters. The in-context agent
  holds intent and asks the user when behavior is ambiguous; CrossHair owns the
  deduction.
allowed-tools:
  - Read
  - Edit
  - Bash
user-invocable: true
---

# Formalize and Check a Function

Drive a propose-contract -> check -> repair loop around one Python function. The
verifier (`edify check`, backed by CrossHair) owns deduction; the skill owns
*intent* — what the function should guarantee. Verification proves code meets a
contract; it does NOT prove the contract is the right one. That judgment stays
here, and genuinely ambiguous intent gets asked about rather than guessed.

## Procedure

1. **Establish intent.** Derive what the target function should guarantee from
   the conversation and the surrounding code. If the intended behavior is
   genuinely ambiguous (edge cases, error handling, empty inputs), ask — do not
   invent a specification.

   Ask inline, in numbered prose, naming the contract clause you would write for
   each case so the user confirms or corrects a concrete guarantee rather than
   discussing behaviour in the abstract:

   ```
   Two cases the code does not settle. Proposed clauses below.

   1. Empty input — `@require(lambda xs: len(xs) > 0)`, i.e. empty is a caller
      error rather than a case returning a default.
   2. Duplicate keys — `@ensure` says last wins. The dict build implies it, but
      nothing states it.
   ```

   Never reach for `AskUserQuestion`. A picker hides the exchange from the
   transcript, and the contract that lands is the *only* durable record of what
   was decided — the reasoning behind it should stay readable in the thread
   beside it.

2. **Write the contract.** Add `icontract` decorators to the function:
   `from icontract import require, ensure`, then
   `@require(lambda <args>: <precondition>)` and
   `@ensure(lambda <args>, result: <postcondition>)`. A target needs at least
   one pre/post-condition or CrossHair will not analyze it.

3. **Check.** Run:

   ```
   edify check <file-or-dotted-target> --json
   ```

   Status is `verified`, `refuted` or `error`, and the exit code encodes it — 0,
   1, 2 respectively. A nonzero exit here is a result, not a command failure:
   this is the case the project's error-handling rule carves out, so read the
   JSON rather than suppressing the exit.

   `--json` also returns `budget` (the per-condition timeout used, `null` at the
   default) and `vacuity_warning` (true for any `verified` reached at the
   default budget). Re-run a `verified` result with an explicit
   `--timeout <seconds>` before reporting it, and state the budget the verdict
   was reached at.

4. **Interpret — the core judgment:**
   - `verified` — no counterexample within CrossHair's search budget. Report and
     stop. State the honest guarantee level: bounded path-exploration, not a
     total proof. State the per-condition budget the verdict was reached at.
   - `refuted` — read the counterexample (falsifying input + location), then
     decide *why* it failed:
     - **code bug** — the implementation is wrong: fix the code.
     - **spec bug** — the contract was wrong or too strong: fix the contract.
     - **intent ambiguity** — the counterexample exposes a case the user has not
       decided (e.g. "what should this do on an empty list?"): STOP and ask.
     Then loop back to step 3.
   - `error` — surface it. A common cause is a target with no contract
     (CrossHair analyzed nothing); add a contract. Never report `error` as
     success.

5. **Loop with a cap.** At most 5 repair iterations — an arbitrary number, not
   calibrated. At the cap, STOP and report the honest state: the last
   counterexample and what remains unresolved. Never upgrade `refuted` or an
   error to "verified".

## Disciplines

- Ambiguity about intent -> ask, never guess.
- Every counterexample gets an explicit code-bug vs spec-bug triage.
- No "verified" claim without a `verified` result from `edify check`.
- A `verified` result is bounded, not a soundness/termination proof — say so.

## Backend

`edify check` wraps CrossHair (symbolic execution + Z3). It is the deduction
oracle; this skill is the intent-holder. Read
`docs/superpowers/design/invariant-guided-verify-loop.md` for the four-state
output contract, the seed-function rule and CrossHair's verbose reporting — it
is the living document and supersedes the 2026-06-08 frozen spec where they
diverge.
