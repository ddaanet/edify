# Route to Execution

Read at the end of a sufficiency gate, once the user has confirmed the
artifact — `outline.md` or `design.md` — as this job's terminal design
artifact.

The question is **does this work need a runbook?** Not whether this session
can execute it: a `/build` run may span several sessions. The decision stays
here because `/build` §1 takes whichever artifact exists and never routes
back to `/runbook`.

## Preconditions

Both bind every branch this node routes, prose included. Phase 0's Simple and
Moderate-agentic-prose routes reach `/build` without reading this node, so
neither precondition binds them.

- Every decision **the executor would otherwise have to make** is resolved.
  This is not "no open questions": an Exploration job exists to answer one,
  and that question is its deliverable rather than a blocker.
- Edit targets are named, section-level or line-level. With no runbook the
  artifact **is** the item list, so `/build` walks what the artifact names.

## Route

```
IF all prose edits, no implementation loops        → /build
ELSE IF work type = Investigation                  → /build
ELSE IF work type = Exploration                    → /build
ELSE (work type = Production AND behavioral code)  → /runbook
```

The first branch is a hard gate — file count is irrelevant to it.

**Prose path rationale:** Prose edits are commutative — editing file A before
or after file B produces the same result. Multi-file prose does not
constitute cross-file coordination. Coordination complexity arises from
runtime ordering dependencies (test↔implementation, build↔verify), not from
editing multiple files.

## Runbook discriminators

Either one holding sends the work to `/runbook` rather than `/build`:

- Cross-file coordination requiring sequencing. Phases exist for this.
- Implementation loops (test/build feedback). `tdd` slices exist for this.

## Terminal action

- **`/build`** — commit the artifact, then name `/build plans/<job>` as the
  next command and stop. No tail-call: `/build` consumes no continuation.
- **`/runbook`** — commit the artifact and stop.
- **A precondition failed** — name it, then resume from A.5 to revise the
  outline or from C.1 to revise the design. Do not route.

Read per sub-problem from the multi-sub-problem gate: record the outcome in that
sub-problem's readiness summary — the route, or the failed precondition and
not-routable — and name no command. Resume neither A.5 nor C.1: the caller
dispatches, and the gate decides what a not-routable sub-problem does to the
outline.
