# Item 2.4 — tdd-slice.md: list revision in the hosting file, steps 2–3 end at §4.4

Target: `plugin/skills/build/references/tdd-slice.md`. Requirements: M5, m13.

## Edits

### §After the slice, step 2 (Refactor on signal) — m13

Appended after "A second `escalated` goes in the run summary and execution
continues":

> Once the refactoring commit lands, run the post-item verification of
> `SKILL.md` §4.4. On `error` → run it too, since a failed refactor can leave
> dirt like any other step, then log and continue.

Replaces the bare "On `error` → log and continue." A refactor returning
`error` after leaving dirt now reaches §4.4 like any other step. `escalated`
is unchanged: `plugin/agents/refactor.md` returns it before editing, so it
leaves no commit to verify.

### §After the slice, step 3 (List revision) — M5, m13

- The revision is made in the file hosting the item — `runbook.md`, or the
  `outline.md` or `design.md` routed to `/build` — in place of `runbook.md`.
- Its commit takes that file alone:
  `git commit -- plans/<job>/<hosting file>`, subject unchanged
  (`<type>: <job> Item N.M/k — list revision`).
- Once that commit lands, run the post-item verification of `SKILL.md` §4.4.
  "List revision: none" commits nothing and has nothing to verify.

No outline KD label appears in the file. Neither rule has a D-number in the
living design, so the text states what is meant.

## Agreement with neighbours

- `SKILL.md` §4.4 lists "a slice's GREEN, its code review, its refactor and
  its list revision". Steps 1–3 now each end at §4.4 once their commit lands.
- `escalation.md` §Post-item remediation step 2 names `edify:artisan` after a
  refactor or list-revision commit. The verification that leads there now
  runs after both.

## Line count

104 lines after `just format`.

## Out-of-scope surfaces still naming `runbook.md` as the list-revision host

Not edited, because they are outside this item's scope:

- `docs/references/pipeline-contracts.md` D-24: "a list revision is an edit to
  `runbook.md` the orchestrator commits". Item 3.1 does not list D-24.
- `docs/references/build-run-state.md` D-90: "the run's reports and
  `runbook.md` list revisions are its record". It is still true, because all
  of `plans/<job>/` is dropped, but it is narrower than KD-7.
- `plugin/agents/tdd-auditor.md` is covered by Item 2.5.

## Verification

`just precommit` passed, run in the foreground.
