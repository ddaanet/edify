# Digest — `plans/skill-reviews/reports/`, open items as of 2026-09-23

Sources: `verify-summary.md`, the eleven `verify-<skill>.md` reports,
`apply-batch-{1,2,3}.md`, `apply-review.md`, all under
`plans/skill-reviews/reports/`. Each open item was checked against the working
tree on 2026-09-23 (HEAD `🔧 brief triage calls, open-decisions proof, orphan
fragments removed`). Items the reports record as fixed or applied are left out,
unless the tree or `apply-review.md` says otherwise.

Frame bullets are the `## Remaining` section of `.claude/handoff-todo.md`,
numbered in order:

- R1 read the reports first
- R2 repo-relative `plugin/…` paths job
- R3 `../claude-plugins/README.md`
- R4 skill-reviews: 27 open-design + 3 disputed
- R5 sweep-exit job
- R6 pilfer defect 21
- R7 brief-triage jobs
- R8 macOS `just test`
- R9 FR-12 remainder
- R10 pilfer-superpowers
- R11 README dprint
- R12 untracked `.claude/` paths
- R13 `MEMORY.md` over budget

R1 tells the reader to read the reports but does not carry any single item, so
this digest does not count it as carrying one.

**Retired skills.** `plugin/skills/inline/` and `plugin/skills/orchestrate/` do
not exist. `plugin/skills/` holds build, deliverable-review, design, formalize,
ground, proof, recall, requirements, review and runbook. The verify reports
already checked every inline/orchestrate finding against its `build/` successor
(`verify-inline.md:3-9`, `verify-orchestrate.md:177-183`), so those findings
are classified below by that successor file. None is OBSOLETE.

**Tree drift since the reports.** Several files have since been split or
renamed:

- `design/SKILL.md` split into `references/triage.md`.
- `build/references/resuming.md` became `escalation.md`.
- `requirements/SKILL.md` split into `elicit-mode.md` and `formats-and-exit.md`.
- `review/references/report-template.md` is now `review-template.md`.

Line numbers below are current-tree, not the reports'.

## STILL-OPEN, in frame

### Job (1): repo-relative paths / `docs/` not shipped

