# 2026-09-20 — the route asks whether the work needs a runbook, not whether it is prose

`route-to-execution.md` routed by material: a prose path of its own, and
"implementation loops" among the runbook discriminators. Both described the work
rather than what `/runbook` adds, which is phases with boundaries and a
corrector, simplifier and `/proof` pass over the decomposition itself. The route
is now three branches — Investigation or Exploration to `/build`, a runbook
discriminator to `/runbook`, everything else to `/build` — so a plan simple
enough not to need that layer is built directly whether it is prose or not. Two
discriminators remain: cross-file coordination requiring sequencing, and a
decomposition the author judges needs its own review before execution. The
second is **ungrounded** and offers no threshold; no data exists on the item
count at which an unreviewed decomposition fails. The prose path's own
contribution survives as a definition under the first — prose edits are
commutative, so multi-file prose is not cross-file coordination.

An outline routed to `/build` therefore carries behavioural changes, which only
a runbook carried before. It writes each one in the item shape of
`runbook-format.md`, and `/build` §4.3 and `tdd-slice.md` now fire on an item
carrying `Slices:` rather than on a phase attribute no outline has. Phase 0's
Moderate non-prose route stops hard-coding `/runbook`: it generates, `/proof`s,
then reads the routing node like the other callers, which go from three to four.
The multi-sub-problem gate gains the branch the node had been deferring to: a
sub-problem recorded not-routable reopens its own entry alone — siblings with no
dependency path through it stay dispatchable, its dependents are held, and the
user confirms the revised entry rather than the whole outline.

This narrows the
[2026-09-17 routing-node entry](2026-09-17-one-routing-node-in-design-artifacts-record-base-commit.md).
Its "preconditions, which bind every branch including prose" was already wider
than what shipped: the first precondition — every decision the executor would
otherwise make is resolved — binds every branch the node routes, while the
second — edit targets named — binds the `/build` branches only, since on the
`/runbook` branch naming targets is `/runbook`'s job.
