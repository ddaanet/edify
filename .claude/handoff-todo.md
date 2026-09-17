## Open decisions

- `plans/build-skill/outline.md` is 589 lines against the 400-line soft cap — hard-wrapped, so the count is honest, and stripping the proof pass's provenance into `inventory.md` §0 only bought 25 lines. The rest is execution content. Split or accept the overage? The real seam is **build the new skill** (new skill, reference nodes, moved references, carried defect, deletions — ~250 lines) versus **update everything that pointed at the old ones** (phase type, executable refs, prose refs, artifact-kind removal, design record, memory — ~300 lines). They execute in that order, the second depends on the first, and a reader doing one does not need the other open.

## Remaining

- Execute `plans/build-skill/outline.md` — the `/inline` + `/orchestrate` → `/build` merge. Proofed 2026-09-17, all 14 items revised; `inventory.md` §0 records the six inventory claims the proof found wrong. Exit condition is a whole-tree grep for the old names with every hit classified accurate-or-stale, never a reading of the diff. `/build` is not invocable until a `handoff:restart`, since skill listings resolve at startup.

### `/design` skill work

- **Remove `/design`'s direct-execution path** — the Phase B / C.5 execution-ready branch that bypasses `/runbook` and implements inside the design session. `/build` should be the lean hub that routes to subagent ceremony only when needed, so the simple case is fast there instead of being special-cased in `/design`. This is the same seam that wrongly justified the `/inline`//`/orchestrate` split: a fast path carved out of the general one, which then diverges. Anything coming out of `/design` has requirements, so it should be checked by `/edify:deliverable-review`. Depends on the build-skill merge landing first.
- **Retire continuation-passing from `/design` and `/runbook`** — the `continuation:` frontmatter blocks, the `## Continuation` sections, and `plugin/fragments/continuation-passing.md` itself. The machinery over-compensated for agents stopping at the end of a skill, which no longer happens; all 16 of its `/inline`//`/orchestrate` citations are self-references, all four cooperative skills declare an identical `default-exit`, and the fragment says nothing enforces it from outside. Continuations have a future as handoff-plugin-driven *handoff-and-continue* and *precompact-commit-and-continue*, conditioned on context usage — a different mechanism, so this one is retired rather than kept as an extension point. The build-skill merge only stops `/build` participating.
- **Design artefacts derived from a deliverable-review should record the review and the initial commit base.** A second pass and its own deliverable-review then know to review the *complete* diff from the original base, not just the incremental changes since the last commit. Without it, pass 2's review sees only the fixes and cannot judge whether the whole deliverable now satisfies its requirements.

### Other

- deliverable-review follow-up (skill-review decision 2, second half): Criticals route to a fresh design-to-deliverable round, Majors and Minors to a direct `/build` flow. Depends on `/build` accepting work with no runbook.
- The remaining `plans/skill-reviews/` findings beyond the five settled decisions — 24 critical / 74 major / 91 minor across eleven skills, none actioned. The proof pass found at least one already fixed in source, so verify each against the file before acting.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable 'when reviewing runbooks/plans' criteria in `corrector.md` ~293–304; the corrector family's `Skill(edify:recall)` (`corrector.md:184`, `runbook-corrector.md:59`) against the by-path recall rule; `review-requirement.md`'s routing table still routing 'plans' to `edify:corrector` with no outline/runbook rows (defers to D-26).
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Extend `/recall` to load skills (`craft`, `plugin-craft`, `sandbox-lies`) as well as memory files; the recall artifact format must allow naming them. Rationale in `inbox/recall-skill.md`.
- `memory/MEMORY.md` needs a `/gitlore:index-audit` pass. Measured 2026-09-17: 26661 bytes against the 25600-byte loader cap, cutoff falling at line 86 of 88 — so two entries are silently dropped from every session, not the whole tail.
