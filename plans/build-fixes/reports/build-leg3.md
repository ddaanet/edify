# build-fixes — leg 3 report

Leg 3 resumed from `build-leg2.md`. The resume-time `verify-step.sh` returned
exit 0. Recall re-read the recall artifact's four memory files. Every item
committed this leg was followed by `verify-step.sh` exit 0.

**Stopped at a decision: where Item 2.14's seven decision records go. The
question is at the end of this report.** Every other item is done.

## Governing rules (unchanged, for a fresh delegate)

- The governing skill text is `plugin/skills/build/` at `d415f22d`. Read it
  with `git show d415f22d:plugin/skills/build/<file>`. Do not use the Skill tool
  for `edify:build`, since it loads a stale `dist/` copy. Do not follow the live
  `plugin/skills/build/`, which this job rewrote.
- Dispatches are unnamed and resumed by agent id. Every dispatch names an output
  file under `plans/build-fixes/reports/`.
- `.claude/handoff-todo.md` is staged by the main session. Every commit uses
  `git commit -m … -- <paths>`. Never unstage, reset or commit it.
- Leave the untracked inbox brief and the zero-byte `.claude/*` sandbox masks
  alone.

## Answers from my human partner, cumulative

1. Leg 2: Item 2.3's question was answered with a variant of option 1, Item 1.4
   `changed-files.sh <job> --phase`. It is done.
2. Leg 2: Item 2.15. Remove `PLR0913` from `ruff_ignores`. Never ignore RUF100.
   Stop on new PLR0913 hits. Add the item to the outline in its commit. It is
   done; see deviation 1.
3. Leg 2: after Item 1.4, a fresh artisan does 2.3 and 2.4, then the run carries
   on as planned. Done.
4. Coordinator default for leg 3: the KD-1 `:(glob)` query gets no pinning
   slice. It is left as a finding for the §5 review gate.

## Completed this leg

| Item | Commit subject |
|---|---|
| 1.4/4 | `🐛 Item 1.4/4 — code-review fixes` |
| 2.3 | `📝 Item 2.3 — phase boundary: changed-files.sh --phase base, validated UNFIXABLE, ordered commit` |
| 2.4 | `📝 Item 2.4 — finishing: changed-files.sh base, KD-5 groups, review-gate and closing commits` |
| 2.5 | `📝 Item 2.5 — review dispatch template: changed-files.sh base, report-only UNFIXABLE and blocked, example scope` |
| 2.6 | `📝 Item 2.6 — dispatch composition: KD-5 slugs, final-review triggers, job-labelled subjects, truncated parts` |
| 2.7 | `📝 Item 2.7 — tdd slice: by-path commits with job-labelled subjects, §4.5 pointer` |
| 2.8 | `📝 Item 2.8 — escalation acceptance: verify-step.sh clean tree, escalate-first rollback, recovery pointer` |
| 2.9 | `📝 Item 2.9 — review requirement: changed-files.sh form, KD-5 skill and design rows, craft fallback, resume-by-name reclassification` |
| 2.10 | `📝 Item 2.10 — tdd auditor: phase boundaries, job-labelled slice marker` |
| 2.11 | `📝 Item 2.11 — plugin README: verify-step.sh call sites, changed-files.sh and exempt-paths.sh` |
| 2.12 | `📝 Item 2.12 — D-86 argument: verify-step.sh exemption in the past tense` |
| 2.13 | `📝 Item 2.13 — test-driver and refactor: job-labelled commit subjects` |
| 2.15 | `📦️ Item 2.15 — just lint agrees with precommit on PLR0913` |

Every report is at `plans/build-fixes/reports/item-1-4-s4-code-review.md` or
`item-2-{3..13,15}.md`. Dispatches this leg:

- Code review 1.4/4: `edify:corrector` (opus).
- 2.3 to 2.7: one `edify:artisan` (opus), resumed once.
- 2.8 to 2.11 and 2.13: one artisan (opus).
- 2.12 and 2.14: one artisan (opus).
- 2.15: executed in session and self-reviewed.

## Resume point

**Item 2.14, once the venue question below is answered.** Then §5 Finish, per
`git show d415f22d:plugin/skills/build/references/finishing.md`: the review
gate, triage feedback, the final review if needed, the TDD audit (Items 1.1 to
1.4 are tdd), and the run summary.

Item 2.14 state:

- Nothing is committed for it.
- Its drafts are in the gitignored `tmp/item-2-14/`: `d.md` holds the seven
  decision paragraphs, D-88 to D-94, and `r.md` holds twelve
  rejected-alternative entries. `decisions-block.md` and `rejected-block.md` are
  also there.
- Its blocked report, with measurements, the KD-to-decision table, the planned
  `docs/design.md` §5.3 edits and a changelog entry, is
  `tmp/item-2-14/blocked-report.md`. I moved it there from
  `plans/build-fixes/reports/item-2-14.md` so that the tree stays clean and
  report history does not count 2.14 as landed. Move it back as the item report
  when 2.14 is executed.
- The artisan that drafted it can be resumed by id, or a fresh opus artisan can
  start from the blocked report and drafts.

## Gate results

- `just precommit` is green at the leg's last commit: version consistency, the
  test sentinel, line limits, and design links (87 decisions, 8 nodes). The
  corrector's and artisans' fresh suite runs report 379/380 passed, 1 xfail.
  Line limits prints three `oversized-file` lines for the allowlisted
  `*-corrector.md` agents.
- `just lint` is now green; it failed at baseline (Item 2.15).
- `verify-step.sh` returned exit 0 after every commit this leg.

