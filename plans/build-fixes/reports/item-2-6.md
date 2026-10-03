# Item 2.6 — `plugin/skills/build/references/dispatch-composition.md`

Requirements: (c), m8, m10.

## Changes per bullet

- **§Naming and resumption ((c), KD-5).** The one-sentence name list became a
  bulleted list. `review-<group>` now lists KD-5's four fixed slugs, each with
  its row:
  - `review-code` — code and tests, and the default for unnamed kinds;
  - `review-skill` — skill definitions plus a skill's `references/` nodes and
    any shared instruction file outside a skill;
  - `review-agent` — agent definitions;
  - `review-design` — the `docs/` design graph, not `plans/<job>/design.md`.

  The class rule follows: a file kind always goes into an existing row, never a
  new group, and planning artifacts route by artifact (`finishing.md` §1). This
  is the one statement `finishing.md` §1 step 2 points at. The shipped text
  names the class, not edify's `plugin/fragments/` directory (KD-5).
- **`item-N-M` for §4.1's self-review (Item 2.1 cross-reference).** The bullet
  now says an item executed in session leaves the name free. The name then
  covers that item's review: the corrector §4.1 dispatches, or the self-review
  report the session writes at that name's path. That report is what the resume
  inventory (`escalation.md` §Resuming) finds.
- **`final-review` (m10).** "A single-phase run's closing corrector" became
  `finishing.md` §3.1's closing corrector. It is dispatched only where the
  review was skipped or routing left a group of changed files unreviewed — the
  two triggers §3.1 names.
- **§Prompt contents item 4 (KD-8).** The subjects are now
  `<type>: <job> Item N.M — <title>` for an item and
  `<type>: <job> Item N.M/k — <title>` for a slice. "The `Item N.M/k` marker is
  the only part of a subject anything may match" became: `<job> Item N.M[/k]`
  is a label only, for a human reading `git log` and to keep two jobs' commits
  apart. Nothing mechanical keys on any part of a subject; resume, inventory
  and base read report history. The hook sentence keeps only the rewrite.
- **§Prompt contents item 5 (m8).** Added: a part ending in neither `CONTINUED`
  nor `END OF REPORT` was truncated, so the reviewer is resumed by name for the
  rest of that part before the next is asked for.

## Judgement calls for review

- **"Nothing mechanical".** KD-8's own word. `tdd-auditor` still reads the
  `Item N.M/k` marker to recognise a slice's two commits. That is an agent's
  reading, not a mechanical key, so the sentence stays true as written, and the
  auditor's text is Item 2.10's.
- **Item subject added to item 4.** The bullet names only the slice marker. The
  item form `<type>: <job> Item N.M — <title>` is added beside it because item
  4 sets the done criteria for every committing dispatch, `edify:artisan` on a
  general item included, and `SKILL.md` §4.1 already uses that form.
- **KD-5's design-row reviewer is not stated here.** `review-design` is
  reviewed by `edify:corrector` with `craft:design-doc-writing`, but that is
  routing, which `review-requirement.md`'s table owns (Item 2.9). This node
  names and classes; it does not route.

## Cross-references left for later items

- `plugin/agents/tdd-auditor.md:96` ("two commits bearing the `Item N.M/k`
  marker") and §Inputs: KD-8's `<job> Item N.M/k` form, Item 2.10 or 2.13.
- `docs/design.md:232-240` still records `<type>: Item N.M/k — <title>`, and
  says the marker "is the only thing `tdd-auditor` may match in a subject". No
  item names `docs/design.md` (Item 2.14 names `pipeline-contracts.md` and
  `decisions.md`). Flagged so KD-8's record covers the hub conclusion too.
- `review-requirement.md` routing table: skill row covering `references/` nodes
  and shared instruction files, design row → the `docs/` graph by
  `edify:corrector`: Item 2.9.

## Verification

- `just format`, then `just precommit` green (version consistency, cached
  tests, line limits — only the three allowlisted correctors reported — and
  design links).
- Self-review of the uncommitted diff against Item 2.6's bullets, KD-5 and
  KD-8, and against `finishing.md` §1 step 2 and §3.1, `SKILL.md` §4.1 and
  `escalation.md` §Resuming step 1.
- `rg` over `plugin/` and `docs/` for the old "only part of a subject" and
  "single-phase run" wording: no hit left in `plugin/skills/`. The two hits
  outside it are listed above.
- 117 lines before, 140 after (`wc -l`, after `rumdl fmt`).
