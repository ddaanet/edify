# Item 1.6 — `/design` routes Moderate non-prose by the node

Requirements: M-3, m-2. Spec: outline KD-4, KD-5. Scope: `plugin/skills/design/SKILL.md` only.

## Step 1 — `description:` frontmatter

Verbatim, lines 3-7:

```yaml
description: >-
  Triage complexity and design implementation approach. Triggers on /design,
  architecture or implementation planning requests, or tasks needing
  complexity assessment. Triages simple/moderate/complex, produces design
  documents for complex jobs, routes by whether the work needs a runbook.
```

Only the final clause changed ("routes moderate to /runbook" → "routes by
whether the work needs a runbook"). Same line count, one character shorter
than the original tail line plus two — no wrap change.

## Step 2 — `:19` Downstream Consumers, Execution bullet

Fourth caller added:

> - **Execution:** `/build` when the work needs no runbook
>   (`references/route-to-execution.md`, reached from both of
>   `references/write-outline.md`'s sufficiency gates, from
>   `references/write-design.md`'s C.5, and from Phase 0's Moderate non-prose
>   route). Handles the execution lifecycle: entry gate, item walk, review
>   gate, triage feedback, deliverable-review handoff.

## Step 3 — Phase 0, Moderate non-prose route

Lead-in and steps 2 and 4 changed; steps 1 and 3 untouched. Now at `:137-141`:

> - **Moderate, non-prose** (all other artifact destinations) **→** ground the
>   brief against the codebase, then plan and route:
>   1. **Code reading:** …
>   2. **Generate** … Where the outline carries a behavioural change, Read
>      `../runbook/references/runbook-format.md` and write that change as an
>      item in its shape — an item carrying `Slices:` carries nothing else to
>      execute, and general work goes in its own item.
>   3. **Proof:** …
>   4. **Route (after /proof approval):** Read `references/route-to-execution.md`
>      and route by it. A failed precondition returns to step 2.

`/runbook plans/<job>` is no longer named here; the node's Terminal action
names the command. The "returns to step 2" sentence is the caller side of the
node's precondition-failed return point (KD-5) — step 2 is this route's own
generate step.

## Step 4 — KD-4 generation sentence on both `/build`-bound routes

Identical sentence appended to the generate step of each route. On the
Simple / Moderate-agentic-prose route (`:133`, step 3, after the
what-changes sentence) and on the Moderate non-prose route (`:139`, step 2,
above). Verbatim:

> Where the outline carries a behavioural change, Read
> `../runbook/references/runbook-format.md` and write that change as an item
> in its shape — an item carrying `Slices:` carries nothing else to execute,
> and general work goes in its own item.

The format itself is not restated; the file is Read. Path is
skill-relative (`../runbook/references/…`), not repo-relative.

## Step 5 — §Routing out

Now `:168-176`:

> ## Routing out
>
> Each branch above stops there, naming its own next command or taking the
> terminal action `references/route-to-execution.md` names. There is no
> tail-call: `/design` states the command, the user or the session runs it.
>
> - Simple, Moderate agentic-prose → `/build plans/<job>`
> - Routed to `/build` by `references/route-to-execution.md` — reached from
>   both of `references/write-outline.md`'s sufficiency gates, from
>   `references/write-design.md`'s C.5, and from Phase 0's Moderate non-prose
>   route → `/build plans/<job>`
> - Routed to `/runbook` by that node → commit the artifact and stop; no next
>   command

The "Moderate non-prose → `/runbook plans/<job>`" bullet is deleted. The
singular "(B gate or C.5)" went with it — **m-2 closed**.

Beyond the item's five bullets, the §Routing out lead sentence was reworded:
"Each branch above names its own next command and stops there" was falsified
by KD-5, since the Moderate non-prose branch now defers the command to the
node (and the node's `/runbook` terminal action names no command at all).

## Step 6 — `runbook` grep disposition

`grep -n -i 'runbook' plugin/skills/design/SKILL.md`, post-edit, eight hits:

| Line | Text | Disposition |
|---|---|---|
| 7 | `description:` tail | **changed** — step 1 |
| 18 | Downstream Consumers, Planning bullet: `/runbook` — phases typed tdd or general | left — describes what `/runbook` consumes, asserts no route |
| 19 | Downstream Consumers, Execution bullet | **changed** — step 2 |
| 41 | Artifact check: `design.md` exists → route to `/runbook` | left — Phase 0 artifact resume path for a pre-existing design, not the Moderate non-prose route. KD-5 does not name it, and the item bars touching Phase A/B/C procedure beyond the routes named. Flagged as a possible follow-up: a pre-existing `design.md` bypasses the node, where a design written here reaches it at C.5 |
| 133 | Simple / Moderate-agentic-prose generate step, KD-4 sentence | **changed** — step 4 |
| 139 | Moderate non-prose generate step, KD-4 sentence | **changed** — steps 3, 4 |
| 163 | Author-Corrector Coupling table row `/runbook (runbook-format.md)` | left — coupling table, not a route |
| 176 | §Routing out third bullet | **changed** — step 5 |

The deleted `:141` `/runbook plans/<job>` and `:173` Moderate-non-prose bullet
no longer appear.

## Constraints

- No repo-relative `plugin/…` path written. `grep -n 'plugin/'` reports only
  the two pre-existing artifact-destination table rows (`:91`, `:92`), which
  are destination path categories rather than references to open — untouched.
- Sibling references written as `references/<file>.md`; the cross-skill one as
  `../runbook/references/runbook-format.md`.
- Phase A/B/C procedure untouched.
- File is 176 lines, unchanged from before the edits (the two KD-4 sentences
  and the widened caller lists extended existing long lines rather than adding
  any). Under the ~200-line `SKILL.md` cap.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, full output:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

Subject as landed (gitmoji hook rewrites the `docs:` prefix):
`📝 Item 1.6 — /design routes Moderate non-prose by the node`. Staged
together: `plugin/skills/design/SKILL.md` and this report. The hash is this
commit's own and so cannot be quoted inside it — `git log -1` on the subject
above resolves it; it was reported to the dispatching agent.
