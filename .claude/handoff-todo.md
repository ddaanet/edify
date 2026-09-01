## Remaining

- Execute outline.md tasks 0-9 (baseline measurement → deletions →
  corrector rename → `/runbook` + `/orchestrate` rewrites → agents →
  consumers → docs → sweep + after-measurement → review dispatch,
  `/deliverable-review` follow-up)
- Dogfood the pipeline end-to-end after pipeline-simplification lands
  (deliverable-review diff base comes from agent context — one commit or
  several, situation-dependent; no fixed git structure required)
- Consolidate `memory/MEMORY.md`: ~31KB against Claude Code's 24.4KB
  loader cutoff, tail entries never load — retire per
  `index-compaction-triggers` (`/gitlore:index-audit`), don't shorten
  lines to hit the number
- FR-12 remainder: defect 21 (corrector skeleton — measured 2026-08-28:
  the four sections it points at are per-agent text, extraction cannot
  reduce tokens, only deletion can; `corrector.md` 21.7KB and
  `runbook-outline-corrector.md` 20.4KB vs the plugin-dev 10,000-char
  cap) and per-class skill-body length targets (no calibration data; do
  not set by reasoning)
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle
  (requirements.md is /proof-validated); update its FR-9/FR-12/NFR
  cross-references when pipeline-simplification lands
