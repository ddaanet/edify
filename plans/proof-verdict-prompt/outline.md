# Outline — `/proof` proposes a verdict instead of polling for one

## Provenance

- **Derived from:** `none`
- **Base:** `5594a753355c8b5378550d6e05ce11e0d977533c` — the commit this work
  starts from

## Scope

`/proof`'s §Item Iteration ends each item with `Verdict? (a)pprove (r)evise
(k)ill (s)kip`. The letter menu is the elicitation defect
`docs/references/agent-instructions.md` D-78 argues against in its
`AskUserQuestion` form: an option list bounds what the user can say, and the
reply it invites is a single character rather than a judgement. Replace it with
the form D-78 prescribes — a proposal carrying its reason, which the user
corrects.

**IN:** `plugin/skills/proof/SKILL.md` §Item Iteration and §Discussion Sub-Loop;
`plugin/skills/proof/references/item-review.md`; the `docs/` record.

**OUT:** the state-line format, the orientation checkpoint, the iteration
guards, terminal actions, and the anti-pattern list — untouched except where a
sentence names the letter shortcuts. `plans/` artifacts are frozen history. The
other skills' own elicitation, which D-78 already rewrote. Widening D-78's
conclusion from `AskUserQuestion` to bounded option lists generally — that is a
question for my human partner, not this change.

## Invariants this change must not break

- **Forced verdict per item.** Every item gets a recorded disposition before the
  next is presented. A guessed verdict is not a recorded one.
- **Accumulate, then apply as a batch.** Verdicts go to the in-memory list; no
  file edit happens during iteration.
- **All four verdicts stay expressible.** approve / revise / kill / skip, each
  reachable from a free-form reply whatever the agent proposed.
- **`SKILL.md` stays under 200 lines** after `just format`'s 80-column reflow,
  with no crammed lines and no shaved prose — detail moves to
  `references/item-review.md` (cap 400) instead.

## Changes

### 1. `plugin/skills/proof/SKILL.md` §Item Iteration

Replace the `Verdict? (a)pprove …` line in the presentation block with a
placeholder for the proposed verdict. Add two rules beside it (D-53 —
a negative constraint sits with the positive guidance it qualifies):

- **Propose, never poll.** State which verdict the item deserves and why; an
  option list bounds what the user can say, which defeats elicitation.
- **Read the verdict from the reply.** Agreement takes the proposal; any of the
  four is expressible however phrased; an unsettled reply gets one clarifying
  question and never a guessed verdict.

Strip the `(a)`/`(r)`/`(k)`/`(s)` shortcuts from the §Verdicts definitions,
keeping the four semantics verbatim. Reword the non-verdict sentence, which
currently keys on "isn't a recognized verdict shortcut".

### 2. `plugin/skills/proof/SKILL.md` §Discussion Sub-Loop

`**Accumulate:**` says the sub-loop "Returns to verdict prompt" — there is no
prompt to return to. It returns by proposing a verdict again, carrying the
accumulated understanding. Tighten the section's opening sentence in the same
pass to pay for the lines §Item Iteration gains.

### 3. `plugin/skills/proof/references/item-review.md` — new §Verdict Capture

Between §Hierarchical Splitting and §Accumulation Format, so the capture rules
precede the format they feed. Carries what will not fit in the hub: worked
proposal wording, the rule that a proposed revision shows the amended item, the
free-form reply mapping (agreement / different disposition / edit to the shown
revision / settles nothing / substantive feedback), and the one-question bound.

Update §Accumulation Format's `**Revise detail:**` and its `V-2` example line,
both of which say the fix is the *user's stated* one — it may now be the agent's
amended text that the reply accepted.

### 4. `docs/` record

- `docs/references/agent-instructions.md` — one paragraph under D-78 recording
  that `proof`'s inline letter menu was the same defect in a different form, and
  what replaced it. D-78's **conclusion line is untouched**, so
  `docs/decisions.md` needs no edit and `scripts/check_design_links.sh` stays
  green.
- `docs/changelog/2026-09-21-proof-proposes-a-verdict-instead-of-polling.md` plus
  its index bullet at the top of `docs/changelog.md`'s list.

`docs/design.md` FR-16 — "Validate an artifact item-by-item with forced
verdicts" — stays true and stays as written.

## Whole-tree search

`rg -U` over the tree for `(a)pprove`, `approve.*revise.*kill.*skip`, `Verdict?`
and `proof` across `docs/`, `plugin/`, `tests/`, `CLAUDE.md`. Live sites: one,
`SKILL.md:115`. The other four hits are frozen artifacts under `plans/` —
listed in the report, not edited. No test asserts the prompt; `plugin/README.md`
and the caller skills describe `/proof` without naming its prompt.
