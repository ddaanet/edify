# Item 2.6 — dispatch-composition.md: resume by agent id, the skill row

Target: `plugin/skills/build/references/dispatch-composition.md`.
Requirements: m10, m11.

## Edits

### §Naming and resumption — `review-skill` bullet (m11)

Was: "skill definitions and the agent-instruction prose they load: a skill's
`references/` nodes and any shared instruction file a repo keeps outside a
skill".

Now, the canonical wording for the rule's three texts:

> `review-skill` — skill definitions and the agent-instruction prose they
> load, meaning their `references/` nodes and the shared instruction files a
> skill loads from outside itself. An instruction file no skill loads, such as
> `CLAUDE.md` or `.claude/rules/*.md`, matches no row and takes the
> `review-code` default;

Item 3.1 can copy the two sentences into D-93 verbatim (the bullet's trailing
`;` is list punctuation only).

### §Naming and resumption — resumption paragraph (m10)

Deleted "an unnamed agent cannot be resumed". Now:

> Resumption is `SendMessage` to the dispatch's name. An agent spawned unnamed
> is resumed by `SendMessage` to its agent id, as `review-requirement.md`
> §UNFIXABLE Detection Protocol step 4 does.

## Verification

- `just format` reflowed the bullet; file is 144 lines.
- `just precommit`: `Precommit OK` (version consistency, tests cached, line
  limits, design links). The three `oversized-file` lines it prints
  (`corrector.md`, `outline-corrector.md`, `design-corrector.md`) are files
  this item does not touch.

## Surfaces outside scope

- D-93 in `docs/references/build-run-state.md` lines 124-126 still carries the
  old skill-row wording ("any shared instruction file kept outside a skill");
  Item 3.1 owns it.
