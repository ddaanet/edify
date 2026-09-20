# Execution routing

Decisions governing how work reaches `/build`: which planning artifact a job
produces, what the runbook layer adds and when the work needs it, and how
escalation is tiered. Read this before changing `/design`, `/runbook` or
`/build`'s routing.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

**D-34 — One execution skill, `/build`, whatever the work arrived as.** It takes
a proofed `runbook.md`, or a `design.md` / `outline.md` with no runbook, or a
task from its own invocation, and runs one lifecycle over all three: entry gate,
pre-work, item walk, review gate, triage feedback, completion.

*Supersedes* (2026-09-17) the split into `/inline` and `/orchestrate`, which
partitioned on whether a runbook existed. The cost was paid twice over: two
skills carrying one lifecycle drifted — three different definitions of a clean
tree between them, two descriptions of the same reviewer's tool list, both wrong
in different ways — and the seam invited the belief that "simple work" needs a
different *skill* rather than a lighter path through one. `/build` is a lean hub
instead: it reaches for subagent ceremony only where the work needs it, so the
simple case is fast without being special-cased.

*Carried forward* from the 2026-09-01 supersession of the three-tier structure —
inline, delegated, orchestrated — whose third tier rested on the
weak-orchestrator premise rejected in `docs/references/pipeline-contracts.md`:
"the inline-versus-delegated distinction survives … as an execution-level
choice, not a route." This merge completes that sentence rather than
contradicting it, and §4 of `/build` is built on it: delegation is decided per
item at dispatch time. External methodology frameworks (Cynefin, XP, Lean
Startup) validate the principle — match process weight to uncertainty — but the
structure derives from how this system executes.

**D-81 — Three planning artifacts, two design routes, one execution skill.**

| Artifact | Means | Goes to |
|---|---|---|
| `design.md` | architecture was uncertain and needed full resolution | `/runbook` |
| `outline.md` | architecture known, or resolved within the outline | `/runbook` or `/build` |
| `runbook.md` | decomposed into typed phases | `/build` |

`outline.md` keeps both consumers: `/design`'s Moderate non-prose route reads
`references/route-to-execution.md` and routes by it, to `/runbook` or to
`/build`; its Simple and agentic-prose route goes to `/build` directly. Those
two were separate branches producing separate artifacts and now produce the same
one, so they are one branch.

`inline-plan.md` is **removed as a kind, not renamed.** It was an `outline.md`
with the architecture section left empty — every field it had, a sufficient
outline has, and `write-outline.md` already says "The outline IS the design"
when its sufficiency criteria hold. The artifact had no identity of its own,
only a consumer, which is how it came to be named after one; `build-plan.md`
would have carried that defect forward under a cleaner name.

**D-35 — Complexity, work type and route are three independent decisions.**
Complexity (Stacey axes) determines design ceremony. Work type
(production/exploration/investigation) determines quality obligations. Route
determines execution mechanics. They are decided at different pipeline stages:
complexity and work type at `/design` Phase 0, which also fixes the route for
Simple and Moderate agentic-prose work — both go straight to `/build`. Moderate
non-prose and Complex work decide the route at the node instead, once the
terminal artifact exists. `references/route-to-execution.md` has four callers:
both of `write-outline.md`'s sufficiency gates, `write-design.md`'s C.5, and
Phase 0's Moderate non-prose route, which generates and `/proof`s its outline
and then reads the node like the rest.

