# build-fixes — leg 4 report

Leg 4 resumed from `build-leg3.md` after my human partner answered Item 2.14's
venue question. The run is **complete**: Item 2.14 landed, and §5 Finish ran in
full (review gate, triage feedback, TDD audit, closing commit).
`verify-step.sh` returned exit 0 after every commit.

## Governing rules (unchanged)

- The governing skill text is `plugin/skills/build/` at `d415f22d`, read with
  `git show`. The live text was not followed, since this job rewrote it.
- Dispatches are unnamed and resumed by agent id.
- Every commit uses `git commit -m … -- <paths>`. The staged
  `.claude/handoff-todo.md` was never touched.

## Answers from my human partner, cumulative

1. to 4. As in `build-leg3.md`: Item 1.4, Item 2.15, the fresh 2.3/2.4
   artisan, and no slice for the KD-1 `:(glob)` test.
2. Leg 4, Item 2.14: option 1. The new node
   `docs/references/build-run-state.md` holds D-88 to D-94 under a new group in
   `docs/decisions.md`. D-86 stays in `pipeline-contracts.md`, and the new node
   cites it. Consent was given for the `CLAUDE.md` routing bullet; see open
   item 1.
3. Leg 4, `corrector.md` §0 versus KD-5's `review-design` row: under
   discussion. Stop before dispatching a `review-design` group that holds a
   single file under a design path. Not triggered, because the group held six
   `docs/` files and its review ran normally.

## Completed this leg

| Step | Commit subject |
|---|---|
| Item 2.14 | `📝 Item 2.14 — record D-88 to D-94 in a new build-run-state node` |
| Review gate, `review-code` | `🐛 Review gate — review-code fixes` |
| Review gate, `review-agent` | `📝 Review gate — review-agent report` |
| Review gate, `review-design` | `🐛 Review gate — review-design fixes` |
| Review gate, `review-skill` | `🐛 Review gate — review-skill fixes` |
| §3 closing commit | `📝 build-fixes Finish` |

## Run summary

**Dispatches across the run** (reports under `plans/build-fixes/reports/`):

- **Items 1.1–1.4 (tdd).** Eleven slices, four dispatches each:
  `item-1-N-s<k>-{red,test-review,green,code-review}.md`.
- **Items 2.1–2.15 (general).** One report each, `item-2-N.md`.
  - 2.1–2.7: one artisan, resumed.
  - 2.8–2.11 and 2.13: one artisan.
  - 2.12 and 2.14: one artisan, resumed with the venue answer.
  - 2.15: executed in session.
- **Review gate.** `review-code.md`, `review-agent.md` and `review-design.md`,
  each by `edify:corrector` (opus). `review-skill.md` by
  `plugin-dev:skill-reviewer` (report-only, in four parts, plus a second pass).
- **Triage and audit.** Triage feedback gave the verdict `match`: 99 files
  changed, 62 reports, behavioural code yes, review artifact present. The TDD
  audit is in `tdd-audit.md`.

**List revisions:** none recorded in a runbook, since the job has no
`runbook.md`. The TDD audit notes two items:

- The outline amendment for Item 1.4 rode the 1.4/1 code-review commit, after
  that item's first GREEN.
- The 1.4/2 and 1.4/3 list changes never reached the outline (Violations 3–4).

**Remediation RCAs:** no post-item remediation fired in leg 3 or leg 4.

**Follow-up:** `/deliverable-review plans/build-fixes`, on opus in a fresh
session.

## Review-gate outcomes

