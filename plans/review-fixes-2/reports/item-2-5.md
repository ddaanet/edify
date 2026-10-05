# Item 2.5 — tdd-auditor reads the hosting file

Requirements: M5. Target: `plugin/agents/tdd-auditor.md`. Wording for the
hosting file follows `plugin/skills/build/references/tdd-slice.md` §After the
slice step 3 (Item 2.4): "the file hosting the item — `runbook.md`, or the
`outline.md` or `design.md` routed to `/build`".

## Edits

The four places the item enumerates:

1. **§Inputs, first bullet** — `Runbook: plans/<job>/runbook.md` becomes the
   hosting file: the plan file carrying the tdd items, `runbook.md` or the
   `outline.md` or `design.md` routed to `/build`, with its git history. List
   revisions are made in it and appear as orchestrator commits touching that
   file alone. The bullet also says how the auditor finds it (see Seam below):
   the first of `plans/<job>/runbook.md`, `design.md` and `outline.md` that
   exists, in the order `/build` §1 loads the work.
2. **§Per-Slice Checks, check 2, the list-revision paragraph** — the
   list-revision commit "touches the hosting file alone"; the violation clause
   reads "neither a report nor a list revision touching the hosting file alone
   accounts for".
3. **§Cross-Slice Checks, List revisions recorded** — "the runbook's git
   history" becomes "the hosting file's git history".
4. **§Report template** — the `**Runbook:** plans/<job>/runbook.md` line
   becomes `**Hosting file:** plans/<job>/<runbook.md, design.md or
   outline.md>`; the `## List Revisions` hint reads "from the hosting file's
   history" instead of "from runbook.md history".

Further places the agent treated the runbook as the slices' host, taken under
the item's "every place":

5. **Opening paragraph (body line 31–34)** — "a runbook's tdd items" becomes "a
   plan's tdd items", and "the `runbook.md` diff records that divergence"
   becomes "the hosting file's diff".
6. **Frontmatter `description`** — "after a runbook's tdd items complete"
   becomes "after a plan's tdd items complete", and the first example's
   context "completed a runbook with tdd items" becomes "completed a plan with
   tdd items".
7. **§Tool Usage** — "**Read** for runbook and reports" becomes "for the
   hosting file and reports".

No `KD-N` citation appears in the agent text. `just format` reflowed the
edited paragraphs; the file is 226 lines after it.

## Seam (reported, not changed)

The auditor is not told which file hosts the slices.
`plugin/skills/build/references/finishing.md` §3 step 2 dispatches
`tdd-audit` naming only the slice reports, and
`plugin/skills/build/references/dispatch-composition.md` §Prompt contents
item 2 states the `tdd-audit` dispatch's inputs are "the slice reports and the
commits that add them, and nothing else" — no design or outline path. The
agent text therefore carries its own determination rule (edit 1), so it needs
no change elsewhere to work.

Two residuals for the orchestrator to weigh:

- `plugin/skills/build/SKILL.md` §1 option 2 names `design.md` and
  `outline.md` together ("`design.md` or `outline.md`") without ordering them.
  The agent's rule takes `design.md` first, the textual order there. A job
  directory holding both with no runbook would make the rule's choice a
  convention, not a match to `/build`. No current `plans/*/` directory holds
  both (checked).
- `dispatch-composition.md`'s "nothing else" for `tdd-audit` already sat
  beside the agent reading `runbook.md` history before this item; this item
  keeps that read, retargeted. If the dispatch should name the hosting file
  instead of the agent deriving it, that is an edit to `finishing.md` §3 step 2
  and `dispatch-composition.md` item 2, both out of this item's scope.

## Verification

`just precommit` green (foreground, full output read).
