# Item 1.3 — `docs/design.md` corrections

Scope: `docs/design.md` only. All corrections in place; no renumbering; two
new decisions appended to the end of the D-nn sequence (D-82, D-83).

## Step 1 — D-80 (`:544`)

**Consumer clause.** Before: "`/edify:deliverable-review` builds its range as
`<Base>..HEAD`, and asks the user for the range when the section is absent or
when `<Base>` does not resolve to a commit." After: the range is established
by `edify-review-range.sh`, a script in the plugin's `bin/` invoked by bare
name, which parses §Provenance and emits one verdict line — the range, or a
verdict with no range (section absent, `<Base>` unresolvable, prior artifact
missing or carrying no full-sha base) on which the skill asks the user. Where
`Derived from:` names a prior artifact the script reads that artifact's
`Base:` and compares, and **stops on a conflict**, substituting neither value
because a conflict means one of the two artifacts is wrong and the script
cannot know which. One hop only.

Recorded as the decision, not as shipped state: the text states what the
consumer does, with no claim about when the script landed. Item 1.2 writes it.

**"No mechanical validator".** Before: "the clause is prose with no mechanical
validator, so the outline- and design-correctors check it only after the
artifact is written". After: "nothing validates a `Base:` at the moment the
author writes it — the write side is prose, and only the read side is
mechanically checked."

**Accepted-tradeoffs clause.** Before: the correctors "cannot repair it — a
base they supplied would be the same recomputation, so they leave a `TODO` for
the author instead." After, per KD-1: they repair it in two halves — copy a
prior artifact's full-sha `Base:` verbatim where `Derived from:` resolves to
one (the author's own rule, not a computation), and leave a `TODO` in `Base:`
where nothing can be copied. Plus the two invariants: never overwrite a
present `Derived from:`; never write a base obtained any way other than the
verbatim copy, since `git log`, `git merge-base` and `HEAD` are all the
recomputation the Critical case names.

## Step 2 — the D-81 passage (was `:599-602`)

Before: "`/design`'s Moderate non-prose route sends it to `/runbook`, its
Simple and agentic-prose route to `/build`." After, per KD-5: the Moderate
non-prose route reads `references/route-to-execution.md` and routes by it, to
`/runbook` or to `/build`; Simple and agentic-prose goes to `/build` directly.
The following sentence ("Those two were separate branches…") is unchanged in
substance.

## Step 3 — D-35 (`:611`) and its caller enumeration (was `:617-618`)

Before: Phase 0 "also fixes the route for Simple and Moderate work; Complex
work decides its route later … both of `write-outline.md`'s sufficiency gates
and `write-design.md`'s C.5 read `references/route-to-execution.md`." After:
Phase 0 fixes the route for Simple and Moderate **agentic-prose** work, both
going straight to `/build`; Moderate non-prose and Complex decide at the node.
The enumeration is now four callers — both sufficiency gates, C.5, and Phase
0's Moderate non-prose route, which generates and `/proof`s its outline and
then reads the node like the rest.

## Step 4 — D-39 (`:642`)

Its own ground — stale-instruction risk when a runbook step edits the runbook
skill, and TDD preserved by dispatching `test-driver` per slice — is
untouched. Only the closing generalisation changed. Before: "Also applies when
there is no parallelization benefit or when coordination cost exceeds
error-recovery value." After: "That is one instance of the general route
(D-82): the question is whether the work needs what `/runbook` adds, and a
plan that does not — prose or not — is built directly, with TDD run per slice
from the executing session."

## Step 5 — the routing decision itself (added)

Greps for `route-to-execution`, `prose path`, `implementation loops`,
`Prose edits are commutative`, `discriminator`, `Slices:`, `§4.3`,
`Investigation or Exploration` found **no** decision recording the node's
branches: the doc named the node (D-35's enumeration) and cited its outcome
(D-81, D-39) but never stated what it decides. The old four-branch route and
the prose-path branch were therefore not recorded as current truth anywhere,
so there was nothing to correct — the gap was the defect. Two decisions added
in §6.5 Execution routing, after D-35 and before D-36, in the doc's D-nn
style:

- **D-82 — The route asks whether the work needs the runbook layer, not
  whether it is prose.** States what `/runbook` adds; the three branches;
  both discriminators with the second marked **ungrounded** and offering no
  threshold (applied unevenly until `triage-feedback.sh` comparisons give
  data); the commutativity definition under the first discriminator, with
  coordination arising from runtime ordering dependencies such as
  build↔verify and a TDD loop alone not being one; and one sentence of
  rationale for why routing on the material — a prose branch,
  "implementation loops" as a discriminator — was the wrong key.
- **D-83 — A behavioural change is a tdd item wherever it is written, and
  `/build` fires on `Slices:`.** KD-4: `/build` §4.3 and `tdd-slice.md` key
  on the item carrying `Slices:` rather than on a phase attribute (citing
  D-30, which is left intact — a runbook's phases still declare a type); an
  outline or design routed to `/build` writes behavioural changes in
  `runbook-format.md`'s item shape by Reading it; an item carrying `Slices:`
  carries nothing else to execute; the route's second precondition follows.

Why added rather than left out: D-39's reworded closing and D-35's split both
cite the general rule, and a living record that cites a rule it does not state
sends the reader to a skill body for current truth.

## Constraints

Paths cited in the doc's own `plugin/`-relative style (`build/references/…`,
`runbook/references/…`) matching the surrounding text. No dates, no
"previously"/"formerly" narration — `docs/changelog.md`'s 2026-09-20 entry
carries the history. No decision renumbered. `docs/design.md` goes from 1165
to 1213 lines (+64 −16); 30 of the added lines are the two new decisions, the
rest is the rewritten D-80, D-81, D-35 and D-39 prose.

## Precommit

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

`docs: Item 1.3 — record provenance repair and routing by need in the design`
