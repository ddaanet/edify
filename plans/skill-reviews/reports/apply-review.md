# Review of the three skill-edit batches — 2026-09-21

Scope: every file under `plugin/skills/` and `plugin/fragments/` listed in
`apply-batch-{1,2,3}.md`, read as `git diff HEAD -- <file>`, against the edits
specified in
`verify-{ground,recall,formalize,design,proof,runbook,requirements,`
`review,deliverable-review}.md`. Plus the two tdd-audit items and the new
`plugin/skills/review/references/report-template.md`.

Every specified `open-mechanical` edit landed with the report's own wording (or
a deliberate improvement the batch report named). No batch edit collided with
today's earlier reviewed edits. No `open-design` finding was acted on. Nine
defects found and fixed, all introduced by the batches or by a prescription the
verify report got wrong; none UNFIXABLE.

## Major

**1. `plugin/skills/requirements/SKILL.md` §6 Finalise — overwrite guard fired
after the write.** `verify-requirements.md` M2 told the agent to move the
"existing requirements.md is being overwritten with a narrower scope → confirm
first" condition into step 6, but C1's fix had just made step 5 the step that
*writes* the file. As applied, the guard sat after the overwrite it guards.
**Fixed:** folded into §5 Write the Draft and Validate as a pre-write clause,
deleted the step-6 bullet. Net zero lines.

**2. `plugin/skills/deliverable-review/SKILL.md` §Layer 2 → Cross-cutting checks
— an invented convention asserted as fact.** M5's replacement text asserted
three fragment conventions. Two hold: all nine `plugin/fragments/*.md` open with
a `## ` heading naming the rule, and state the rule before its rationale. The
third — "referenced by path from at least one skill" — is false for five of the
nine: `claude-config-layout.md`, `token-economy.md` and
`workflows-terminology.md` are referenced from no production file at all (only
from `plans/` reports), and `error-classification.md` and
`prerequisite-validation.md` only from `.claude/rules/planning-work.md`. The
verify report itself said to cut the clause rather than assert an invented
convention. **Fixed:** clause dropped, the two verifiable ones kept.

**3. `plugin/skills/review/SKILL.md` frontmatter — `allowed-tools` narrower than
the body it governs.** M5 rewrote it to `Read` / `Write` / `Bash(git:*)` while
C2 rewrote §Constraints to grant "read-only search (`rg`, `rg --files`)", M10
added `ls plans/*/design.md …` to step 2, and `references/review-axes.md:35,:38`
require `rg --files` and `rg`. **Fixed:** `Bash(git:*, rg:*, ls:*)` on the one
existing line — net zero, so the 161-line budget holds.

**4. Ground's output-path rename left two sibling citations stale.** Ground
finding 4 moved the grounded document to `plans/reports/<topic>-grounding.md`;
`requirements/SKILL.md` §Standard Format → References and
`design/references/design-content-rules.md` (references list) both still named
`plans/reports/<topic>.md` as the grounding synthesis. **Fixed:** both updated.
(`design/references/research-protocol.md` says only "in `plans/reports/`" —
correct either way, left alone.)

**5. `plugin/agents/tdd-auditor.md` §Cross-Slice Checks → Scope compliance — the
same-item case unnamed.** The check covered only "work products belonging to
later items in earlier commits", while D-26's neighbour D-84
(`docs/references/pipeline-contracts.md`) makes a GREEN that implements the rest
of its *own* item the violation that strands the item's later slices. **Fixed:**
added the per-slice within-item clause, wording only, no decision id cited (the
plugin ships without `docs/`).

**6. `plugin/skills/build/references/dispatch-composition.md` §Prompt contents —
item 2 stated universally.** "Context by path, never by content" listed
`design.md` and the recall artifact for *every* dispatch, though the `tdd-audit`
dispatch's inputs are the slice reports and the commit range only
(`finishing.md` §3, and `tdd-auditor.md` §Inputs now blocks rather than falling
back to transcripts). **Fixed:** scoped the rule to dispatches that execute or
review the plan's work, with `tdd-audit` named as the exception. Review
dispatches keep the artifact — `review-dispatch-template.md` hands it to them.

## Minor

**7. `plugin/skills/runbook/SKILL.md` §1 Recall and Discovery — renumbering
rotted an inbound reference.** m14 renumbered the substeps `0.`–`4.` to
`a.`–`e.`; substep e still read "exploration may surface domains **step 1** did
not anticipate", whose referent was the old substep 1. **Fixed:** "step b".

