## Open decisions

- `plans/build-skill/outline.md` is 589 lines against the 400-line soft cap -- hard-wrapped, so the count is honest, and stripping the proof pass's provenance into `inventory.md` §0 only bought 25 lines. The rest is execution content. Split or accept the overage? The seam is **build the new skill** (~250 lines, now executed) versus **update everything that pointed at the old ones** (~300 lines, still to run); a reader doing one does not need the other open.

## Remaining

- Another pass on `plugin/skills/build/SKILL.md` (217 lines). The hub now routes to opt-in nodes for the once-firing steps, each routing line naming its trigger.
- Finish `plans/build-skill/outline.md` -- the reference sweep across /design, /runbook, `plugin/fragments/`, `plugin/README.md`, `README.md`, `CLAUDE.md`, `docs/design.md`, `docs/changelog.md` and `memory/workflow-pipeline-revival.md`, in the plan's order. Cite by string, never by line: inventory §0 records where its own line cites were wrong, and report claims need verifying against the file before acting.
- **Retire continuation-passing entirely** -- settled 2026-09-17, no longer deferred. The `continuation:` frontmatter blocks and `## Continuation` sections in /design and /runbook, and `plugin/fragments/continuation-passing.md` itself. /build already omits it, including from its `§References` index.

### /design skill work

- **Remove /design's direct-execution path** -- the Phase B / C.5 execution-ready branch that bypasses /runbook and implements inside the design session. /build is now the lean hub that routes to subagent ceremony only when needed, so the simple case is fast there instead of being special-cased in /design. This is the same seam that wrongly justified the /inline vs /orchestrate split. Anything coming out of /design has requirements, so it should be checked by /edify:deliverable-review.
- **Design artefacts derived from a deliverable-review should record the review and the initial commit base.** A second pass and its own deliverable-review then know to review the complete diff from the original base, not just the changes since the last commit. Without it, pass 2's review sees only the fixes and cannot judge whether the whole deliverable satisfies its requirements.

### Other

- deliverable-review follow-up (skill-review decision 2, second half): Criticals route to a fresh design-to-deliverable round, Majors and Minors to a direct /build flow. Depends on /build accepting work with no runbook.
- The remaining `plans/skill-reviews/` findings beyond the five settled decisions -- 24 critical / 74 major / 91 minor across eleven skills, none actioned. The proof pass found at least one already fixed in source, so verify each against the file before acting.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable 'when reviewing runbooks/plans' criteria in `corrector.md` ~293-304; the corrector family's `Skill(edify:recall)` (`corrector.md:184`, `runbook-corrector.md:59`) against the by-path recall rule; `review-requirement.md`'s routing table still routing 'plans' to `edify:corrector` with no outline/runbook rows (defers to D-26).
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Extend /recall to load skills (`craft`, `plugin-craft`, `sandbox-lies`) as well as memory files; the recall artifact format must allow naming them. Rationale in `inbox/recall-skill.md`.
- `memory/MEMORY.md` needs a `/gitlore:index-audit` pass. Measured 2026-09-17: 26661 bytes against the 25600-byte loader cap, cutoff falling at line 86 of 88 -- so two entries are silently dropped from every session, not the whole tail.
