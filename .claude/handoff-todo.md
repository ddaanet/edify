## Open decisions

- Build-skill proof item 6 — does the merge also supply the `general` item format that `plugin/skills/runbook/references/runbook-format.md` has never specified (inventory C1)? `general` is the default phase type, yet every content section of that file is tdd-shaped. Cheap while that file's phase-type line is already being rewritten; genuinely separate work otherwise.
- Build-skill proof item 9 — does `plans/<job>/inline-plan.md` become `build-plan.md`, with `plugin/skills/design/references/write-inline-plan.md` → `write-build-plan.md` and its status line `inline-planned → /inline` becoming `build-planned → /build`? Correct by the stale-name argument, but it reaches into `/design` and `/proof` beyond the merge proper.

## Remaining

- Proof, then execute, `plans/build-skill/inline-plan.md` — the `/inline` + `/orchestrate` → `/build` merge. Exit condition is a whole-tree grep for the old names with every hit classified accurate-or-stale, never a reading of the diff; expect the count to exceed the inventory's. `/build` is not invocable until a `handoff:restart`, since skill listings resolve at startup.
- deliverable-review follow-up (skill-review decision 2, second half): Criticals route to a fresh design-to-deliverable round, Majors and Minors to a direct `/build` flow. Depends on `/build` accepting work with no runbook.
- The remaining `plans/skill-reviews/` findings beyond the five settled decisions — 24 critical / 74 major / 91 minor across eleven skills, none actioned.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable 'when reviewing runbooks/plans' criteria in `corrector.md` ~293–304; the corrector family's `Skill(edify:recall)` (`corrector.md:184`, `runbook-corrector.md:59`) against the by-path recall rule; `review-requirement.md`'s routing table still routing 'plans' to `edify:corrector` with no outline/runbook rows (defers to D-26).
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Extend `/recall` to load skills (`craft`, `plugin-craft`, `sandbox-lies`) as well as memory files; the recall artifact format must allow naming them. Rationale in `inbox/recall-skill.md`.
- `memory/MEMORY.md` sits at ~104% of the 25600-byte loader budget, so entries past the cutoff are silently dropped from every session. Needs a `/gitlore:index-audit` pass.
