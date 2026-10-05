# Item 2.7 — review-requirement.md: the skill row conforms

Target: `plugin/fragments/review-requirement.md`. Requirements: m11.

## Edits

### §Proportionality — reviewer routing table, skill row

Was: "Skill definitions, their `references/` nodes, and shared instruction
files kept outside a skill".

Now, the same words as `dispatch-composition.md` §Naming and resumption's
`review-skill` bullet:

> Skill definitions and the agent-instruction prose they load, meaning their
> `references/` nodes and the shared instruction files a skill loads from
> outside itself

### §Proportionality — new paragraph after the routing table

> An instruction file no skill loads, such as `CLAUDE.md` or
> `.claude/rules/*.md`, matches no row and takes the `review-code` default.
> `review-code` is `/build`'s dispatch name for the first row, and
> `plugin/skills/build/references/dispatch-composition.md` §Naming and
> resumption states this rule.

The first sentence is word for word the one in `dispatch-composition.md`. The
second exists because this fragment's table names reviewers, not dispatch
slugs, so `review-code` would otherwise be undefined here; it also points at
the rule's single statement.

### Not edited

§UNFIXABLE Detection Protocol step 4 is unchanged (ruled).

## Verification

- `just format`: file is 271 lines.
- `just precommit`: `Precommit OK` (version consistency, tests cached, line
  limits, design links). The three `oversized-file` lines it prints
  (`corrector.md`, `outline-corrector.md`, `design-corrector.md`) are files
  this item does not touch.

## Surfaces outside scope

- D-93 in `docs/references/build-run-state.md` still carries the old skill-row
  wording; Item 3.1 owns it.
