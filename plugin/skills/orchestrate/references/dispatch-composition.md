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
   subject to use. A slice commit's subject is `<type>: Item N.M/k —
   <title>`; `<type>` is the executor's choice — `feat`, `fix`, `docs`,
   `perf`, `test`, `build` and `chore` are all legitimate, since a slice may
   pin an error path or change a build surface rather than add a feature.
   The `commit-msg` hook rewrites the prefix to an emoji before the commit is
   written, so no check may key on the type; the `Item N.M/k` marker is the
   only part of a subject anything may match. Overrides: a RED dispatch
   commits nothing and stops after the red run; a review dispatch commits
   nothing either — the orchestrator commits the fixes a corrector applied.
5. **Report path** — `plans/<job>/reports/<dispatch name>.md`, the `name`
   from §Naming and nothing else. This is the only rule for report paths:
   the prompt assigns the path and the agent writes exactly there, whatever
   default its own definition carries. Per-dispatch names are what keep a
   slice's test review and code review from overwriting each other, and what
   let `tdd-auditor` find them. Return contract: the report path on success,
   or `blocked: <reason>` — except `edify:refactor`, whose own protocol
   returns `success` / `escalated: <reason>` / `error: <reason>` and still
   writes its report at the assigned path.
6. **Mode**, for `edify:test-driver` only: `RED` or `GREEN`, named
   explicitly — the agent refuses a prompt that names neither.

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

The three rules are exhaustive and strictly ordered: a `Model:` line wins;
absent one, the artifact-type override wins wherever the dispatch edits those
paths; absent both, the type default applies. No other consideration changes
the model.

## Naming and resumption

Give every dispatch a `name`: `item-N-M` for a general item,
`item-N-M-s<k>-red` / `-test-review` / `-green` / `-code-review` for slice
dispatches, `item-N-M-s<k>-refactor` for a refactor the code review flagged
(the opus re-dispatch reuses the name), `phase-P-corrector` for checkpoints,
`final-review` for a
single-phase run's closing corrector, `tdd-audit` for the auditor. Resumption
is `SendMessage` to that name; an unnamed agent cannot be resumed.

A child's own reply is the only authoritative result for its task. A late
task-notification on an already-reported task id may be answering something
else — never treat one as the report.

## Agent behaviour contract

The dispatched agent follows `plugin/fragments/delegation.md`: it reports to
a file and returns only the filepath or an error, resolves recall by
reading the artifact's listed files itself, and is resumed at most once
before a fresh launch.