**8. `plugin/agents/tdd-auditor.md` §Edge Cases — unresolvable citation.** The
new missing-reports clause cited `` `finishing.md` §3 `` from `plugin/agents/`,
where the bare form resolves to nothing; agent definitions cite full
repo-relative paths (`runbook-corrector.md:66`). **Fixed:**
`plugin/skills/build/references/finishing.md` §3. The bare form is correct
*inside* `build/references/`, so my own new citation in
`dispatch-composition.md` uses it, matching `review-dispatch-template.md`.

**9. `plugin/skills/deliverable-review/SKILL.md` §Phase 4 — orphan list item.**
M1's merge step landed as a numbered item "1." followed by unnumbered prose.
**Fixed:** prose, net zero.

**10. `plugin/skills/deliverable-review/SKILL.md` §Severity classification —
line-number citation in living prose.** m1 prescribed
`` `docs/references/deliverable-review.md:36-38` (D-56) ``; batch 2 had already
rejected raw line numbers for the same reason in `requirements/SKILL.md` m3.
**Fixed:** `` `docs/references/deliverable-review.md` §D-56 ``, matching the
`§D-26` form batch 1 applied in `design/SKILL.md`.

**11. `plugin/skills/deliverable-review/references/example-report.md` §Inventory
— the example stopped reading coherently.** m5's fallback dropped the two
`Configuration` rows, but findings C1 (`justfile:140-141`), C2
(`justfile:209-222`) and C3 (`plugin/justfile`) are filed against those files,
and the closing prose still says "artifacts (justfile/config)". An inventory
missing files the review reports on is the exact gap Phase 2 exists to catch.
**Fixed:** rows restored with the Lines cell reading `not recorded` — the
historical counts are unrecoverable (no `plans/worktree-update/`, no `wt-*`
block in today's `justfile`) and inventing them is what m5 forbade. Residual:
the example now shows two rows without a churn count.

**12. `plugin/skills/ground/references/grounding-criteria.md` §Process Skill
Internal Sources — an instruction the holder cannot execute.** Finding 14's
inserted bullet said to "route through `edify:recall`", but `ground/SKILL.md`
declares `Read, Write, Bash, WebSearch, WebFetch, Agent` — no `Skill` — and the
bullet is consumed by a Branch A dispatch whose tool list the skill does not
fix. **Fixed:** conditional — route through `edify:recall` where `Skill` is
available, otherwise match the index's hooks and Read the files they name.

## Accepted, not fixed

- **`a.`–`e.` in `runbook/SKILL.md` §1 are no longer a Markdown list.**
  CommonMark has no alpha-ordered lists, so each substep renders as a paragraph
  beginning "a. ". The scheme is what m14 specified, it reads correctly, and
  `just format` leaves it alone. Not worth churning.
- **`§`-citations of bold labels rather than headings** — `design/SKILL.md`
  §D-26, `item-review.md` §Verdicts, `deliverable-review/SKILL.md` §D-56. Each
  resolves by grep and the three are consistent with each other. Left.
- **`write-design.md` §C.1's recall-diff dedup** now points at
  `references/research-protocol.md` §A.5, whose prose names A.5's change
  triggers (codebase findings, external research, Context7) rather than C.1's
  (approach commitment, revised scope, rejected alternatives). The act survives
  inline in the pointer ("re-invoke recall on what just changed and reconcile
  the artifact"), so the loss is the trigger list, not the instruction. As m6
  prescribed; flagging rather than reverting.

## Verifications that came back clean

- **`review/SKILL.md` 231 → 161 loses nothing.** `report-template.md` is
  byte-identical to `HEAD:plugin/skills/review/SKILL.md` lines 84–166 (`diff`
  exit 0), the hub points at `references/report-template.md`, which resolves,
  the file is 85 lines, ends with a newline, and its only line over 80 columns
  (line 15, 81 chars) is inside the fenced template. The other deletion, m14's
  `**Required:**`/`**Optional:**` summary, now routes to
  `plugin/fragments/review-requirement.md` §Execution Context — that heading
  exists (`:107`) and is the authority the finding named.
- **Every `references/…`, `../…` and `plugin/…` path cited in a touched file
  resolves**, checked mechanically over all 34 changed files. Remaining
  unresolved strings are bare artifact names (`design.md`, `runbook.md`),
  placeholders, and the historical example report's paths.
- **Every skill and agent name resolves:** `edify:recall`, `edify:proof`,
  `edify:tdd-auditor`, `commit-commands:commit`, `handoff:handoff`,
  `code-review`, `security-review`.
- **Section citations resolve:** `delegation.md` §Quiet Execution Pattern,
  §Recall Artifacts For Sub-Agents, §Recall Content In Delegation Prompts, §Task
  Agent Tool Usage; `grounding-criteria.md` §Process Skill Internal Sources;
  `research-protocol.md` §A.5; `item-review.md` §Revisit;
  `review-requirement.md` §Execution Context; `finishing.md` §3.
- **The cross-file claims are true of the files they describe.**
  `deliverable-review` M6's "`Bash` in its tool list for search" matches
  `delegation.md` §Task Agent Tool Usage (:85-87); recall M3's sub-agent clause
  matches §Recall Artifacts For Sub-Agents (:94-96); recall M5 matches §Recall
  Content In Delegation Prompts (:118-119); review M4's built-ins match this
  environment's skill list; review M7's stage list matches the pipeline
  `CLAUDE.md` records.
- **`formalize`'s new mechanism claims hold against the code.**
  `src/edify/check_cli.py:15-19` maps VERIFIED→0, REFUTED→1, ERROR→2; `:85-86`
  computes `vacuity_warning` as verified-at-default-budget; `:99-100` emits
  `budget` and `vacuity_warning` in `--json`; `--timeout` is `cli.py:127-132`.
  Both files it now cites exist.
- **No unmarked threshold was introduced.** Every number the batches added or
  moved carries its marker: `recall` 5 entries ("an arbitrary ceiling, not
  calibrated"), `formalize` 5 iterations ("an arbitrary number, not
  calibrated"), `design-content-rules` 100–300 and five-repetition, `runbook`
  and `runbook-corrector` >8 items, `deliverable-review` 500/2000,
  `common-scenarios` 1000+.
- **No pending design job was pre-empted.** `/proof`'s
  `(a)pprove (r)evise (k)ill (s)kip` prompt is untouched, and m5/m6's dedup
  moved detail between `SKILL.md` and `item-review.md` without deciding which
  owns the coupling. `deliverable-review`'s "report severity counts only / the
  report is the deliverable" stance and the absent routing to `/design` are
  unchanged; m3's `## Sub-reports` section records Layer 1 provenance, not
  finding lifecycle. The corrector family (`corrector.md`,
  `design-corrector.md`, `outline-corrector.md`) is untouched — only
  `runbook-corrector.md`, for M5's ungrounded marker. `file:line` in a finding's
  Location is unchanged in both report templates; the one line-number edit I
  made (#10 above) was a living-prose citation, not a finding record.
  Repo-relative `plugin/…` references grew by three sites (`recall` ×2,
  `ground`, `deliverable-review`), all following the convention six existing
  files already use — the pending question is untouched, its surface is slightly
  larger.
- **Narration check.** The added text carries acts, not history. The three
  borderline additions — `formalize`'s "this is the case the project's
  error-handling rule carves out", `deliverable-review`'s "that is what makes
  them parallel", `tdd-auditor`'s "it is what strands the item's later slices" —
  each attach a reason to an instruction in the same sentence, which is the
  house form. No batch edit added a dated history note or a rationale paragraph
  where an instruction was wanted.

## Line budget

`wc -l` after `just format`, against the ceilings in the dispatch:

| File | Budget | Now |
|---|---|---|
| `plugin/skills/build/SKILL.md` | 218 | 218 |
| `plugin/skills/design/SKILL.md` | 277 | 277 |
| `plugin/skills/proof/SKILL.md` | 197 | 197 |
| `plugin/skills/requirements/SKILL.md` | 354 | 354 |
| `plugin/skills/review/SKILL.md` | 161 | 161 |
| `plugin/skills/deliverable-review/SKILL.md` | 198 | 196 |
| `plugin/agents/corrector.md` | 682 | 682 |
| `plugin/agents/design-corrector.md` | 460 | 460 |
| `plugin/agents/outline-corrector.md` | 450 | 450 |

`scripts/check_line_limits.allow` not touched.

## Gate

`just format && just precommit`, full output:

```
**Reformatted files:**
  - plugin/skills/deliverable-review/SKILL.md
  - plugin/skills/ground/references/grounding-criteria.md
  - plugin/skills/requirements/SKILL.md
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/requirements/SKILL.md: 354 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 277 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Seven `oversized-file:` lines, each inside its own allowlisted ceiling — the
same set batch 3 reported. Nothing staged, nothing committed, still on `main`.