- **`deliverable-review` C2.** Shipped skill cites
  `docs/references/deliverable-review.md`, which the plugin does not carry. One
  citation sits inside the report template, so every report writes a dead
  citation. Source: `verify-deliverable-review.md`. Evidence: still cited at
  `deliverable-review/SKILL.md:67`, `:153` (template), `:178`, `:196`, and at
  `references/example-report.md:3`. Frame: **R2** ("`deliverable-review/SKILL.md`
  ×5 to `docs/references/deliverable-review.md`"), also R4.
- **`formalize` 2.** Bare `edify check` works only in the dev checkout. The fix
  waits on D-12's open probe of whether `${CLAUDE_PLUGIN_DATA}` substitutes in
  skill content. Source: `verify-formalize.md`. Evidence: `formalize/SKILL.md:59`
  still `edify check <file-or-dotted-target> --json`.
  `docs/references/cli-and-package.md:103-112` still ends "*Open gate:* one
  throwaway skill echoing the placeholder confirms `DATA`…". `CLAUDE_PLUGIN_DATA`
  appears only in `plugin/bin/bootstrap-venv.sh`. Frame: **R4**. R2 carries job
  (1) but does not name this site.

### Job (2): sweep / review-scoping exit condition

No finding. `verify-summary.md` records the absence explicitly.

### Job (3): `/proof` verdict prompt

That job has since shipped (`5f860e07 … /proof verdicts`), without settling the
following finding.

- **`proof` C1.** Three callers say `/proof` dispatches a corrector, but `/proof`
  has no dispatch, and the callers disagree on the trigger (revise/kill vs
  apply). Source: `verify-proof.md`. Evidence: `proof/SKILL.md:167-173` "apply" is
  still display → confirm → batch-edit → return, with no dispatch. `Agent` is
  still in `allowed-tools` (:8). The callers still make the claim at
  `design/SKILL.md:112` and `:130` ("dispatched by /proof on revise/kill"),
  `design/references/write-outline.md:222` and `write-design.md:70` ("on
  'apply'"). Frame: **R4** (named).
- **`design` C2.** Same defect as proof C1; one fix closes both. Source:
  `verify-design.md`. Evidence as above. Frame: **R4**.

### Job (4): corrector-family dedup (pilfer defect 21)

- **`orchestrate` M5.** "The corrector never commits" is asserted only by
  callers. `corrector.md` carries no prohibition and holds `Bash`, and the file
  is at its 682-line ceiling. Source: `verify-orchestrate.md`. Evidence: a grep
  of `plugin/agents/corrector.md` for "commit" returns only scope and template
  text (:222, :243, :251, :317, :413, :456-477). `scripts/check_line_limits.allow`
  still pins `corrector.md` at 682, and it measures 682. Frame: **R6** ("the
  missing 'corrector never commits' prohibition"), also R4.

### Job (5): deliverable-review report contract and findings routing

- **`deliverable-review` C3.** The skill says it does not queue follow-up work,
  against D-58 (every finding resolves to a fix or tracked task) and D-60
  (route findings to `/design`). Source: `verify-deliverable-review.md`.
  Evidence: `deliverable-review/SKILL.md:191` "skill does not queue follow-up work
  or record lifecycle state". `docs/references/deliverable-review.md:53` (D-58)
  and `:65` (D-60) are unchanged. Frame: **R4** only. No R-bullet names job (5)
  or D-58/D-60. R6's report-head/finding-shape item covers report shape, not
  routing.

### No pending job

- **`design` C1.** The Defect route names a `structured-bugfix` workflow that
  does not exist. Source: `verify-design.md`. Evidence: `design/SKILL.md:135` and
  `design/references/triage.md:33`. No other hit in `plugin/` or `docs/`. Frame:
  **R4**.
- **`design` M5.** It is undecided whether `write-outline.md` or
  `research-protocol.md` owns A.5's output spec, and the conditional read is
  defeated. Source: `verify-design.md`. Evidence: `write-outline.md:139`
  conditional read, then an unconditional read at `:157`. The escape-hatch
  paragraph is still in both files (`write-outline.md:162`,
  `research-protocol.md:62`). Frame: **R4**.
- **`design` M6.** `triage-feedback.sh` checks only Simple and Complex, so
  Moderate and Defect always read "match". Source: `verify-design.md`. Evidence:
  `plugin/bin/triage-feedback.sh:48`, `:54` branch on Simple and Complex, with a
  bare `else` at :60. `triage.md:106` still offers Defect. Frame: **R4**.
- **`design` m4.** A.0/A.2.5/C.4.5 numbering accretion; renumbering would break
  inbound references. Source: `verify-design.md`. Evidence: `design/SKILL.md:32`
  "### 0. Complexity Triage". `write-outline.md` has A.0, A.2.5, "A.3-4" and an
  unnumbered Post-Outline re-check (:166). `write-design.md:66` has C.4.5.
  Frame: **R4**.
- **`formalize` 1.** The skill says `error` means "no contract", but a
  contract-free target reports `verified`. Also, `vacuity_warning` is not a
  no-contract signal. Source: `verify-formalize.md`. Evidence:
  `formalize/SKILL.md:84-85` still "A common cause is a target with no contract
  (CrossHair analyzed nothing)".
  `docs/superpowers/design/invariant-guided-verify-loop.md:85` L1 still defers to
  "add a contract on `error`". Frame: **R4**.
- **`formalize` 8.** Should the budget discipline go inline or in a new
  `references/` node? Source: `verify-formalize.md`. Evidence:
  `plugin/skills/formalize/` holds only `SKILL.md`. Frame: **R4**.
- **`ground` 3.** No precedence between `grounding-criteria.md`'s two scope
  selectors. Source: `verify-ground.md`. Evidence: `grounding-criteria.md:52`
  (question shape) and `:125` (topic class), with no precedence stated. Frame:
  **R4**.
- **`ground` 8.** The description has no exclusion clause. Source:
  `verify-ground.md`. Evidence: `ground/SKILL.md:3-7`, triggers only. Frame:
  **R4**.
- **`ground` 10.** "design a methodology" overlaps `/design`'s "planning
  requests". Source: `verify-ground.md`. Evidence: `ground/SKILL.md:6`,
  `design/SKILL.md:6-7`. Frame: **R4**.
- **`ground` 13.** Cites `agents/learnings.md`, which is over its own limit.
  Source: `verify-ground.md`. Evidence: still cited at `grounding-criteria.md:109`.
  The file is 195 lines against its "Soft limit: 80 lines" (`agents/learnings.md:5`).
  **Half resolved:** the `/codify` routing is gone, replaced in `10b509e2 🔧 sweep
  the non-design open items …`. Frame: **R4** (learnings-retirement fork named).
- **`proof` M8.** `p:` semantics is cited twice and defined nowhere. Source:
  `verify-proof.md`. Evidence: `proof/SKILL.md:162`,
  `proof/references/item-review.md:115`. Frame: **R4** (named).
- **`proof` M9.** `agents/learnings.md` is a write target with no absence
  handling in a consuming repo. Source: `verify-proof.md`. Evidence:
  `proof/SKILL.md:161`, `item-review.md:114`. Frame: **R4** (named).
- **`recall` M1.** How much of `gitlore:recall` edify's recall still duplicates.
  Source: `verify-recall.md` (README decision 3's surviving half). Evidence:
  `recall/SKILL.md` still carries the 5-entry ceiling (:77), "unsure means
  exclude" (:79) and the single-message batch Read (:84). The description has no
  `gitlore:recall` exclusion. Frame: **R4**.
- **`requirements` m4 / `runbook` m13 (two findings, one fork).** "D+B" is
  unexpanded jargon: expand it at every site, or route once from a shared
  fragment. Source: `verify-requirements.md`, `verify-runbook.md`. Evidence:
  13 sites across 9 files in `plugin/skills/`:
  - `runbook/SKILL.md` ×3
  - `design/SKILL.md` ×2
  - `build/SKILL.md` ×2
  - one each in `requirements/SKILL.md`, `proof/SKILL.md`, `triage.md`,
    `write-outline.md`, `finishing.md` and `review-dispatch-template.md`

  None routes to D-52. Frame: **R4**.
- **`inline` m7.** The `build/` sites of the same "D+B" fork. Its status is
  migrated, but the fix is the fork above. Source: `verify-inline.md`. Evidence:
  the 2 hits in `build/SKILL.md` (from the D+B count above). Frame: **R4**, via
  requirements m4 / runbook m13.
- **`review` m13.** Should the mandatory Positive Observations section stay?
  Source: `verify-review.md`. Evidence: `review/references/review-template.md:45`.
  Frame: **R4**.
- **`review` m15.** Two runbook-only axes load on every code review. Source:
  `verify-review.md`. Evidence: `review/references/review-axes.md:33`, `:41`
  "(when reviewing runbooks/plans)". Frame: **R4**.
- **`review` m17.** `/review` has no recall checkpoint. Source:
  `verify-review.md`. Evidence: no `Skill` or `recall` in `review/SKILL.md` or
  its references. Frame: **R4**.
- **`runbook` M4 / m16 (two findings, one decision).** §3 Self-Check duplicates
  `runbook-format.md`, and two of its rules have drifted names. Source:
  `verify-runbook.md`. Evidence: `runbook/SKILL.md:110` "No vacuous items"
  vs `runbook-format.md:124` "No setup-only items". `:114` "Prose atomicity"
  vs `:132` "No split prose edits". Frame: **R4**.
- **`deliverable-review` m6.** ✅/❌ glyphs in the example's Gap Analysis; nothing
  in-repo governs them. Source: `verify-deliverable-review.md`. Evidence:
  `deliverable-review/references/example-report.md:191-204`. Frame: **R4**.

### Disputed (the three R4 counts)

- **`ground` 9.** The review says the bare trigger "ground" auto-fires; the
  dispute is that no measurement backs this. Source: `verify-ground.md`.
  Evidence: `ground/SKILL.md:5` still lists `"ground"`. The dispute stands
  unchanged. Frame: **R4**.
- **`recall` m3.** The review calls "the one procedure" false; the dispute is
  that a documented override is still one procedure. Source: `verify-recall.md`.
  Evidence: `recall/SKILL.md:15` unchanged. Frame: **R4**.
- **`formalize` 11.** The review calls the "function whose correctness matters"
  trigger undetectable; the dispute is that the clause is the skill's purpose
  statement. Source: `verify-formalize.md`. Evidence: `formalize/SKILL.md:7`
  unchanged. Frame: **R4**.

## STILL-OPEN, missing from frame

### Migrated defects (`verify-summary.md` §Migrated-defect targets; no pending job)

`apply-batch-3.md` confirms these were not applied ("nothing to apply from those
two reports"). R4 counts only open-design and disputed, so the frame carries
none of them. The fix text is in `verify-inline.md` and `verify-orchestrate.md`.

Changed-files reference point. The reports treat this as one wound:
orchestrate C1 + M8, and inline M2 + m10 + m12.

- **`orchestrate` C1.** The phase-boundary changed-files list is a bare
  `git diff --name-only`, which is empty after every committed dispatch, so the
  halt fires on well-behaved runs. Evidence: `build/references/phase-boundary.md:9`,
  with the halt at :17-19. The inherited copy is at
  `plugin/fragments/review-requirement.md:125`.
- **`orchestrate` M8.** The phase-boundary halt checks only IN, OUT and changed
  files. It omits Requirements summary and Constraints, which
  `review-requirement.md` requires. Evidence: `phase-boundary.md:17-19`.
- **`inline` M2.** The review template has no `**Constraints:**` block, and its
  Changed files is the whole baseline diff, not the group's share. Evidence:
  `build/references/review-dispatch-template.md:20`. No `Constraints:` block in
  the file.
- **`inline` m10.** The finishing review scope is "the uncommitted changes",
  which is empty under committed dispatches. Evidence:
  `build/references/finishing.md:31`.
- **`inline` m12**, partial. Half resolved in `5594a753`: `finishing.md:45` now
  commits each group's report and fixes. Still open: no `verify-step.sh` run
  between that commit and §2.

Dispatch contracts:

- **`inline` M1.** Two report-path rules, each calling itself the only rule.
  Evidence: `dispatch-composition.md:39-40` ("the only rule for report paths")
  vs `review-dispatch-template.md:89` ("one rule — …/review-<group>.md").
- **`inline` m15.** Two return contracts. Evidence:
  `review-dispatch-template.md:42`, `:136` ("UNFIXABLE: …" on failure) vs
  `dispatch-composition.md:46` (`blocked: <reason>`).
- **`inline` m16**, first half. No slot for the `plugin-dev:agent-development`
  criteria that `review-requirement.md:53` says the dispatch prompt names.
  Evidence: no `agent-development` in `review-dispatch-template.md`.
- **`inline` m6.** The planning-artifact routing paragraph is duplicated.
  Evidence: `finishing.md:34-38` and `review-dispatch-template.md:100-104`, both
  ending "`runbook-corrector` rejects anything that is not `runbook.md`."
- **`inline` m11.** UNFIXABLE handling skips the validation protocol, and there
  is no re-review after report-only fixes. Evidence: `finishing.md:42` "UNFIXABLE
  in any report → STOP and surface it". The protocol is at
  `review-requirement.md:190`.

Triage script:

- **`inline` M3.** `reports_count` counts review reports, so a reviewed Simple
  job reads `underclassified`. `finishing.md` does not handle the
  `WARNING: No corrector report` line. Evidence: `triage-feedback.sh:21`
  excludes only `design-review*`, `outline-review*` and `recall-*`. The warning
  is at :102, and `finishing.md:58-59` handles only divergence and match.

Tool availability and escalation:

- **`orchestrate` M1.** `TaskOutput` is declared and prescribed, but it does not
  resolve in the deferred tool set. Evidence: `build/SKILL.md:8` `allowed-tools`
  lists it. The procedure moved to `build/references/escalation.md:33` ("check
  with `TaskOutput`").
- **`orchestrate` m7.** `TaskStop` is presented as procedure, against the
  fragment's "do not treat it as the guard until probed". Evidence:
  `build/SKILL.md:8`, `escalation.md:33` ("stop the task"),
  `escalation-acceptance.md:70`.
- **`orchestrate` M7.** `/build` remediates a dirty tree while the fragment
  prescribes an unconfirmed `git clean -fd`. Evidence: `escalation.md` exit-1
  remediation (resume, then fresh artisan) states no override. The fragment is
  unchanged at `escalation-acceptance.md:48-49` ("Revert to last clean commit:
  `git checkout -- . && git clean -fd`"). `escalation.md:35` still cites that
  fragment.
- **`inline` m2.** `delegation.md` prescribes
  `git status --porcelain && just lint` as the correct pattern; the `&&` guards
  nothing. Evidence: `plugin/fragments/delegation.md:112-113`.

`build/SKILL.md` body:

- **`orchestrate` M4.** No step commits a corrector's fixes before post-item
  verification when a general item is itself a review. Evidence:
  `build/SKILL.md:122` routes `edify:corrector` for such items. §4.4 covers "a
  slice's code review once its commit lands" and "any general or directly
  executed item", with no commit step for the general-review case.
- **`orchestrate` C2**, partly mitigated. Nothing says where `<job>` comes from
  on a fresh-session resume. Evidence: `build/SKILL.md:27` `ls plans/<job>`. The
  resume section (`escalation.md` §Resuming) starts from `git log`, not the
  job. `.claude/handoff-task.md` is named in `build/` only as something `/build`
  never writes (`finishing.md` §3.3).
- **`orchestrate` m3.** "Checkpoint form" is coined and never defined. Evidence:
  `build/SKILL.md:115`, `phase-boundary.md:14`.
- **`orchestrate` m4.** A redundant `verify-step.sh` run at the phase boundary,
  right after §4.4's run. Evidence: `phase-boundary.md:8`.
- **`orchestrate` m5.** Untracked files count as dirt by design, but nothing
  says so. Evidence: `verify-step.sh:5-9` exempts only ` M memory`.
  `build/SKILL.md:53` DIRTY verdict gives no rule.
- **`inline` m9.** Sentence fragment. Evidence: `build/SKILL.md:93` "Patterns for
  implementing this, not for classifying it."

### Disputed half-finding outside R4's three

- **`inline` m16**, `argument-hint` half. The review asks for an
  `argument-hint`; the dispute is that no edify skill declares that key, so its
  absence is the convention. Source: `verify-inline.md`. Evidence: a grep for
  `argument-hint` in `plugin/skills/` finds nothing. The dispute stands.

### `apply-review.md` §Accepted, not fixed

- **`runbook` §1 substeps.** The `a.`–`e.` substeps are not a Markdown list and
  render as paragraphs. Evidence: `runbook/SKILL.md:50`, `:55`, `:60`, `:66`,
  `:70`.
- **§-citations of bold labels rather than headings.** Evidence:
  `design/SKILL.md:152` §D-26, `item-review.md:103` §Verdicts,
  `deliverable-review/SKILL.md:178` §D-56.
- **`write-design.md` §C.1 recall diff.** It points at `research-protocol.md`
  §A.5, whose triggers are A.5's, so C.1's own trigger list (approach
  commitment, revised scope, rejected alternatives) is lost. Evidence:
  `write-design.md:7-8`.
- **Example-report inventory.** Two rows read `not recorded` (residual of fix
  #11). Evidence: `deliverable-review/references/example-report.md:18-19`.

### Out-of-sweep items the verify reports named

- **`ground` 12, `CLAUDE.md` copy.** The non-runnable
  `edify list | extract <prefix> | collect` pipeline was fixed in the skill.
  The report left the `CLAUDE.md` copy "outside this sweep". Source:
  `verify-ground.md` §Cross-file links. Evidence: `CLAUDE.md:248` still
  "`edify list | extract <prefix> | collect`".
- **`runbook` recall re-invocation.** A second `Skill(edify:recall)` call where
  `recall/SKILL.md` says to run the loaded procedure inline. It is the same
  pattern as requirements m3, which was applied, and was not filed as a runbook
  finding. Source: `verify-requirements.md` m3, `verify-summary.md`
  cross-cutting table. Evidence: `runbook/SKILL.md:71` "Invoke
  `Skill(skill: "edify:recall")` (no topic —".

## RESOLVED-SINCE

- **`orchestrate` M2** (agent half). `tdd-auditor.md` fell back to reading
  subagent transcripts. Source: `verify-orchestrate.md`, `apply-review.md` #5,
  #8. Evidence: no `transcript` or `subagents/` left in
  `plugin/agents/tdd-auditor.md`. `:207` now returns
  `blocked: report missing for <dispatch name>`. Landed in
  `5594a753 🐛 sweep the non-design remaining items — gates, TDD rules,
  skill-review edits`.
- **`requirements` m10.** A plain-scalar description, skipped on line budget.
  Source: `apply-batch-2.md`. Evidence: `requirements/SKILL.md:3` is now
  `description: >-`. Landed in `5f860e07 🐛 deliverable review fixes, skill hub
  splits, /proof verdicts, D-87 and D-9 rewired`.
- **Allowlist ceilings not ratcheted down** for shrunk files (design, proof,
  review, requirements). Source: `apply-batch-1.md`, `apply-batch-2.md`.
  Evidence: `scripts/check_line_limits.allow` now lists only the three
  correctors. All ten `SKILL.md` files are at or under 199 lines. Changed in
  `5f860e07`.

## OBSOLETE

None. No open item targets a file that no longer exists. Every open finding
against the retired `inline` and `orchestrate` skills was already re-targeted to
its `build/` successor by the verify reports, and those successor sites exist.

## UNCLEAR

- **`runbook` M7**, blocking half; also the mechanism half of `review` C2. Both
  rest on `allowed-tools` granting rather than restricting. Source:
  `verify-runbook.md`, `verify-review.md`. Check: a grep of `docs/` and
  `memory/` for an `allowed-tools` grant/restrict statement found nothing, so
  the tree cannot settle it. The mechanical halves of both findings were
  applied (`runbook/SKILL.md:122-124` runs `just precommit`).

## Counts

| Classification | Items |
|---|---|
| STILL-OPEN, in frame | 31 (27 open-design, 3 disputed, 1 migrated riding the D+B fork) |
| STILL-OPEN, missing from frame | 28 (21 migrated, 1 disputed half, 4 apply-review accepted, 2 out-of-sweep) |
| RESOLVED-SINCE | 3 |
| OBSOLETE | 0 |
| UNCLEAR | 1 |
