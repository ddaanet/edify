# Item 3.6 — README names its optional plugins

- Requirements: C-2 (leg-4 open item 6, ruled into scope)
- Target: `plugin/README.md`, a new `## Optional plugins` section between
  `## Scripts` and `## Recipes`
- Finding (`plans/review-fixes-2/reports/build-leg4.md` §Open items, item 6):
  `plugin/README.md` named neither `plugin-dev` nor `craft` as optional. Only
  `sandbox-lies` was named as optional, inside the `verify-step.sh` bullet.

## Before

No section named optional plugins. The `## Scripts` section ended at the
`exempt-paths.sh` bullet and `## Recipes` followed directly:

```markdown
- `exempt-paths.sh` — sourced by the other two, never run: the one definition of
  the three paths dirty by convention (`memory`, `.claude/handoff-*.md`,
  `inbox/*.md`), which the gate tolerates and the changed-files list drops.

## Recipes
```

## After

The text as committed, after the formatter (rumdl) ran:

```markdown
- `exempt-paths.sh` — sourced by the other two, never run: the one definition of
  the three paths dirty by convention (`memory`, `.claude/handoff-*.md`,
  `inbox/*.md`), which the gate tolerates and the changed-files list drops.

## Optional plugins

Edify depends on none of these plugins. Each entry says what is lost without it:

- `plugin-dev` — without it, the review gate's skill-definition row (routing
  table in `fragments/review-requirement.md`) falls back to `edify:corrector`,
  and the agent-definition row loses its criteria source — review against the
  agent definitions already in `agents/` instead.
- `craft` — without it, the design-graph row keeps `edify:corrector` but loses
  its criteria source.
- `sandbox-lies` — what is lost without it is stated in the `verify-step.sh`
  bullet under Scripts.

## Recipes
```

## Contract

- **One place names all three.** `## Optional plugins` lists `plugin-dev`,
  `craft` and `sandbox-lies`, and each entry says what is lost without that
  plugin.
- **The `plugin-dev` and `craft` consequences are worded as the fragment
  states them.** `plugin/fragments/review-requirement.md` §"When plugin-dev
  or craft is not installed" reads:

  > without `plugin-dev`, the skill-definition row falls back to
  > `edify:corrector`, and the agent-definition row loses its criteria source
  > — review against the agent definitions already in `plugin/agents/`
  > instead. Without `craft`, the design-graph row keeps `edify:corrector` but
  > loses its criteria source.

  How the README maps onto it:
  - The row names (skill-definition, agent-definition, design-graph), the
    fallback to `edify:corrector`, "loses its criteria source", the
    `plugin/agents/` instruction and "keeps `edify:corrector`" are carried
    over word for word.
  - "the review gate's" and the parenthetical "(routing table in
    `fragments/review-requirement.md`)" are added to name the table the rows
    belong to. The contract calls it "the review gate's skill row", and
    `plugin/skills/build/references/finishing.md` §1 routes the review gate
    through that fragment. They add no claim.
  - Path base: the fragment's `plugin/agents/` became `agents/`, the README's
    plugin-relative convention (its Agents section says "Subagent definitions
    in `agents/`"). The consequence is unchanged.
  - The intro sentence "Edify depends on none of these plugins" restates the
    fragment's "not an edify dependency" so that it covers all three plugins.
    It does not repeat the fragment's "separate marketplace plugin", because
    the fragment says that of `plugin-dev` and `craft` only, and nothing here
    states it for `sandbox-lies`.
  - The fragment's routing instruction ("check availability before routing,
    and note the fallback in the review report") is for the reviewer
    dispatcher and is not carried into the README.
- **The `sandbox-lies` consequence is pointed at, not restated.** Its entry
  points at the `verify-step.sh` bullet under Scripts. That bullet is
  unchanged: it still states that without the plugin no listing is annotated,
  so the re-run never fires, and a masked listing reads as dirt.
- `plugin/README.md` has no entry in `scripts/check_line_limits.allow`; it
  went from 105 to 118 lines.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, run in the
foreground from the repo root.

The first run failed at the rumdl check: it reflowed the intro sentence's two
lines into one line of exactly 80 columns. That change was applied by hand to
`plugin/README.md`. The second run ended `✓ Precommit OK`. Checks that ran:

- version consistency: `Version consistent: 0.3.0`
- tests: `Tests cached (inputs unchanged)`
- rumdl: passed (no diff and no section output on the second run)
- line limits: passed; it listed the three allowlisted corrector-family files
  (`corrector.md` 682, `outline-corrector.md` 450, `design-corrector.md` 460),
  which this item does not touch
- design links: 94 decisions indexed, defined once, conclusions match, 9 nodes
  present

After the run, `git status --porcelain` showed `plugin/README.md` modified
and the two untracked `inbox/brief-*.md` files only.
