# Item 1.8 — not-routable sub-problem branch and changelog entry

Requirements: M-5, m-4. Key decisions: KD-3 to KD-6 (changelog), KD-6 (branch).

## `write-outline.md` — new branch, lines 187-193

Inserted in the Multi-Sub-Problem Sufficiency Gate, after the `**If sufficient**`
block (`:181-185`) and before `**If insufficient**` (now `:195`).

```markdown
**If a sub-problem is not routable** — the node records not-routable in that sub-problem's readiness summary instead of a route. Resume A.5 for that entry alone:
- Siblings with no dependency path through the not-routable entry stay dispatchable
- Its dependents are held; the readiness summary names which ones are held and on what
- Only the revised entry goes back through `references/route-to-execution.md` — the rest of the outline is not reopened
- The user confirms that entry, not the whole outline
- Held dependents release once the entry routes
```

The existing "per sub-problem" bullet in `**If sufficient**` is unchanged. The
one path written is skill-relative (`references/route-to-execution.md`), per the
outline's cross-cutting rule; no repo-relative `plugin/…` path was introduced.

This is the branch `route-to-execution.md`'s closing sentence defers to ("the
gate decides what a not-routable sub-problem does to the outline"), which M-5
reported as pointing at nothing.

## `docs/changelog.md` — new entry, lines 14-46

Placed at the top of the entry list, above the 2026-09-17 routing-node entry,
which is left untouched (the file is a write-time record). No KD labels: the
file's other entries cite `docs/design.md` decision ids (D-nn) and file paths,
never plan decisions, so the changes are described rather than labelled. Item
1.3 records the KD numbers in `docs/design.md`.

```markdown
## 2026-09-20 — the route asks whether the work needs a runbook, not whether it is prose

`route-to-execution.md` routed by material: a prose path of its own, and
"implementation loops" among the runbook discriminators. Both described the
work rather than what `/runbook` adds, which is phases with boundaries and a
corrector, simplifier and `/proof` pass over the decomposition itself. The
route is now three branches — Investigation or Exploration to `/build`, a
runbook discriminator to `/runbook`, everything else to `/build` — so a plan
simple enough not to need that layer is built directly whether it is prose or
not. Two discriminators remain: cross-file coordination requiring sequencing,
and a decomposition the author judges needs its own review before execution.
The second is **ungrounded** and offers no threshold; no data exists on the
item count at which an unreviewed decomposition fails. The prose path's own
contribution survives as a definition under the first — prose edits are
commutative, so multi-file prose is not cross-file coordination.

An outline routed to `/build` therefore carries behavioural changes, which
only a runbook carried before. It writes each one in the item shape of
`runbook-format.md`, and `/build` §4.3 and `tdd-slice.md` now fire on an item
carrying `Slices:` rather than on a phase attribute no outline has. Phase 0's
Moderate non-prose route stops hard-coding `/runbook`: it generates, `/proof`s,
then reads the routing node like the other callers, which go from three to
four. The multi-sub-problem gate gains the branch the node had been deferring
to: a sub-problem recorded not-routable reopens its own entry alone — siblings
with no dependency path through it stay dispatchable, its dependents are held,
and the user confirms the revised entry rather than the whole outline.

This narrows the 2026-09-17 routing-node entry below. Its "preconditions,
which bind every branch including prose" was already wider than what shipped:
the first precondition — every decision the executor would otherwise make is
resolved — binds every branch the node routes, while the second — edit targets
named — binds the `/build` branches only, since on the `/runbook` branch naming
targets is `/runbook`'s job.
```

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, full output:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

Subject `docs: Item 1.8 — not-routable sub-problem branch and changelog entry`,
staging `plugin/skills/design/references/write-outline.md`, `docs/changelog.md`
and this report together. The hash is not written here: this report is inside
the commit it would name, so any value recorded would be the pre-amend one. The
hash is reported to the dispatching agent, and `git log -1` on `main` gives it.
