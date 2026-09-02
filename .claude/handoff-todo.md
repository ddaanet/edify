## Remaining

- Dogfood the simplified pipeline end to end (`/design` → `/runbook` → `/orchestrate`) on a real plan; L-6 records it as unexercised, and FR-5's slice-batching claims stay unvalidated until it supplies counts. The refactor-dispatch naming, the two-commit-per-reviewed-slice rule, and this session's contract fixes were all settled on paper.
- Consolidate `memory/MEMORY.md` (~32.4 KB against the 24.4 KB loader cutoff) via `/gitlore:index-audit` — retire, don't shorten — and fix `docs/design.md` L-5's stale "~28.9 KB" in the same pass. That is Major 10 of the deliverable review, the one finding left open.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable "when reviewing runbooks/plans" criteria in `corrector.md` ~293–304; the corrector family's `Skill(edify:recall)` (`corrector.md:184`, `runbook-corrector.md:59`) against the by-path recall rule now stated once in `dispatch-composition.md` and `delegation.md`; `review-requirement.md`'s routing table still routing "plans" to `edify:corrector` with no outline/runbook rows (defers to D-26).
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Report-only reviewers (`plugin-dev:skill-reviewer`, no Write) get truncated at ~4,000 chars in the reply; give `plugin/skills/inline/references/review-dispatch-template.md` a chunked-return instruction, or route skill definitions to a Write-capable reviewer.
