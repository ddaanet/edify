# Discuss Directive: Add Divergent Thinking Step

Brief from devddaanet session (2026-03-06). Droplet resize recipe naming took 5 rounds of user-driven iteration to reach `off/small/big` from `resize s-2vcpu-4gb`.

## Problem

The discuss protocol (`d:` directive) is entirely convergent: ground → assess → stress-test → verdict. Every step narrows toward correctness of the *current* proposal. No step generates alternatives or reframes the problem.

"Argue against your OWN position" tests the proposal's weaknesses but doesn't generate different approaches. The agent defends its framing until the user pushes a reframe.

## Observed Failure

Naming progression for droplet resize recipes:

1. `resize s-2vcpu-4gb` — mechanism + DO slug (agent's first proposal)
2. `resize 4g` — mechanism + human label (user pushed)
3. `ram 4g` — different verb (justfile can't start with digit)
4. `fourg/twog` — literal state names (user pushed)
5. `off/small/big` — abstract state names (user pushed reframe)

Each step required explicit user intervention. The reframe from "resize operation" to "state transition" is where the good naming lived. A divergent step at step 1 would have generated the state-naming framing alongside the mechanism framing.

## Proposed Change

Add a divergent step to the discuss protocol, after grounding and before assessment:

> Generate 3+ alternative framings. At least one must reframe the problem (different conceptual frame), not just vary the solution within the current frame.

## Artifacts to Modify

1. **`agent-core/hooks/userpromptsubmit-shortcuts.py`** — `_DISCUSS_EXPANSION` string (lines 82-96). Add the divergent step between "Ground first" and "Form your assessment."

2. **`agent-core/fragments/pushback.md`** — "Design Discussion Evaluation" section (lines 5-33). Add divergent thinking step between "Ground your evaluation" and "Form your assessment" subsections.

## Scope Constraint

The divergent step is unconditional — discuss is never about factual assessment (those don't need `d:`), so every discuss invocation is a design space that benefits from alternatives. No conditional trigger needed.

## Acceptance

After the change, `d: <proposal>` should produce 3+ framings before narrowing to a verdict. At least one framing should differ conceptually from the proposal's implicit frame.
