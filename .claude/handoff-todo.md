## Open decisions

- Outline D1: after `/runbook`, execution routes always to `/orchestrate` and `/inline` never consumes a runbook — its "Delegated Execution (Tier 2)" section is deleted and prompt composition single-sources to `plugin/skills/orchestrate/references/dispatch-composition.md`. This goes beyond the requirements, whose Out of Scope presumes `/inline` keeps consuming the runbook artifact. Accept or restore the `/inline` delegated path.
- Outline D12: add a branch gate to `/orchestrate` preflight (`git branch --show-current` on `main` → STOP, name `superpowers:using-git-worktrees`). Derived from no FR; motivated by the deliverable-review diff range coming from context. Keep or strike.

## Remaining

- Finish `/proof plans/pipeline-simplification/outline.md` (19 items), then the outline sufficiency gate, then `/inline plans/pipeline-simplification execute` on a branch
- Dogfood the pipeline end-to-end on a branch, after pipeline-simplification lands (the deliverable-review diff range comes from context, so work committed on `main` first would leave nothing to review)
- Consolidate `memory/MEMORY.md`: 31.1KB against Claude Code's 24.4KB loader cutoff, so tail entries never load — retire per `index-compaction-triggers`, don't shorten lines to hit the number
- FR-12 remainder: defect 21 (corrector skeleton — measured 2026-08-28: the four sections it points at are per-agent text, not shared; extraction cannot reduce tokens, only deletion can; `corrector.md` 21.7KB and `runbook-outline-corrector.md` 20.4KB are 2x the plugin-dev 10,000-char cap) and per-class skill-body length targets (no calibration data; do not set by reasoning)
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle (requirements.md is /proof-validated); update its FR-9/FR-12/NFR cross-references when pipeline-simplification lands
