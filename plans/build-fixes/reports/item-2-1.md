# Item 2.1 — `plugin/skills/build/SKILL.md`

Requirements: Major 1, Major 4, Major 7 (§4.1), m16.

## Changes per bullet

- **§1, KD-1's test.** Dropped "A resumed run Reads `references/escalation.md`
  §Resuming before §2" from the `<job>` paragraph. Added a paragraph after the
  existence rules: any `plans/<job>/reports/item-*.md` on disk → resumed, Read
  `escalation.md` §Resuming before §2; none → fresh; only `item-*` counts,
  since planning reports share the directory. No STOP. Also "Section 5 writes
  under `plans/<job>/reports/`" became "Sections 4 and 5", since §4.1 now
  writes `item-N-M.md` there.
- **§2, baseline capture.** Deleted the "Capture the baseline" paragraph, its
  `git rev-parse HEAD > tmp/build-baseline` block and the rationale after it.
  The clean-tree sentence now says "Section 4 and `references/finishing.md`
  call the same one" rather than naming `finishing.md` §1 only, so it stays
  true once Item 2.4 adds §3's `verify-step.sh` run.
- **§4.1, review before the one commit.** Order is now: edit,
  `just precommit`, review the uncommitted diff (self-review via `git diff
  HEAD` writing `plans/<job>/reports/item-N-M.md` itself, or the `item-N-M`
  corrector scoped to the uncommitted changes, whose report is taken at that
  path), then one commit `<type>: <job> Item N.M — <title>` carrying edits,
  fixes and report, by `git commit -- <paths>` (KD-1, KD-8). The old "commit
  its report and fixes as §4.2 does" sentence is gone.
- **§4.4.** "a review item or §4.1's corrector once its commit lands … any
  general or directly executed item" became "a review item once its commit
  lands, §4.1's one commit, … any general item"; the lead is "every step whose
  work is committed", since §4.1's commit is not a dispatch.
- **§5.** Added: "`references/finishing.md` §1's report commit carries it"
  for `review-skip.md` (KD-4).
- **§6.** Deleted the 2-level paragraph (a word-for-word copy of
  `escalation.md` §Escalation's opening). The pointer paragraph stays.

## Line count

200 before, 193 after (`wc -l`, after `rumdl fmt`).

## Cross-references left for later items

- `review-skip.md` committed by `finishing.md` §1's report commit: `finishing.md`
  states it in Item 2.4.
- `item-N-M` as the name of §4.1's self-review report: stated in
  `dispatch-composition.md` §Naming and resumption by Item 2.6.
- The `<type>: <job> Item N.M — <title>` subject form: Item 2.6 restates it in
  `dispatch-composition.md` §Prompt contents item 4; Item 2.13 sweeps the agent
  files.

## Verification

`just precommit` green (rumdl reflowed two paragraphs first). Self-review of
the uncommitted diff against the outline's Item 2.1 bullets and KD-1, KD-4,
KD-8.
