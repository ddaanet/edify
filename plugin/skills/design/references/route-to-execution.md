# Route to Execution

Read once the artifact — `outline.md` or `design.md` — is confirmed as this
job's terminal design artifact: at the end of either sufficiency gate, at
C.5, or, on Phase 0's Moderate non-prose route, once `/proof` has approved
the generated outline.

The question is **does this work need a runbook?** Not whether this session
can execute it: a `/build` run may span several sessions. The decision stays
here because `/build` §1 takes whichever artifact exists and never routes
back to `/runbook`.

## Preconditions

The first binds every branch this node routes. The second binds the `/build`
branches only, and is evaluated after the route — on the `/runbook` branch,
naming edit targets is `/runbook`'s job. Phase 0's Simple and
Moderate-agentic-prose routes reach `/build` without reading this node, so
neither precondition binds them.

- Every decision **the executor would otherwise have to make** is resolved.
  This is not "no open questions": an Exploration job exists to answer one,
  and that question is its deliverable rather than a blocker.
- Edit targets are named, section-level or line-level, and every behavioural
  change has its slices written. With no runbook the artifact **is** the item
  list, so `/build` walks what the artifact names; write a behavioural change
  in the item shape of `../runbook/references/runbook-format.md`.

## Route

```
IF work type = Investigation or Exploration   → /build
ELSE IF a runbook discriminator holds         → /runbook
ELSE                                          → /build
```

## Runbook discriminators

What `/runbook` adds is phases with boundaries
(`../build/references/phase-boundary.md`), and a corrector, simplifier and
`/proof` pass over the decomposition itself. Either discriminator holding
sends the work to `/runbook` rather than `/build`:

- Cross-file coordination requiring sequencing. Phases exist for this. Prose
  edits are commutative — editing file A before or after file B produces the
  same result — so multi-file prose is not cross-file coordination.
  Coordination arises from runtime ordering dependencies such as
  build↔verify.
- A decomposition the author judges needs its own review before execution.
  This is **ungrounded** and offers no threshold: no data exists on the item
  count at which an unreviewed decomposition fails.

## Terminal action

- **`/build`** — commit the artifact, then name `/build plans/<job>` as the
  next command and stop. No tail-call: `/build` consumes no continuation.
- **`/runbook`** — commit the artifact and stop.
- **A precondition failed** — name it, then resume to revise the artifact:
  from A.5 for an outline, from C.1 for a design, or — for a Phase 0
  Moderate non-prose caller, which ran neither — from that route's own
  generate step. Do not route.

Read per sub-problem from the multi-sub-problem gate: record the outcome in that
sub-problem's readiness summary — the route, or the failed precondition and
not-routable — and name no command. Resume neither A.5 nor C.1: the caller
dispatches, and the gate decides what a not-routable sub-problem does to the
outline.
