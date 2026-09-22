# Item Review Reference

Detailed patterns for item detection, granularity, accumulation, and
presentation. Core loop mechanics are in SKILL.md — this file provides the
detection and format specifications.

## Granularity Detection

Parse artifact structure to identify reviewable items. Detection is automatic
based on artifact type:

| Artifact type | Pattern | Item granularity |
|--------------|---------|-----------------|
| requirements.md | `**FR-N:**` / `**NFR-N:**` / `**C-N:**` | Individual requirement/constraint |
| outline.md | `### D-N:` decision headings or `## Section` headings | Decision or section |
| design.md | `## Section` headings | Design section |
| runbook.md | Phase/item markers (`## Phase`, `Item N.M:`) | Individual item |
| Source files | Function/class definitions | Function or class |
| Diff output | Hunk markers (`@@`) | Individual hunk |

**Fallback:** No recognized pattern detected → artifact is one item. Loop runs
once. Orientation shows "1 item."

## Hierarchical Splitting

Large items auto-split into sub-items. No metric-based threshold —
judgment-based indicators:

- **Multiple independent concerns:** Item addresses 2+ unrelated topics (working
  memory overload — Cowan's ~4 concurrent items limit)
- **Visual context loss:** Item requires scrolling past a single screen of
  content
- **Internal structure:** Item contains sub-headings, enumerated sub-items, or
  other markers suggesting natural decomposition points

When splitting: present parent item title, then sub-items as "Item N.1 of N.K",
"Item N.2 of N.K". Sub-items inherit the parent's position in the linear order.

## Verdict Capture

The verdict is proposed, never polled for. Present the item, then say in plain
prose which verdict it deserves and why — "reads right to me, approving unless
you object", or "this overlaps item 4; I'd kill it and absorb the example
there". The four verdicts are the vocabulary for *recording* a disposition, not
a menu offered to the user: an option list bounds what they can say, and the
reply it invites is one character rather than a judgement.

**A proposed revision shows the amended item.** Write the item out as it would
read after the fix, so the reply lands on concrete wording rather than on a
request to produce some. When the reply accepts it, the shown text is what the
verdict records.

**Mapping a free-form reply.** The reply is prose. Read it for the disposition
it settles:

- Agreement with the proposal ("yes", "sure", "next") — record the proposed
  verdict.
- A different disposition, named or described — record that one instead. All
  four stay reachable whatever was proposed: "leave it as is", "change X to Y",
  "drop this one", "park it for now".
- An edit to a proposed revision — record the revision as the reply amends it,
  not as first shown.
- Nothing that settles a disposition — ask one clarifying question naming the
  readings the reply could bear, then read the answer. Never infer a verdict
  from a reply that does not carry one, and never present the next item until
  this one's verdict is recorded.
- Substantive feedback that is not a disposition — the discussion sub-loop in
  SKILL.md, which ends by proposing a verdict again.

**One question, not a sequence.** The clarifying question is a single turn. If
its answer still settles nothing, the input is discussion — enter the sub-loop
rather than asking again.

## Accumulation Format

Verdicts accumulate in-memory during iteration. The verdict list is the
structured input for batch-apply — the agent works from this list, not from
memory of the discussion.

```
- V-1: [item identifier] — approve
- V-2: [item identifier] — revise: "[the settled fix]"
- V-3: [item identifier] — kill (delete only)
- V-4: [item identifier] — kill (absorb → plans/foo/requirements.md)
- V-5: [item identifier] — skip
```

**Item identifier:** Use the item's title or heading text (e.g., "FR-3: Per-item
recall pass", "D-1: Verdict Vocabulary"). Must be unambiguous within the
artifact.

**Revise detail:** Capture the settled fix verbatim — the amended item the reply
accepted, or the user's own wording where they supplied it. This is the edit
specification for batch-apply; the discussion sub-loop may refine it before the
verdict is recorded.

**Kill sub-actions (planning artifacts only):** Per verdict semantics in
SKILL.md.

## Batch-Apply Execution

On terminal action "apply" after user confirms the verdict summary, apply each
accumulated verdict per §Verdicts in SKILL.md — approve and skip need no edit,
revise applies the stated fix, kill deletes or absorbs.

For multi-file composites (glob-matched artifacts), apply edits per-file
independently.

## Cross-Item Outputs

During iteration, normal loop actions produce immediate side effects (distinct
from verdict application which is batched):

- **learn** — appended to `agents/learnings.md` immediately
- **pending** — captured for handoff via `p:` semantics immediately
- **brief** — context transferred to a follow-up task immediately

These are listed in the verdict summary under "Cross-item outputs" so the user
sees the full picture before confirming apply.

## Revisit

After completing iteration through all items, user can revisit any
previously-reviewed item:

- Identification is flexible: by number ("revisit 3"), by title ("revisit
  FR-3"), or by content description
- Agent matches semantically — no exact-match requirement
- Propose a verdict afresh for the identified item
- New verdict replaces previous in the accumulation list
- Returns to post-iteration state (not back into the linear sequence)
