# Item 2.8 — delegation.md: resume by name or agent id

Target: `plugin/fragments/delegation.md`. Requirements: m10.

## Edits

### §Delegate Resume — first bullet

Was: "Give the agent an explicit `name` at spawn; resuming is `SendMessage` to
that name".

Now:

> Give the agent an explicit `name` at spawn; resuming is `SendMessage` to that
> name, or to the agent id where the agent was spawned unnamed

This agrees with `dispatch-composition.md` §Naming and resumption (Item 2.6)
and `review-requirement.md` §UNFIXABLE Detection Protocol step 4: a named
dispatch resumes by name, an unnamed one by agent id. The "spawn with a name"
instruction stays.

## Verification

- `just format`: no reflow beyond the edit; file is 128 lines.
- `just precommit`: `Precommit OK` (version consistency, tests cached, line
  limits, design links). The three `oversized-file` lines it prints
  (`corrector.md`, `outline-corrector.md`, `design-corrector.md`) are files
  this item does not touch.

## Surfaces outside scope

None found: a search of `plugin/`, `docs/`, `README.md` and `CLAUDE.md` for
"unnamed" and "cannot be resumed" finds no other surface.
