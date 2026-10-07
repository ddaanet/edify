# Dispatch Prompt Composition

The single source for composing a delegation prompt from a runbook item, or from
an ad-hoc task where the work has no runbook. The dispatcher writes the prompt
itself, live — there are no prepared prompts to reuse.

## Prompt contents

Every dispatch prompt carries:

1. **Item id and text, verbatim** — including the `Interfaces:` blocks the item
   consumes and produces. For a tdd slice, the slice's own numbered entry with
   its test list, plus the item's `Interfaces:` block.
2. **Context by path, never by content**, for any dispatch that executes or
   reviews the plan's work:
   - `Read plans/<job>/design.md` (or `outline.md`, whichever the plan has)
   - `Read plans/<job>/recall-artifact.md, then Read each file it lists`

   The `tdd-audit` dispatch is the exception: its inputs are the slice reports,
   the commits that add them, and the hosting file and its history, which the
   prompt names (`finishing.md` §3).
3. **Scope:** IN — this item (or slice); OUT — the next items' targets, named
   explicitly so the executor does not wander into them. For a GREEN dispatch,
   OUT also names the rest of the item's own contract: the `Interfaces:` block
   goes in for structure, and every part of it this slice's tests do not reach
   is out of scope for this dispatch. A GREEN that implements the whole item
   leaves the later slices unable to red.
4. **Done criteria:** `just precommit` green, clean tree, and the commit subject
   to use. An item commit's subject is `<type>: <job> Item N.M — <title>`, a
   slice commit's `<type>: <job> Item N.M/k — <title>`; `<type>` is the
   executor's choice — `feat`, `fix`, `docs`, `perf`, `test`, `build` and
   `chore` are all legitimate, since a slice may pin an error path or change a
   build surface rather than add a feature. The `commit-msg` hook rewrites the
   prefix to an emoji before the commit is written. `<job> Item N.M[/k]` is a
   label only, for a human reading `git log` and to keep two jobs' commits
   apart: nothing mechanical keys on any part of a subject, since resume,
   inventory and base all read report history. A committing dispatch stages the
   paths it names — its own report among them — and never `git add -A`, then
   commits with `git commit -- <paths>`, naming the paths it staged. Overrides:
   a RED dispatch commits nothing and stops after the red run; a review dispatch
   commits nothing either — the orchestrator commits the corrector's report,
   with the fixes it applied where there are any, in the same form.
5. **Report path** — `plans/<job>/reports/<dispatch name>.md`, the `name` from
   §Naming and resumption and nothing else. This is the only rule for report
   paths: the prompt assigns the path and the agent writes exactly there,
   whatever default its own definition carries. Per-dispatch names are what keep
   a slice's test review and code review from overwriting each other, and what
   let `tdd-auditor` find them. A report names no hash of the commit that
   carries it; whoever needs that commit resolves it with
   `git log --diff-filter=A` over the report's path. Return contract: the report
   path on success, or `blocked: <reason>`. UNFIXABLE is never a return: a
   reviewer marks an issue it cannot fix `UNFIXABLE` inside its report. Two
   exceptions to the contract: `edify:refactor`, whose own protocol returns
   `success` / `escalated: <reason>` / `error: <reason>` and still writes its
   report at the assigned path; and a report-only reviewer
   (`plugin-dev:skill-reviewer`), which returns its findings as text in parts
   and writes nothing — the dispatching session resumes it by name for the next
   part while a part ends `CONTINUED`, and writes the parts to the assigned path
   only once one ends `END OF REPORT` (`review-dispatch-template.md`
   §Report-only variant). A part ending in neither marker was truncated: resume
   the reviewer by name for the rest of that part before asking for the next.
6. **Mode**, for `edify:test-driver` only: `RED` or `GREEN`, named explicitly —
   the agent refuses a prompt that names neither.

When the design specifies explicit classifications or patterns, include them
LITERALLY — executors apply design rules, they do not invent alternatives.

## Model assignment

- **Type default:** `artisan` / `test-driver` → sonnet; `corrector` → opus — the
  reviewer runs a tier above the implementers (D-32).
- **Artifact-type override (D-42):** opus for any dispatch whose deliverable is
  **prose consumed by a reader or an LLM** — wording there determines downstream
  agent behaviour or a human's understanding, so the judgement is the work. The
  test is the artifact kind, not the path. In this repo that covers skills
  (`plugin/skills/`), fragments (`plugin/fragments/`), agent definitions
  (`plugin/agents/`), the living design (`docs/design.md`), changelog entries
  and decision nodes — but those are examples, not the definition: a consumer
  repository's `docs/` prose qualifies just as much, and no path list reaches
  it. The dispatcher applies this override itself.
- **Fixed assignments, overriding both:** a `test-driver` dispatch runs
  **sonnet** in RED and in GREEN; a dispatch whose deliverable is prose runs
  **opus**. These are not defaults — nothing overrides them.

The rules are exhaustive and strictly ordered: the two fixed assignments win;
absent either, the artifact-type override wins where the deliverable is prose;
absent all three, the type default applies. No other consideration changes the
model.

**A runbook item does not carry a model.** There is no `Model:` line to consult:
the field was removed because it is written at planning time, by a skill that
knows neither which agent type the dispatcher will pick nor what the work turns
out to involve. Where an item needs a stronger model than the rules give it, the
agent escalates and the dispatcher re-dispatches — the same mechanism D-30
already specifies for `edify:refactor`. Escalation on demand, never prediction
at plan time.

## Naming and resumption

Give every dispatch a `name`:

- `item-N-M` for a general item. An item executed in session (`/build` §4.1)
  leaves the name free, so it names that item's review: the corrector §4.1
  dispatches, or the self-review report the session writes itself at that name's
  report path.
- `item-N-M-s<k>-red` / `-test-review` / `-green` / `-code-review` for slice
  dispatches, and `item-N-M-s<k>-refactor` for a refactor the code review
  flagged (the opus re-dispatch reuses the name).
- `phase-P-corrector` for phase boundaries.
- `review-<group>` for a review-gate dispatch, `<group>` one of four fixed
  slugs, the rows `finishing.md` §1 groups by:
  - `review-code` — code and tests, and the default for any file kind no row
    names;
  - `review-skill` — skill definitions and the agent-instruction prose they
    load, meaning their `references/` nodes and the shared instruction files a
    skill loads from outside itself. An instruction file no skill loads, such as
    `CLAUDE.md` or `.claude/rules/*.md`, matches no row and takes the
    `review-code` default;
  - `review-agent` — agent definitions;
  - `review-design` — the living design graph under `docs/`, not a job's
    `plans/<job>/design.md`, which is a planning artifact.

  A file kind is always classed into one of these rows, never into a new group.
  The gate routes implementation files only; planning artifacts route by
  artifact (`finishing.md` §1).
- `final-review` for `finishing.md` §3.1's closing corrector, dispatched only
  where the review was skipped over a non-empty list or routing left a group of
  changed files unreviewed.
- `tdd-audit` for the auditor.

Resumption is `SendMessage` to the dispatch's name. An agent spawned unnamed is
resumed by `SendMessage` to its agent id, as `review-requirement.md` §UNFIXABLE
Detection Protocol step 4 does.

A child's own reply is the only authoritative result for its task. A late
task-notification on an already-reported task id may be answering something else
— never treat one as the report.

## Agent behaviour contract

The dispatched agent follows `plugin/fragments/delegation.md`: it reports to a
file, resolves recall by reading the artifact's listed files itself, returns per
§Prompt contents item 5, and after a failure is resumed at most once before a
fresh launch. The report-only reviewer's part-resumes are its return protocol,
not recovery.
