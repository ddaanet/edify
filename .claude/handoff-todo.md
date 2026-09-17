## Open decisions

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
  structural site list on any finding naming N sites. Its recommendation is the
  authoring agent's input, not a decision. Decide whether it becomes its own
  `/edify:design` job.
- **Nothing implements the findings-routing rule** the last two passes followed
  by hand — criticals to a fresh design-to-deliverable round, majors and minors
  to a direct `/build` flow. Decide where it lives:
  `deliverable-review/SKILL.md` currently ends by disclaiming exactly this
  ("the skill does not queue follow-up work"), so it may belong in `/design`'s
  Phase 0 instead.
- **Whether the sweep mechanism M-3 descoped becomes its own job.**
  `provenance-reach-and-sweep` fixes the three stale hits and leaves the
  mechanism alone, by decision. The evidence has since grown: that job's
  `/proof` found two further reach defects no grep for the retired name could
  reach, and `memory/ddaanet/reference-audit-after-a-move.md` now carries the
  rule — pair the name grep with one for the defect's *form*, each with its own
  exit condition. Decide whether that becomes a design job against the sweep's
  exit condition.

## Remaining

- `/proof`'s verdict prompting is too formal. Replace the
  `(a)pprove (r)evise (k)ill (s)kip` prompt in `plugin/skills/proof/SKILL.md`
  §Item Iteration with: propose a verdict conversationally, show the amended
  item, capture the verdict from the reply. Couples to
  `references/item-review.md`; route through `/design`. The provenance-reach
  proof run is fresh evidence — eleven items, the formal prompt every time, and
  every reply came back as plain prose.
- Wire a hard-wrapping markdown formatter into the validation gate. `just
  format` (`plugin/portable.just:117-132`) runs only `ruff` and `docformatter`,
  so no markdown reflow happens, while `memory/ddaanet/shared-claude.md`
  prescribes `rumdl` with MD013 reflow at 80 columns ahead of the line-count
  checker. Line counts in skill bodies and plans are unverified against the
  400/~200 caps until it exists.
- The remaining `plans/skill-reviews/` findings beyond the five settled
  decisions — 24 critical / 74 major / 91 minor across eleven skills, none
  actioned. The proof pass found at least one already fixed in source, so
  verify each against the file before acting.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable 'when
  reviewing runbooks/plans' criteria in `corrector.md` ~293-304; the corrector
  family's `Skill(edify:recall)` (`corrector.md:184`,
  `runbook-corrector.md:59`) against the by-path recall rule;
  `review-requirement.md`'s routing table still routing 'plans' to
  `edify:corrector` with no outline/runbook rows (defers to D-26).
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which
  have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Extend `/recall` to load skills as well as memory files, per
  `inbox/recall-skill.md`. The proof pass ran the extension by hand and it
  worked: a recall artifact already carries a `## Skills to load before
  executing` section, and bodies resolve under
  `~/.claude/plugins/cache/<owner>/<plugin>/<version>/skills/<name>/SKILL.md`.
  What is missing is the rule in `plugin/skills/recall/SKILL.md`.
