# Implementation report — `/proof` proposes a verdict instead of polling

## Triage (`/design` Phase 0)

**Classification: Simple.** Both axes high, no behavioral code.

- **Implementation certainty: High** — a prose rewrite of one section of a skill
  body plus its reference file. No new mechanism: the replacement form is the
  one `docs/references/agent-instructions.md` D-78 already prescribes for
  elicitation (a proposal carrying its reason, which the user corrects).
- **Requirement stability: High** — the change and its invariants were stated in
  the request; scope is the `proof` skill and the docs describing it.
- **Behavioral code check: No** — markdown under `plugin/skills/` only.
- **Work type: Production.** **Artifact destination: agentic-prose.**

Simple and Moderate-agentic-prose are the *same route* in `/design` Phase 0, so
the classification carried no routing risk either way. Full block, with the
requirements-clarity gate and the author-corrector coupling check (coupled
corrector: none), is in `plans/proof-verdict-prompt/classification.md`. Outline
in `plans/proof-verdict-prompt/outline.md`, base commit
`5594a753355c8b5378550d6e05ce11e0d977533c`.

Recall surfaced `memory/line-caps.md` (the 200-line `SKILL.md` cap is a hard
gate; never satisfy it by shaving prose — move detail to a seam instead) and
`memory/style-edit-briefs.md` (a load-bearing em-dash survives an edit pass).
Design nodes read: `agent-instructions.md` D-61/D-62/D-78, `quality-gates.md`
D-48/D-50/D-52/D-53.

## Files changed

### `plugin/skills/proof/SKILL.md` — 197 → 199 lines (cap 200, no allowlist entry)

- **:115** — `Verdict? (a)pprove (r)evise (k)ill (s)kip` →
  `[proposed verdict in prose, with its reason; a revision shows the amended
  item]`. The presentation block now ends in a placeholder for the proposal
  rather than a menu.
- **:118-122 (new)** — `**Propose a verdict; never poll for one.**` The reason
  (an option list bounds what the user can say, which defeats elicitation) sits
  beside the positive rule per D-53, followed by the capture rule: agreement
  takes the proposal, all four verdicts stay expressible however phrased, an
  unsettled reply gets **one** clarifying question and never a guess. Points at
  `references/item-review.md` for the cases.
- **:130-135** — `**Verdicts**` list: `(a)`/`(r)`/`(k)`/`(s)` shortcuts dropped,
  the four semantics kept. `revise` re-worded from "user states fix" to "the fix
  the reply settles on" (the fix may now be the agent's amended text the reply
  accepted). `kill`'s sub-action condensed from a quoted prompt to an ask.
- **:137-138** — `**Non-verdict input is implicit discussion.**` keyed on "isn't
  a recognized verdict shortcut" → "settles no verdict and answers no clarifying
  question". Dropped the trailing sentence about the conversational medium,
  which the new §Item Iteration now states directly.
- **:142** — §Discussion Sub-Loop opener tightened from two lines to one.
- **:148** — `**Accumulate:**` "Returns to verdict prompt with accumulated
  understanding" → "when discussion concludes, propose a verdict again, carrying
  it". There is no prompt to return to.

The net +2 is paid for out of §Discussion Sub-Loop and the condensed `kill`
bullet; nothing was crammed and no prose was shaved. Count is after
`just format`'s 80-column reflow.

### `plugin/skills/proof/references/item-review.md` — 95 → 131 lines (cap 400)

- **:39-72 (new)** — **§Verdict Capture**, placed between §Hierarchical Splitting
  and §Accumulation Format so capture precedes the format it feeds. Carries the
  worked proposal wording, the rule that a proposed revision shows the amended
  item, the five-case mapping of a free-form reply (agreement / a different
  disposition / an edit to the shown revision / settles nothing → one clarifying
  question / substantive feedback → the sub-loop), and the one-question bound
  (a second unsettled answer is discussion, not a third question).
- **:82** — accumulation example `revise: "[user's stated fix]"` →
  `revise: "[the settled fix]"`.
- **:92-95** — `**Revise detail:**` "Capture the user's stated fix verbatim" →
  "Capture the settled fix verbatim — the amended item the reply accepted, or the
  user's own wording where they supplied it."
- **:129** — §Revisit: "Re-enter verdict prompt for the identified item" →
  "Propose a verdict afresh for the identified item".

### `docs/references/agent-instructions.md` — new paragraph under D-78

D-78's **conclusion line is untouched**, so `docs/decisions.md` needed no edit
and `scripts/check_design_links.sh` stays green (86 decisions indexed,
conclusions match). The paragraph records that the bounded option list is the
defect rather than the tool rendering it: `proof`'s menu was inline, so the
`allowed-tools` omission that enforces D-78 never reached it. It states what
replaced it and leaves the widening question open in the node itself.

### `docs/changelog/2026-09-21-proof-proposes-a-verdict-instead-of-polling.md` (new) + index bullet

New entry file matching the split changelog's shape, plus a bullet at the top of
`docs/changelog.md`'s list. Design-significant because it changes how the
pipeline's sole user-validation gate elicits a disposition.

`docs/design.md` FR-16 — "Validate an artifact item-by-item with forced
verdicts" — is unchanged and still true, so the hub needed no edit.

## Invariants verified against the edited text

