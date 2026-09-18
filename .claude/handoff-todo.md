## Open decisions

- **Whether `route-to-execution.md`'s preconditions are meant to bind the
  `/runbook` branch** (review M-3). The scope sentence binds both preconditions
  to every branch the node routes; the "edit targets are named" rationale is
  scoped to the no-runbook case, so a Production job whose design names no
  section-level targets is bounced to A.5/C.1 instead of to `/runbook`, whose
  job that is. `docs/changelog.md:29-31` records the widening as deliberate.
  Either the reach narrows, or the rationale stops justifying it by the
  no-runbook case.
- **Whether the review-scoping memories become a `craft` skill.** Four facts
  share one trigger — about to scope a review, sweep or audit:
  `ddaanet/reference-audit-after-a-move`,
  `ddaanet/audit-a-contract-across-its-surfaces`,
  `ddaanet/examine-evidence-drift` and the project-local
  `feedback-stale-claims-survive-reference-sweeps`. `inbox/recall-skill.md`
  names group migration to a skill as the index-pressure valve, and
  `ddaanet/extracting-memory-into-skills` carries the migration checklist.
  Decide whether that is its own `/edify:design` job, and whether four facts
  is enough to carry a skill description's always-on cost.
- **`memory/MEMORY.md` is at 105% of its 25600-byte budget.** Past 24.4KB
  Claude Code's loader silently truncates the tail, so index lines beyond the
  cutoff never reach a session. Decide whether to compress existing hooks,
  move facts into tier carriers, or raise the budget. `/gitlore:index-audit` is
  the pass that acts on it, and `gitlore:memory-writing` §7 rules that being
  over the cap is never a reason to under-trigger a fact — so the index grows
  on demand until that audit runs.
- **`inbox/brief-review-feeds-back-into-design.md`** — descoped from
  `provenance-reach-and-sweep` by decision, still unanswered. It proposes three
  changes to the deliverable-review *report contract*: co-location grouping
  alongside the severity sort, per-reviewer counts where two layers merge, and a
  structural site list on any finding naming N sites. The last one just gained a
  fresh instance — review M-6, where a fix closed one of three sites pointing at
  the same target. Its recommendation is the authoring agent's input, not a
  decision. Decide whether it becomes its own `/edify:design` job.
- **Nothing implements the findings-routing rule** the last passes followed by
  hand — criticals to a fresh design-to-deliverable round, majors and minors
  to a direct `/build` flow. Decide where it lives:
  `deliverable-review/SKILL.md` currently ends by disclaiming exactly this
  ("the skill does not queue follow-up work"), so it may belong in `/design`'s
  Phase 0 instead.
- **Whether the sweep mechanism M-3 descoped becomes its own job.** Three
  consecutive passes now show the same shape: a sweep scoped to the files under
  edit reports clean while the defect form persists outside it. `/proof` found
  P-1 and P-2 past the first deliverable review; the build's skill review found
  B and C by grepping for the defect's *form*; this review's M-6 found five more
  "per X" pointers tree-wide, two aimed at the target C had just fixed. Decide
  whether that becomes a design job against the sweep's exit condition.

## Remaining

- Work the deliverable review's remaining majors: M-1/M-2, the correctors'
  Provenance repair directive (it overwrites a correct `Derived from:` and bars
  the one safe repair, with D-80 carrying the same over-broad rationale); M-4,
  the consumer never checking the inheritance rule; M-6, the tree-wide "per X"
  pointer sweep. M-5 is the write-outline gate item below.
- The review's five minors — `research-protocol.md:41`'s "as shown" covering a
  first-pass field value, `design/SKILL.md:174`'s singular "B gate",
  `route-to-execution.md:30`'s mislabelled catch-all `ELSE`,
  `docs/changelog.md:29-31`'s over-wide precondition claim, and the corrector
  line counts under item 5.
- Give `write-outline.md`'s multi-sub-problem gate a branch for a sub-problem
  found not-routable after confirmation. `route-to-execution.md` now defers that
  decision to the gate, and the gate carries none — its "If insufficient" branch
  is evaluated before the node is read. Observation A in
  `plans/provenance-reach-and-sweep/reports/review-skills.md`, review M-5;
  deferred by decision, needs a `/design` pass rather than a wording fix.
- `/proof`'s verdict prompting is too formal. Replace the
  `(a)pprove (r)evise (k)ill (s)kip` prompt in `plugin/skills/proof/SKILL.md`
  §Item Iteration with: propose a verdict conversationally, show the amended
  item, capture the verdict from the reply. Couples to
  `references/item-review.md`; route through `/design`.
- Wire a hard-wrapping markdown formatter into the validation gate. `just
  format` (`plugin/portable.just:117-132`) runs only `ruff` and `docformatter`,
  while `memory/ddaanet/shared-claude.md` prescribes `rumdl` with MD013 reflow
  at 80 columns ahead of the line-count checker. Both correctors read as under
  the 400 cap only because of this: 396 and 398 lines, but 435 and 456 once
  their character counts are divided by 80.
- The remaining `plans/skill-reviews/` findings — 24 critical / 74 major / 91
  minor across eleven skills, none actioned. At least one is already fixed in
  source, so verify each against the file before acting.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable 'when
  reviewing runbooks/plans' criteria in `corrector.md` ~293-304; the corrector
  family's `Skill(edify:recall)` (`corrector.md:184`,
  `runbook-corrector.md:59`) against the by-path recall rule;
  `review-requirement.md`'s routing table still routing 'plans' to
  `edify:corrector` with no outline/runbook rows (defers to D-26), and routing
  'Design documents' to `edify:design-corrector`, whose definition scopes it to
  `plans/<job>/design.md` — an edit to `docs/design.md` has no fitting row.
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which
  have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Extend `/recall` to load skills as well as memory files, per
  `inbox/recall-skill.md`. A recall artifact already carries a `## Skills to
  load before executing` section, and bodies resolve under
  `~/.claude/plugins/cache/<owner>/<plugin>/<version>/skills/<name>/SKILL.md`.
  What is missing is the rule in `plugin/skills/recall/SKILL.md`.
