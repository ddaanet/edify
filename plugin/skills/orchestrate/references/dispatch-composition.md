# Dispatch Prompt Composition

The single source for composing a delegation prompt from a runbook item (or
from an ad-hoc task in `/inline`'s delegated path). The dispatcher writes the
prompt itself, live — there are no prepared prompts to reuse.

## Prompt contents

Every dispatch prompt carries:

1. **Item id and text, verbatim** — including the `Interfaces:` blocks the
   item consumes and produces. For a tdd slice, the slice's own numbered
   entry with its test list, plus the item's `Interfaces:` block.
2. **Context by path, never by content:**
   - `Read plans/<job>/design.md` (or `outline.md`, whichever the plan has)
   - `Read plans/<job>/recall-artifact.md, then Read each file it lists`
3. **Scope:** IN — this item (or slice); OUT — the next items' targets,
   named explicitly so the executor does not wander into them.
4. **Done criteria:** `just precommit` green, clean tree, and the commit
   subject to use. (RED dispatches override this: no commit, stop after the
   red run.)
5. **Report path** under `plans/<job>/reports/` and the return contract:
   the report path on success, or `blocked: <reason>`.

When the design specifies explicit classifications or patterns, include them
LITERALLY — executors apply design rules, they do not invent alternatives.

## Model assignment

- **Type default:** `artisan` / `test-driver` → sonnet; `corrector` → opus —
  the reviewer runs a tier above the implementers (D-32).
- **Artifact-type override (D-42):** opus for any dispatch editing skills
  (`plugin/skills/`), fragments (`plugin/fragments/`), agent definitions
  (`plugin/agents/`), or the living design (`docs/design.md`) — prose
  instructions consumed by LLMs, where wording determines downstream agent
  behaviour. The dispatcher applies this override itself.
- **Per-item override:** a `Model:` line on the runbook item overrides both.

## Naming and resumption

Give every dispatch a `name`: `item-N-M` for a general item,
`item-N-M-s<k>-red` / `-test-review` / `-green` / `-code-review` for slice
dispatches, `phase-P-corrector` for checkpoints. Resumption is `SendMessage`
to that name — the `Agent` tool has no `resume` parameter, so an unnamed
agent cannot be resumed. Do not pass `max_turns`; the tool has no such
parameter and rejects unknown ones.

A child's own reply is the only authoritative result for its task. A late
task-notification on an already-reported task id may be answering something
else — never treat one as the report.

## Agent behaviour contract

The dispatched agent follows `plugin/fragments/delegation.md`: it reports to
a file and returns only the filepath or an error, resolves recall by
reading the artifact's listed files itself, and is resumed at most once
before a fresh launch.
