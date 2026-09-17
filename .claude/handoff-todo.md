## Open decisions

- **`memory/MEMORY.md` is at 105% of its 25600-byte budget.** Past 24.4KB
  Claude Code's loader silently truncates the tail, so index lines beyond the
  cutoff never reach a session. Decide whether to compress existing hooks,
  move facts into tier carriers, or raise the budget.
- **`inbox/brief-review-feeds-back-into-design.md`** — descoped from
  `provenance-reach-and-sweep` by decision, still unanswered. It proposes three
  changes to the deliverable-review *report contract*: co-location grouping
  alongside the severity sort, per-reviewer counts where two layers merge, and
  a structural site list on any finding naming N sites. Its recommendation is
  the authoring agent's input, not a decision. Decide whether it becomes its
  own `/edify:design` job.
- **Nothing implements the findings-routing rule** the last two passes
  followed by hand — criticals to a fresh design-to-deliverable round, majors
  and minors to a direct `/build` flow. Decide where it lives:
  `deliverable-review/SKILL.md` currently ends by disclaiming exactly this
  ("the skill does not queue follow-up work"), so it may belong in `/design`'s
  Phase 0 instead.

## Remaining

- Restart the Claude Code process before `/edify:build` — a `/clear` does not
  reload plugin bodies. The `/edify:design` body loaded in this process is the
  pre-change version (reads "execution-ready (B gate or C.5)" at §Routing out,
  no Provenance clause at `:133`), and every skill body this job edits has the
  same exposure. `/handoff:restart` does it.
- `/proof`'s verdict prompting is too formal. Replace the
  `(a)pprove (r)evise (k)ill (s)kip` prompt in `plugin/skills/proof/SKILL.md`
  §Item Iteration with: propose a verdict conversationally, show the amended
  item, capture the verdict from the reply. Couples to
  `references/item-review.md`; route through `/design`.
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
- Extend /recall to load skills (`craft`, `plugin-craft`, `sandbox-lies`) as
  well as memory files; the recall artifact format must allow naming them.
  Rationale in `inbox/recall-skill.md`.
