## Brief: dispatch model precedence — test-driver sonnet, prose opus

2026-09-07

Raised from a live `/orchestrate` run in the gitlore repository, over
`plans/index-edit-propagation/runbook.md`. A gitlore-side stopgap is in place
and must be removed when this lands — see *Stopgap to remove*.

### Decisions

These two are my human partner's, stated directly. They are settled input, not
proposals:

- **A `edify:test-driver` dispatch runs sonnet**, in both RED and GREEN mode.
- **A dispatch whose deliverable is prose runs opus** — design documents,
  decision nodes, changelog entries, skills, fragments, agent definitions.

Both **outrank a runbook item's own `Model:` line**. Reviewers are untouched:
`edify:corrector` was already opus and stays there, so D-32 is unaffected.

### The actual defect is precedence, not the defaults

`plugin/fragments/delegation.md:14` already says `artisan` and `test-driver`
dispatches run sonnet. The default is correct today. What defeats it is the
third rule on the same list, `plugin/fragments/delegation.md:18` — "a `Model:`
line on the runbook item overrides both" — restated in
`plugin/skills/orchestrate/references/dispatch-composition.md` §Model
assignment as "The three rules are exhaustive and strictly ordered: a `Model:`
line wins".

`/runbook` is what puts the wrong value there. The item shape in
`plugin/skills/runbook/references/runbook-format.md:14-19` carries `Model:
opus` in its own worked example, and the gitlore runbook duly assigned `Model:
opus` to all three of its tdd items. Every test-driver dispatch in that run was
therefore headed for opus while the type default said sonnet.

So the fix has two halves, and the second is the one that stops it recurring:

1. Make the two rules above outrank `Model:`, in both files that state the
   ordering.
2. Stop `/runbook` emitting a blanket `Model:` on tdd items, and change the
   format doc's example, which is where the habit is learned.

### D-42 needs generalizing at the same time

D-42 (`docs/design.md`) enumerates edify's own paths: `plugin/skills/`,
`plugin/fragments/`, `plugin/agents/`, `docs/design.md`. That list does not
reach a consumer repository's prose. The gitlore runbook's Item 4.3 writes a
changelog entry and a summary bullet under `docs/`, and was assigned `Model:
sonnet` — no path in D-42's list matches, so nothing corrected it.

State the override by **artifact kind**, prose consumed by a reader or an LLM,
with the current path list as examples rather than as the definition.

### Constraints

- The ordering is stated in two places that must not drift:
  `plugin/fragments/delegation.md:13-19` and
  `plugin/skills/orchestrate/references/dispatch-composition.md` §Model
  assignment. `plugin/skills/inline/SKILL.md` references model assignment too;
  check whether it restates the ordering or defers.
- D-32 and D-42 are both grounded in recorded experiments. Neither conclusion
  is being challenged — only D-42's scope, and the precedence that sits above
  both.
- `docs/design.md` and `docs/changelog.md` need the new decision and its entry,
  per edify's own six-section living-doc structure.

### Rejected approaches

- **Leaving it to the runbook author.** A `Model:` line is written at planning
  time by a skill that does not know which agent type the orchestrator will
  dispatch, so it cannot get this right by construction. That is why the rule
  belongs above it rather than inside it.
- **Fixing only the type default.** The default was already correct. A change
  there would have looked right and changed nothing.

### Open question for the implementing session

Whether `Model:` retains force at all once these two rules outrank it, or
whether it survives only for `artisan` and `corrector` dispatches on
non-prose targets. My human partner settled the two rules, not this. Surface
it before writing code.

### Stopgap to remove on delivery

The rule was written into the shared ddaanet conventions file as a stopgap:
`memory/ddaanet/shared-claude.md`, the **Dispatch** section, the sentence
beginning "Two dispatches are fixed regardless". That file is the always-loaded
tier shared by every mounting repository, edify included, so the stopgap is
already visible from edify itself.

Delete that sentence when this lands. It is a duplicate of a rule the tooling
will then enforce, and a convention line is paid for by every session in every
ddaanet repo. The edit must be made from a session whose working directory is
the repo that owns the memory mount — not from edify.
