# Items 2.6–2.9 — run summary

Status: **all four applied, no stop.** `just precommit` passed before each
commit. The only other output was the three `oversized-file` lines for
`plugin/agents/corrector.md`, `outline-corrector.md` and `design-corrector.md`,
which were there before this run and did not fail the gate. After each commit,
`git status --porcelain` showed only the pre-existing `.claude/handoff-task.md`,
`.claude/handoff-todo.md`, `memory` and `inbox/…md` paths.

| Item | Commit | Change |
|------|--------|--------|
| 2.6 | `167db2e5` | `escalation.md`: the Exit-1 bullet now starts with the mask re-run (once, not remediated). "Agent never returns" follows KD-4. §Post-item remediation says it is the dirty-tree rule and requires confirmation before `git clean -fd`. §Resuming re-invokes with the same `plans/<job>` and resolves the phase base per KD-1 ([item-2-6.md](item-2-6.md)) |
| 2.7 | `52028fbb` | `review-requirement.md` Changed files: `git diff --name-only <base>` against the run's or phase's base, never bare ([item-2-7.md](item-2-7.md)) |
| 2.8 | `7bf20896` | `escalation-acceptance.md` §Dirty tree recovery: defers to `escalation.md` §Post-item remediation and restates KD-5 ([item-2-8.md](item-2-8.md)) |
| 2.9 | `e35bc1dc` | `delegation.md` §Multi-Step Verification: `/build`'s `verify-step.sh` owns the verdict. `&&` guards nothing because `git status --porcelain` exits 0 when the tree is dirty ([item-2-9.md](item-2-9.md)) |

Judgement calls the outline left open, with details in each item report:

- **2.6:** if the re-run is annotated again, stop and report to the user. A
  resumed run keeps `tmp/build-baseline` and does not recapture it.
- **2.7:** "recorded base" became "base commit of the run or phase under
  review", because KD-1 resolves the phase base rather than storing it.
- **2.8:** the section names the governing rule and restates it, instead of
  being a bare pointer.

Seams I noticed but did not change, because they are outside the named sections:

- `escalation-acceptance.md` §Rollback protocol still runs an unconfirmed
  `git checkout -- .`.
- The same file's "clean = empty porcelain" definition ignores the KD-7
  exemptions.
- `review-requirement.md` self-review still uses `git diff HEAD`.
- `SKILL.md` §2 does not itself say a resumed run skips the baseline capture.