**D-82 — The route asks whether the work needs the runbook layer, not whether it
is prose.** What `/runbook` adds is phases with boundaries
(`build/references/phase-boundary.md`) and a corrector, simplifier and `/proof`
pass over the decomposition itself, so the route turns on whether the work needs
that layer. Three branches: Investigation or Exploration goes to `/build`; a
runbook discriminator holding sends the work to `/runbook`; everything else goes
to `/build`. Two discriminators, either sufficient — cross-file coordination
requiring sequencing, and a decomposition the author judges needs its own review
before execution. The second is **ungrounded** and offers no threshold: no data
exists on the item count at which an unreviewed decomposition fails, so it is
applied unevenly until `triage-feedback.sh` comparisons give data. Prose edits
are commutative — editing file A before or after file B gives the same result —
so multi-file prose is not cross-file coordination; coordination arises from
runtime ordering dependencies such as build↔verify, and a TDD loop alone is not
one. Routing on the material instead — a branch of its own for prose,
"implementation loops" among the discriminators — described the work rather than
what `/runbook` adds, and sent a simple plan with a TDD loop through a layer it
had no use for.

**D-83 — A behavioural change is a tdd item wherever it is written, and `/build`
fires on `Slices:`.** `/build` §4.3 and `build/references/tdd-slice.md` key on
the item carrying `Slices:`, not on a phase attribute, which only a runbook has
(D-30). An outline or design routed to `/build` writes each behavioural change
in the item shape of `runbook/references/runbook-format.md` — `Item 1.M`,
`Slices:`, `Interfaces:` where consumed — by Reading that file rather than
restating it. An item carrying `Slices:` carries nothing else to execute;
general work goes in its own item. The route's second precondition follows: a
behavioural change has its slices written.

**D-36 — Artifact destination determines ceremony, not behavioral-code presence
alone.** Prototype scripts, one-off analysis and spikes do not need runbooks,
TDD or test files even though they contain behavioral code. Design resolves the
complexity; after design a prototype is direct implementation.

**D-37 — Simple classification still routes through `/build`.** Doing the work
in the design session instead — recall, explore, edit, done — bypasses the
integration-test gate, review dispatch, triage feedback and the
deliverable-review chain. That path is retired and so is its name: "direct
execution" survives only in `/build` §4.1, where it means inline rather than
delegated dispatch. Classification determines *design* ceremony, not *execution*
ceremony. Simple therefore gets the same four steps as Moderate agentic-prose —
outline, proof, commit, route to `/build` — which is why those two `/design`
branches collapsed into one (D-81).

**D-38 — Composite tasks are decomposed before classification.**
Batch-classifying an input holding N discrete work items averages heterogeneous
items, so a behavioral-code change gets masked by non-behavioral siblings.
Produce a per-item behavioral-code check; any item adding conditional branches,
functions or logic paths raises that item to Moderate minimum. Distinct from
companion tasks, which the user bundles explicitly.

**D-39 — Self-modifying work leaves the runbook pipeline.** When the planned
work edits pipeline skills or pipeline contracts, a runbook step that edits the
runbook skill creates stale-instruction risk for later steps. Structure it as an
inline task sequence instead, each task executing with fresh instruction loads.
TDD discipline is preserved — the executing session dispatches `test-driver` per
slice. That is one instance of the general route (D-82): the question is whether
the work needs what `/runbook` adds, and a plan that does not — prose or not —
is built directly, with TDD run per slice from the executing session.

**D-40 — Escalation has three tiers.** *Item-level:* a single `UNFIXABLE` item
blocks execution on a missing design decision, ambiguous requirement or external
dependency — the orchestrator stops and surfaces it with an investigation
summary and subcategory (U-REQ, U-ARCH, U-DESIGN). *Local:* the implementation
needs restructuring within the same design — delegate to `refactor` in the
current phase; design and runbook stay valid. *Global:* execution reveals a
design flaw — invalidated assumptions, accumulating same-type UNFIXABLEs,
dependency cycles, an inadequate test plan — so stop and return to planning.

## Rejected alternatives

**A combined time-OR-tool-count timeout signal** — OR-logic is the union of two
kill zones, so it *increases* false positives against either threshold alone.
Spinning (high activity, no convergence) needs a turn bound; hanging (no
activity, high wall-clock) needs a duration timeout. They are independent
guards. Neither is implementable today (L-4).