- **`review-code`: Ready.**
  - Added pinning tests, each proven red by an in-place mutation, for:
    - the KD-1 `:(glob)` query (this closes leg 3's open finding);
    - the job-name guard;
    - unborn HEAD giving exit 2 rather than `NO-BASE:`;
    - `--no-renames` on the diff;
    - `triage-feedback.sh`'s `--no-color` and its failing-diff error path.
  - Corrected a false `--no-renames` rationale in the `changed-files.sh`
    comment. The 1.2/3 code-review record makes the same wrong claim and was
    left as written.
  - Decided that the `printf` DIRTY listing gets no test.
- **`review-agent`: Ready**, with no changes.
- **`review-design`: Ready.** One major and three minor fixes, all in
  `build-run-state.md` and `design.md` §5.3:
  - the `--no-renames` rationale in D-88;
  - triage's relation to the script in D-90;
  - the empty-operand clause in D-92;
  - the hub wording.
- **`review-skill`: 2 major and 11 minor findings**, every one applied except
  m11's first bullet (§4.4 exhaustiveness, which the reviewer made
  conditional).
  - MAJOR 1: `SKILL.md` §1 and the `escalation.md` exit-1 bullet now say that
    §Resuming step 2 stands in for §2 on a resumed run.
  - MAJOR 2: the review template gains the design-row criteria slot.
  - The second pass found three minor issues, all fixed:
    - the rollback scope;
    - the `git revert --no-commit` recipe, probed on git 2.47.3;
    - the routing of non-item steps to remediation.
- No UNFIXABLE in any report.

## Deviations this leg

1. **The `CLAUDE.md` bullet was not added**, either by the 2.14 artisan or by
   me. Consent relayed through an agent message is not my human partner's own
   approval for a `CLAUDE.md` edit. See open item 1.
2. **Report-only fixes were applied by a delegated opus artisan, not in
   session.** My context was past 200k tokens. The four parts were saved to
   `tmp/review-skill-parts/`, the artisan applied the fixes and wrote
   `review-skill.md`, and I committed. The second pass ran as `finishing.md`
   §1 prescribes.
3. **Review-gate commits** use `Review gate — <group>` subjects, one commit per
   group, rather than one combined commit. The d415f22d text has each group's
   report committed. The closing commit's subject is `build-fixes Finish`.
4. **Stale git locks were removed twice.** `.git/HEAD.lock` (21:35:45) and
   `.git/refs/heads/main.lock` (21:46:00) were each zero-byte and left behind
   right after a sandboxed commit had landed. Each persisted outside the
   sandbox, nothing held it (`fuser` empty), and an unsandboxed commit failed
   the same way. That is case 4 of the `sandbox-effects` discriminator, so I
   ran `rm` on each. Later commits ran unsandboxed and left no lock.

## Open items for my human partner

1. **`CLAUDE.md` §Design Decisions needs the new node's routing bullet.** Add
   it after the `pipeline-contracts.md` bullet, or confirm in your own words
   and a session will add it:

   ```markdown
   - `build-run-state.md` — `/build`'s run state in git: resume, run and phase
     bases, changed files, the clean tree, dirt, review-gate groups, commit
     subjects
   ```

   `.claude/rules/workflow-work.md` routes workflow work only to
   `pipeline-contracts.md` and `execution-routing.md`. Adding the new node there
   too is a separate call.
2. **`corrector.md` §0 versus D-93** (the KD-5 design row) is still open. A
   `review-design` group holding only `docs/design.md` would be refused. Defect
   21 owns corrector edits.
3. **KD-3 and committed work** (`review-skill.md` m6): should "nothing reverts
   by default" also cover a committed failed fix, so that it escalates before
   any `git revert`? `escalation-acceptance.md` currently reverts on
   failure.
4. **Work taken from the invocation** (`SKILL.md` §1 option 3): does it name
   its report `item-1-1`? The answer decides whether `NO-BASE:` at finishing
   (Item 2.4's STOP) can arise legitimately.
5. **Two zero-byte reflog-path locks remain**: `.git/logs/HEAD.lock` and
   `.git/logs/refs/heads/main.lock`. Their mtimes match the removed ref locks
   to the nanosecond, nothing holds them, and git does not use those paths.
   They look synthetic, so I left them; they do not block commits.
6. **The TDD audit's Important recommendations**: route code-review behaviour
   changes to a pinning slice, and commit list revisions before the slices
   they govern, on their own. These are for the deliverable review or a later
   job.
7. A dated changelog entry
   (`docs/changelog/2026-10-03-build-reads-run-state-from-report-history.md:24`)
   says "after an item" where `escalation.md` now says "after a committed
   step". It is left as written.
