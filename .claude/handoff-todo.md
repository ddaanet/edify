## Remaining

- `/deliverable-review plans/pipeline-simplification` in a fresh opus session.
- Dogfood the simplified pipeline end to end (`/design` → `/runbook` → `/orchestrate`) on a real plan; L-6 in `docs/design.md` records it as unexercised, and FR-5's slice-batching claims stay unvalidated until it supplies counts.
- Consolidate `memory/MEMORY.md` (32,346 bytes vs the 24.4KB loader cutoff) via `/gitlore:index-audit` — retire, don't shorten; update `docs/design.md` L-5's stale "~28.9 KB" figure in the same pass.
- Pilfer defect 21 (corrector-skeleton dedup) now also carries two observations from `reports/review-agents.md`: `corrector.md` lines ~293–304 hold "when reviewing runbooks/plans" criteria its Step 0 runbook-rejection makes unreachable, and the corrector family resolves recall via `Skill(edify:recall)` while `delegation.md` and `dispatch-composition.md` hand dispatched agents a flat-list Read.
- FR-12 remainder beyond defect 21: per-class skill-body length targets (no calibration data).
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Report-only reviewers (`plugin-dev:skill-reviewer`, no Write) return their report in the reply, which the harness truncates at roughly 4,000 characters; the skills review took five SendMessage round-trips to recover. Either give `plugin/skills/inline/references/review-dispatch-template.md` a chunked-return instruction for report-only reviewers or route skill definitions to a Write-capable reviewer.
