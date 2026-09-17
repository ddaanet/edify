# Review: docs/design.md D-80 (m-1 fix)

## Scope

`docs/design.md` D-80 only, per outline `plans/provenance-reach-and-sweep/outline.md`
Region 5 finding m-1 and its "D — D-80 is corrected in place" decision.

## Change under review

`docs/design.md:549`, in D-80's *Consumer:* clause:

> asks the user for the range when the section is absent **or** when `<Base>`
> does not resolve to a commit.

Diff: `and` → `or`.

## Findings

No defects found. The `and`→`or` fix is correctly applied and no further
changes are needed within scope.

### Criterion: `or` reads correctly, states two independent triggers

Confirmed. "when the section is absent or when `<Base>` does not resolve to a
commit" reads as two independent sufficient conditions, matching the intended
semantics: either condition alone triggers the user prompt.

### Criterion: D-80 and `deliverable-review/SKILL.md:31` agree

Confirmed, both quoted:

- `docs/design.md:549` — "asks the user for the range when the section is
  absent or when `<Base>` does not resolve to a commit."
- `plugin/skills/deliverable-review/SKILL.md:31` — "Ask the user for the range
  when the artifact carries no Provenance section, or when
  `git rev-parse <Base>^{commit}` does not resolve."

Both now specify identical behaviour: two independent fallback triggers joined
by `or`, either sufficient alone.

### Criterion: no other clause of D-80 contradicts the corrected trigger logic

Checked the full D-80 paragraph (`docs/design.md:544-563`), specifically the
*Accepted tradeoffs* clause about correctors leaving a `TODO`: "the clause is
prose with no mechanical validator, so the outline- and design-correctors
check it only after the artifact is written, and they cannot repair it — a
base they supplied would be the same recomputation, so they leave a `TODO`
for the author instead."

No contradiction. A `TODO` placeholder left in an unrepairable Provenance
block is exactly the case where `<Base>` fails to resolve to a commit — it
reaches the second trigger, and with `or` that trigger now fires on its own
regardless of whether the section itself is present. This is the defect the
fix addresses (per the outline's stated rationale) and the surrounding prose
is consistent with it.

### Criterion: present tense, standing rule, no write-time narration

Confirmed. The full D-80 paragraph is written in present tense throughout
("carries", "asks", "takes", "copies", "leave", "fall", "surface") with no
narration of when or why the edit was made. The one `and` remaining in the
sentence ("builds its range as `<Base>..HEAD`, and asks the user...") is an
ordinary sentence conjunction between two actions the consumer performs, not
part of the two-trigger OR logic, and does not need to change.

## Out of scope, not touched

- `plugin/` files (reviewed separately).
- `docs/changelog.md` — no entry added, per decision in outline ("D — D-80 is
  corrected in place, with no changelog entry").
- No new decision id proposed.

## Verdict

D-80 is correct as changed. No edits made.
