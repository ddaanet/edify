## Remaining

- `/design plans/pipeline-simplification/` — requirements /proof-validated 2026-08-29; execute as an inline task sequence (C-5), on a branch
- Dogfood the pipeline end-to-end on a branch, after pipeline-simplification lands (the deliverable-review diff range comes from context, so work committed on `main` first would leave nothing to review)
- Consolidate `memory/MEMORY.md`: 31.3KB (126% of the 25600-byte budget); Claude Code's loader truncates past 24.4KB so tail entries never load, and the compose hook asks for under 17.1KB — retire per `index-compaction-triggers`, don't shorten lines to hit the number
- FR-12 remainder: defect 21 (corrector skeleton — measured 2026-08-28: the four sections it points at are per-agent text, not shared; extraction cannot reduce tokens, only deletion can; `corrector.md` 21.7KB and `runbook-outline-corrector.md` 20.4KB are 2× the plugin-dev 10,000-char cap) and per-class skill-body length targets (no calibration data; do not set by reasoning)
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle (requirements.md is /proof-validated)