## Deviations

1. **Item 2.15 also edits `justfile`.** The ruling named `plugin/portable.just`
   only, but `justfile`'s prolog redefines `run-lint-checks`, and that copy
   wins. Measured: with `portable.just` edited alone, `just lint` still failed
   on RUF100 at `tests/line_limits_helpers.py:32`. With the same one-token
   removal in both files it passes. `ruff check --select PLR0913 src tests`
   finds no hits, so no stop condition fired. The outline's Item 2.15 and
   Scope IN record both files.
2. **Item 2.9 extra scope (orchestrator's call).** `review-requirement.md`
   §UNFIXABLE Detection Protocol step 4 said reclassification is a fresh
   delegation with "no continuation mechanism available". Items 2.3 and 2.4
   resume `review-<group>` by name instead. Step 4 now resumes a named dispatch
   by `SendMessage` and re-delegates an unnamed one. Recorded in `item-2-9.md`.
3. **Item 2.14 extra scope (orchestrator's call, not yet executed).**
   `docs/design.md` §5.3 still records the pre-KD-8 subject form. The artisan
   was told to update the hub along with the node, because a hub conclusion and
   its node's argument change together.
4. **Code review 1.4/4 fix with no test.** `verify-step.sh` now prints the
   DIRTY listing with `printf '%s\n'` rather than `echo`, which guards against
   an inherited `BASHOPTS=xpg_echo`. The verdict was never affected, and no
   test pins the fix.
5. Executors went past their items' literal text in these places, each
   recorded in the item's report under "Judgement calls":
   - 2.3: an extra STOP when the P-1 landed query disagrees with `--phase`'s
     `BASE:`.
   - 2.4: `NO-BASE:` at finishing is a STOP, and the review gate makes one
     commit for all groups.
   - 2.5: a `blocked:` reply routes to `escalation.md`, and the U-REQ, U-ARCH
     and U-DESIGN glosses are written inline.
   - 2.6: an item subject is added beside the slice one.
   - 2.7: the GREEN subject also moves to KD-8's form.
   - 2.8: `git revert HEAD` is kept for an already-committed fix.
   - 2.9: the working-tree form serves `/review` and the `/build` §4.1
     corrector.
   - 2.10: the auditor accepts the refactor commit and a list-revision commit
     that touches only `runbook.md`, neither of which has a report.
   - 2.11: the README's `verify-step.sh` call sites add the entry gate and a
     delegated general item.

   All of these are for the §5 review gate.

## Findings for the §5 review gate

- The KD-1 `:(glob)` `item-*` query has no pinning test. The default above
  leaves it here.
- **`plugin/agents/corrector.md` §0 "Design document rejection"** refuses a
  single-file scope that is `design.md` or sits in a `design` path. KD-5's
  `review-design` row sends the `docs/` design graph to `edify:corrector`, so a
  group holding only `docs/design.md` would be refused with
  `Error: Wrong agent type`. `corrector.md` is outside this job's scope; defect
  21 owns corrector edits and the file is allowlisted at 682 lines. This job's
  own gate is not affected, because its `review-design` group will hold several
  `docs/` files. Flagged by `item-2-9.md` and the 2.14 blocked report.
- Two older slips in `review-requirement.md` are in no item: "phase checkpoint"
  in one place, and a "4-gate checklist" where the protocol lists three gates.
- `--phase` alone cannot detect a skipped boundary. `phase-boundary.md` now
  checks with KD-2's per-phase landed query (`item-2-3.md`).

## Open question: where do Item 2.14's decisions go?

The seven decisions (KD-1, KD-2, KD-3, KD-5, KD-6, KD-8 and build-defects KD-7,
drafted as new decisions D-88 to D-94) do not fit in
`docs/references/pipeline-contracts.md`. `scripts/check_line_limits.sh` caps
`docs/` markdown at 400 lines as a hard gate, and the node is at 314. The drafts
measure 129 lines of decisions plus 38 lines of rejections, which comes to
481 lines plus separators. Inlining the rejections still gives 443. Raising an
allowlist ceiling is not an option (`memory/line-caps.md`), and shaving the
argument is forbidden.

1. **A new node, `docs/references/build-run-state.md` (recommended default).**
   It holds D-88 to D-94 under a new group in `docs/decisions.md`. The seam is
   real: all seven decisions concern how `/build` keeps and reads run state in
   git. `pipeline-contracts.md` stays at 314. **Cost: one bullet in
   `CLAUDE.md` §Design Decisions**, the node routing list, and optionally a line
   in `.claude/rules/workflow-work.md`. I have not edited `CLAUDE.md`; this
   needs your consent. Sub-question: D-86 stays in `pipeline-contracts.md` and
   the new node cites it (default), or it moves with them.
2. **Distribute across existing nodes.** D-91 goes to `quality-gates.md` and
   D-92 to `execution-routing.md`. `pipeline-contracts.md` would still reach
   428, so this needs a further move or a split as well.
3. **Split `pipeline-contracts.md`** along its planning/execution seam. This is
   the largest rewire: existing index lines move between groups, and the
   `CLAUDE.md` routing list changes too.

When answered, the 2.14 executor writes the node or nodes, the
`docs/decisions.md` index lines and rejections, `docs/design.md` §5.3 (script
set, D-94's subject form), and a changelog entry. It also makes the `CLAUDE.md`
bullet, if option 1 or 3 is chosen with your consent. Then it commits
`docs: Item 2.14 — …` and runs `verify-step.sh`, and §5 Finish follows.
