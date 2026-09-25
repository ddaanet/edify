# Item 2.2 — `plugin/skills/build/references/phase-boundary.md`

Status: **applied.** A later artisan, in a session that accepts edits, applied
the three Edits below with `Edit`, verbatim, after re-checking each old string
against the file and each new text against the item and KD-1, then reflowed by
`just format`. The history follows.

Original status: **blocked, Edit refused.** Each of the three Edits below came
back with "The server-side auto mode classifier gave no verdict (it skipped this
action)". That agent's session was still in auto mode. Nothing was applied.

Re-check notes, on applying:

- Every old string matched today's file exactly.
- Edit 1 covers both m4 (the run is gone, with its sandbox line) and C1: the
  bare `git diff --name-only` becomes KD-1's `<phase base>`, phase 1 from
  `tmp/build-baseline`, phase P>1 from D-86's `--diff-filter=A` query over
  `phase-<P-1>-corrector.md`.
- Edit 2's fragment pointer uses `../../fragments/`, the form the sibling
  references `finishing.md` and `escalation.md` already use; `phase-boundary.md`
  carried no fragment pointer before.
- Edit 3 is not one of the item's four bullets. It is kept because KD-7 now
  requires every commit to use `git commit -- <paths>`, and this is the
  orchestrator's phase-boundary commit, worded as SKILL.md §4.2 words the same
  commit for a review item.

Requirements: orch C1, M8, m3, m4.

## Edit 1 — drop the `verify-step.sh` run (m4); phase-base resolution (C1, KD-1)

- old:

  ````
  ```bash
  plugin/skills/build/scripts/verify-step.sh
  git diff --name-only
  ```

  Run `verify-step.sh` with `dangerouslyDisableSandbox: true`.
  ````

- new:

  ````
  The changed-files list is the phase's diff against its base:

  ```bash
  git diff --name-only <phase base>
  ```

  For phase 1 the base is the commit in `tmp/build-baseline`. For phase P>1 it is
  the commit that adds the previous phase's corrector report, which the commit
  closing that phase always lands:

  ```bash
  git log --diff-filter=A --format=%H \
      -- plans/<job>/reports/phase-<P-1>-corrector.md
  ```
  ````

The file carries no "do not run it again" line. SKILL.md §4.4 already covers the
run, and directive-writing cuts restating a step an earlier one settled.

## Edit 2 — scoped dispatch (m3) and the full §Execution Context halt (M8, KD-1)

- old:

  ```
  Read `references/dispatch-composition.md` and compose by it a checkpoint-form
  dispatch of `edify:corrector`: scope IN/OUT from the phase's items, design and
  recall artifact by path, changed-files list, report path from that reference's
  §Prompt contents rule under the dispatch name `phase-P-corrector`. IN/OUT lists
  must be non-empty and the changed-files list present — empty fields → STOP
  before delegating. UNFIXABLE
  ```

- new:

  ```
  Read `references/dispatch-composition.md` and compose by it a dispatch of
  `edify:corrector` scoped to the phase's items: scope IN/OUT and the Requirements
  summary from the phase's items, design and recall artifact by path, the changed
  files as an explicit list, a Constraints section barring findings outside scope
  OUT, and the report path from that reference's §Prompt contents rule under the
  dispatch name `phase-P-corrector`. Before delegating, STOP on any field
  `../../fragments/review-requirement.md` §Execution Context requires that is
  empty or missing: scope IN, scope OUT, changed files, Requirements summary and
  the Constraints section. UNFIXABLE
  ```

Pointer checked: `review-requirement.md` §Execution Context lists IN, OUT,
changed files and Requirements summary as required. Its §Enforcement paragraph,
in the same section, adds the Constraints section to the halt.

## Edit 3 — pathspec commit (KD-7, as accepted for Item 2.1)

- old: `applied where there are any — and always happens.`
- new:

  ```
  applied where there are any — and always happens. Stage those paths by name and
  commit with `git commit -- <paths>`.
  ```

## Carry-forward

The SKILL.md §2 sentence "Section 4 and `references/phase-boundary.md` call the
same one" goes stale with Edit 1. The orchestrator authorized fixing it in Item
2.3.