- **Forced verdict per item** — `SKILL.md:121-122` ("never a guess"),
  `item-review.md:63-66` ("never present the next item until this one's verdict
  is recorded"), and the untouched `SKILL.md:196-197` anti-pattern
  ("Advancing past an item without an explicit verdict").
- **Accumulate, then apply as batch** — `SKILL.md:147` and §Terminal Actions
  untouched; §Iteration Guards' no-direct-edits rule untouched.
- **All four verdicts expressible** — `SKILL.md:120-121` plus
  `item-review.md:58-60`, which gives a phrasing for each of the four.
- **Ambiguity costs one question, not a guess** — `SKILL.md:121-122`,
  `item-review.md:63-66` and `:70-72`.

## Whole-tree search (`rg -U`, multiline)

Patterns: `(a)pprove`, `(r)evise`, `(k)ill`, `(s)kip`,
`approve.*revise.*kill.*skip`, `Verdict?`, `verdict prompt`, `verdict shortcut`;
also `verdict` across `docs/ tests/ CLAUDE.md plugin/` and `proof` across
`docs/` and `plugin/`.

**Live sites — all fixed:**

| Site | Disposition |
|---|---|
| `plugin/skills/proof/SKILL.md:115` | the menu itself — replaced |
| `plugin/skills/proof/SKILL.md:124-130` (old) | letter shortcuts in the verdict list — dropped |
| `plugin/skills/proof/SKILL.md:132-134` (old) | "recognized verdict shortcut" — reworded |
| `plugin/skills/proof/SKILL.md:144-146` (old) | "Returns to verdict prompt" — reworded |
| `plugin/skills/proof/references/item-review.md:57` (old) | "user's stated fix" — reworded |
| `plugin/skills/proof/references/item-review.md:94` (old) | "Re-enter verdict prompt" — reworded |

**Deliberate historical quotations, added by this change:**
`docs/references/agent-instructions.md:139` and the changelog entry both quote
the removed menu to say what was removed.

**Frozen artifacts under `plans/` — listed, not edited:**

- `plans/reports/interactive-review-supplementary-internal.md:282` (the menu) and
  `:348` ("isn't a recognized verdict shortcut")
- `plans/skill-reviews/reports/apply-review.md:173`
- `plans/skill-reviews/proof.md:27`
- `plans/skill-reviews/reports/verify-summary.md:290` — the pending-job line that
  generated this task
- `plans/provenance-enforcement-and-routing/outline.md:367`
- `plans/reports/interactive-review-supplementary-grounding.md:85` and
  `interactive-review-external-research.md:394` — mention the vocabulary, not the
  menu

**No test asserts the prompt.** `tests/` hits on "verdict" are all
`edify-review-range.sh` verdict lines, unrelated. `plugin/README.md:36` and every
caller (`design/SKILL.md`, `write-outline.md`, `write-design.md`,
`requirements/SKILL.md`, `runbook/SKILL.md`) describe `/proof` without naming
its prompt — no caller edit needed. `memory/` untouched.

## `verify-proof.md` findings

**Folded in (they touch the same section):** none outstanding — every
`open-mechanical` finding in that report (C2, M1, M2, M3, M4, M5, M6, m1–m6)
was already applied in the working tree before this change; I verified each
against the current files rather than trusting the report's status column. The
one item genuinely coupled to this change was not in the report:
`item-review.md` §Revisit's "Re-enter verdict prompt", which the removal of the
prompt made stale. Fixed.

**Left untouched — all three are `open-design` forks needing my human partner's
call, and none is in this change's blast radius:**

- **C1 (critical)** — terminal "apply" still has no corrector dispatch, `Agent`
  is still in `allowed-tools` (`SKILL.md:8`) with no dispatch in the body, and
  three callers still assert one (`design/SKILL.md:214-215`, `:232-233`,
  `write-outline.md:220-222`, `write-design.md:68-70`). Trigger disagreement
  (revise/kill vs apply) unchanged. Fork: implement the dispatch, or strip the
  claim from the callers.
- **M8 (major)** — `p:` semantics cited at `SKILL.md:162` and
  `item-review.md:115`, defined nowhere in the tree.
- **M9 (major)** — `agents/learnings.md` is still the write target
  (`SKILL.md:161`, `item-review.md:114`) with no absence handling for a
  consuming repo.

## Questions for my human partner, and the default I took

1. **Should D-78's conclusion widen from `AskUserQuestion` to bounded option
   lists generally?** The letter menu is not that tool, but it is exactly the
   defect D-78's argument names. **Default taken: no.** I added a paragraph to
   D-78's node body recording `proof`'s case and left the conclusion line alone,
   so `docs/decisions.md` needed no edit. Widening would reach every skill in the
   plugin and is a scope call, not an implementation detail; the node and the
   changelog entry both record it as open.
2. **The outline was not run through `/proof`,** which the Simple route calls
   for between generating the outline and routing to `/build`. **Default taken:
   skipped** — there is no interactive user in this dispatch, and `/proof`
   without one is a no-op that would have produced a fabricated approval. The
   outline is on disk and reviewable.
3. **Nothing was committed.** Changes are in the working tree as instructed.

## Side effect worth naming

`just format` reflowed
`docs/changelog/2026-09-20-route-asks-whether-work-needs-runbook.md`, an
untracked file belonging to the concurrent changelog-split work. I did not
revert it — `just format` is the project recipe and the reflow is what the gate
expects — but it is a change to another agent's in-flight file, not mine.

## `just precommit` — full output, exit 0

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 348/349 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/requirements/SKILL.md: 354 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 277 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
# design links
design-links: 86 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
=== PRECOMMIT EXIT: 0 ===
```

Every `oversized-file` line is a pre-existing allowlisted ceiling, reported by
design and not failing the run. `plugin/skills/proof/SKILL.md` is **not** among
them: it is at 199 lines against the 200-line `SKILL.md` cap, with no allowlist
entry, so no ceiling was raised.
