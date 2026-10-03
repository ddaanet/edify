# Item 2.8 — `plugin/fragments/escalation-acceptance.md`

Requirements: Major 5, (a), m13, and the review's recovery-copy minor.

## Changes per bullet

- **§Required and §Verification sequence (m13).** The clean-tree criterion is
  now `plugin/skills/build/scripts/verify-step.sh` exit 0, named as `/build`'s
  single definition of a clean tree. It names the three paths dirty by
  convention (`memory`, `.claude/handoff-*.md`, `inbox/*.md`) and says the test
  is not an empty `git status --porcelain`, which any of them fails. Step 3 of
  the sequence runs `verify-step.sh` instead of checking `git status
  --porcelain`. On `DIRTY:` it commits the fix by name
  (`git commit -- <paths>`, KD-4's form) and re-runs until exit 0.
- **§Rollback protocol (Major 5, (a), KD-3).** The `git revert HEAD` /
  `git checkout -- .` bullet is now two bullets:
  - Fix committed: `git revert HEAD`, unchanged.
  - Fix uncommitted: escalate to the user with the `verify-step.sh` listing and
    what the attempt found. Nothing reverts it by default. A path the user
    decides to revert is reverted by name, by the one call
    `escalation.md` §Post-item remediation gives. Never `git checkout -- .`,
    which reverts every modified tracked path at once, exempt ones included.
  The Saga, Assumption and after-rollback bullets are kept.
- **§Dirty tree recovery (recovery-copy minor).** The five-line restatement is
  gone. It had already drifted: it kept the fresh `edify:artisan` and the
  `git checkout -- . && git clean -fd` fallback, and it lacked the
  skip-the-resume cases. What remains is the trigger (`verify-step.sh` reports
  `DIRTY:` after the item), the pointer to `escalation.md` §Post-item
  remediation, and a statement that this fragment keeps no copy.
  `escalation.md`'s own line ("§Dirty tree recovery defers to it") stays true.

## Judgement calls for review

- **`git revert HEAD` kept for a committed fix.** The item's bullet covers the
  uncommitted case and the `git checkout -- .` command only. KD-3 is about dirt,
  and the reason it rejects a default revert is that one "discards work the run
  already paid for". `git revert` adds a commit and keeps the reverted work in
  history, so I left it alone. If KD-3's "nothing reverts by default" is meant
  to cover committed work too, this bullet needs the same escalate-first
  wording.
- **"Commit the fix by name" in step 3.** The old step said only "commit fix".
  I added `git commit -- <paths>` because a pathspec-less commit would carry
  staged exempt dirt, which is the safety argument KD-4 and KD-7 rest on.
- **Trigger in §Dirty tree recovery is `DIRTY:`, not exit 1.** Exit 1 also
  covers `PRECOMMIT:`, which is not dirt. `escalation.md` §Post-item remediation
  handles both, so the pointer loses nothing.
- **Path form.** The new pointers use the `plugin/skills/build/...` form the
  fragment already used at its one existing pointer (outline §Scope OUT).
- **Voice.** "the user", as the file already says.

## Cross-references left for later items

- `docs/design.md:303` points at this fragment for timeout handling only, so
  nothing there goes stale. No `docs/` drift seen for Items 2.12 and 2.14.

## Verification

- `just format`, then `just precommit` green: version consistency, cached
  tests, line limits (only the three allowlisted correctors reported), design
  links.
- Self-review of the uncommitted diff against Item 2.8's three bullets, KD-3,
  KD-4 and KD-7, and against `escalation.md` §Post-item remediation, which now
  holds the one copy, and `SKILL.md` §2's clean-tree sentence.
- 87 lines before, 88 after (`wc -l`, after `rumdl fmt`).
