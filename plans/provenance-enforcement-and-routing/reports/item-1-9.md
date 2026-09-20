# Item 1.9 — the remaining "per X" pointers made imperative Reads

Requirements: M-6. Job: `plans/provenance-enforcement-and-routing/`.

## Before-search hit list

`rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/` — ten hits across seven
files (`tdd-slice.md:4` already fixed by Item 1.7 and no longer matching):

| Site | Target | Class |
|---|---|---|
| `plugin/fragments/delegation.md:33` | `dispatch-composition.md` | must-open |
| `plugin/skills/runbook/SKILL.md:36-37` | `references/runbook-format.md` | must-open |
| `plugin/skills/runbook/SKILL.md:78` | `references/runbook-format.md` | must-open |
| `plugin/skills/review/SKILL.md:207` | `plugin/fragments/review-requirement.md` | must-open |
| `plugin/skills/build/references/phase-boundary.md:14-15` | `dispatch-composition.md` | must-open |
| `plugin/skills/build/references/finishing.md:10-11` | `plugin/fragments/review-requirement.md` | must-open |
| `plugin/skills/build/references/finishing.md:17-18` | `review-dispatch-template.md` | must-open |
| `plugin/skills/build/references/finishing.md:35-36` | `docs/design.md` §6.4 D-26 | citation |
| `plugin/skills/build/references/review-dispatch-template.md:77` | `docs/design.md` §6.4 D-26 | citation |

`plugin/agents/refactor.md:59` ("per the prompt") does not match the pattern —
no `.md` target — and needed no edit, as the review already recorded.

## Per-site before/after

**`plugin/fragments/delegation.md:33`** — path left exactly as found
(repo-relative `plugin/skills/build/references/…`): a fragment has no
announced base directory, so its path form belongs to the repo-relative job
(outline §Scope). Wording only:

- before: `The dispatcher composes each prompt per \`plugin/skills/build/references/dispatch-composition.md\`: item text inline, …`
- after: `Read \`plugin/skills/build/references/dispatch-composition.md\` and compose each prompt by it: item text inline, …`

**`plugin/skills/runbook/SKILL.md:36-37`** — skill-relative already; kept.

- before: `… concrete action against a named target. Both per \`references/runbook-format.md\`.`
- after: `… concrete action against a named target. Read \`references/runbook-format.md\` and write both by it.`

**`plugin/skills/runbook/SKILL.md:78`**

- before: `Write \`plans/<job>/runbook.md\` per \`references/runbook-format.md\`:`
- after: `Read \`references/runbook-format.md\` and write \`plans/<job>/runbook.md\` by it:`

**`plugin/skills/review/SKILL.md:207`** — repo-relative → skill-relative.

- before: `When delegating to corrector, include scope context per \`plugin/fragments/review-requirement.md\`:`
- after: `When delegating to corrector, Read \`../../fragments/review-requirement.md\` and include the scope context it specifies:`

**`plugin/skills/build/references/phase-boundary.md:14-15`** — sibling bare
form the file already uses, kept.

- before: `Dispatch \`edify:corrector\` (checkpoint form, composed per \`dispatch-composition.md\`): scope IN/OUT …`
- after: `Read \`dispatch-composition.md\` and compose by it a checkpoint-form dispatch of \`edify:corrector\`: scope IN/OUT …`

**`plugin/skills/build/references/finishing.md:10-11`** — repo-relative →
base-relative (reasoning below).

- before: `Route changed files to the appropriate reviewer per \`plugin/fragments/review-requirement.md\` routing table.`
- after: `Read \`../../fragments/review-requirement.md\` and route changed files to the appropriate reviewer by its routing table.`

**`plugin/skills/build/references/finishing.md:17-18`** — sibling bare form
the file already uses, kept.

- before: `4. Dispatch each group to its reviewer, structuring the prompt per \`review-dispatch-template.md\``
- after: `4. Read \`review-dispatch-template.md\` and dispatch each group to its reviewer, structuring the prompt by it`

**`plugin/skills/build/references/finishing.md:35-36`** — citation, reworded
without "per", not made a Read.

- before: `They route by artifact per \`docs/design.md\` §6.4 D-26: …`
- after: `They route by artifact, as \`docs/design.md\` §6.4 D-26 records: …`

**`plugin/skills/build/references/review-dispatch-template.md:77`** — citation.

- before: `Planning artifacts route by artifact per \`docs/design.md\` §6.4 D-26:`
- after: `Planning artifacts route by artifact, as \`docs/design.md\` §6.4 D-26 records:`

## Path-form reasoning for `finishing.md`

`finishing.md` lives at `plugin/skills/build/references/finishing.md`. What
resolves at read time is the base directory the Skill tool announces for the
`build` skill — `plugin/skills/build/` — not the directory the file itself
sits in. From that base, `plugin/fragments/` is `../../fragments/`
(`build` → `skills` → `plugin`). So line 10 got the **base-relative** form
`../../fragments/review-requirement.md`, not the file-relative
`../../../fragments/…` the outline item first wrote.

The two sibling pointers in the same file (`review-dispatch-template.md`,
line 17; and `dispatch-composition.md` in `phase-boundary.md`) were left in
the **bare** form those files already use. That is inconsistent with the
base-relative rule — from base `build/` the sibling is
`references/review-dispatch-template.md` — but the item's instruction was to
keep the form the file already uses, and `build/SKILL.md:122` vs
`tdd-slice.md:5` show both forms in live use today. Flagging it: which of the
two forms a `references/` node should use for a sibling is unresolved in the
tree and not settled here.

`review/SKILL.md:211` still carries the repo-relative
`plugin/fragments/review-requirement.md` in a "See … for full template"
sentence. It is not a "per" pointer, this item did not write it, and the 34
existing repo-relative references are explicitly out of scope (§Scope).

## After-search hit list

Four searches, all zero hits:

```
rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/        → 0
rg -n -U    '\bper\s+`?[\w/.-]+\.md' plugin/ docs/        → 0
rg -n -U -i '\bper\s*\n\s*`'         plugin/ docs/        → 0
rg -n    -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/        → 0   (single-line control)
```

Every before-hit is classified: seven **fixed-imperative** (of which
`delegation.md:33` is additionally **deferred-path-form** — wording fixed,
path left repo-relative for the §Scope job), two **citation-reworded**.
`refactor.md:59` is **left-with-reason** (not a file pointer; never matched
the pattern). Zero unclassified.

### `-U` confirmation

Run against the pre-edit content of the seven files (extracted from HEAD), the
single-line search returned 4 hits and the `-U` search returned 9. The five
`-U` caught and the single-line form missed are exactly the wrapped ones:
`finishing.md:10-11`, `:17-18`, `:35-36`, `runbook/SKILL.md:36-37`,
`phase-boundary.md:14-15` — the same five the review's single-line search
missed. Confirmed.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, full output:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

Subject: `docs: Item 1.9 — make the remaining "per X" pointers imperative Reads`
