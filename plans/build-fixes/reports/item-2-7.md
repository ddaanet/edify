# Item 2.7 — `plugin/skills/build/references/tdd-slice.md`

Requirements: Major 3, m14.

## Changes per bullet

- **§After the slice, step 1 (KD-4, KD-8, Major 3).** "Stage those paths by
  name." became "Stage those paths by name and commit with
  `git commit -- <paths>`." The subject is now
  `<type>: <job> Item N.M/k — code-review fixes`.
- **§After the slice, step 3 (KD-4, KD-8, Major 3).** "Commit the `runbook.md`
  edits after the slice" now gives the form: stage the file by name, commit
  with `git commit -- plans/<job>/runbook.md`, subject
  `<type>: <job> Item N.M/k — list revision`. KD-8 lists list-revision commits
  under the `Item N.M[/k]` form.
- **Step 1, the stale pointer (m14).** "The same step §5 takes at a phase
  boundary" (§5 is Finish) became "the order `SKILL.md` §4.5's phase boundary
  keeps too". `phase-boundary.md` §Commit commits, then runs §4.4's
  verification.

## Judgement calls for review

- **(c) GREEN's subject too.** `<type>: Item N.M/k — <title>` in (c) became
  `<type>: <job> Item N.M/k — <title>`. The item's bullets name only steps 1
  and 3. Leaving GREEN on the old form would put two subject forms for one
  slice in this file, against KD-8 ("Every `/build` commit uses one of these
  subjects") and `dispatch-composition.md` item 4 as Item 2.6 left it.
- **`SKILL.md` named in the m14 fix.** The outline says the pointer "becomes
  §4.5's". The sentence already cites `SKILL.md` §4.4, and a bare "§4.5" in
  this node could read as one of its own sections, so the fix names `SKILL.md`.

## Cross-references left for later items

- `edify:refactor`'s own commit subject (step 2, "its own refactoring commit")
  comes from `plugin/agents/refactor.md`: Item 2.13.
- `plugin/agents/test-driver.md`'s GREEN subject: Item 2.13.
- `SKILL.md` §4.4 does not list the list-revision commit among the steps
  followed by `verify-step.sh`. KD-4 does not require it and no item names it.
  Noted only.

## Verification

- `just format`, then `just precommit` green (version consistency, cached
  tests, line limits — only the three allowlisted correctors reported — and
  design links).
- Self-review of the uncommitted diff against Item 2.7's bullets, KD-4 and
  KD-8, and against `dispatch-composition.md` item 4 and `phase-boundary.md`
  §Commit.
- 95 lines before, 98 after (`wc -l`, after `rumdl fmt`).
