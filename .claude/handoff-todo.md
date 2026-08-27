## Open decisions

- Whether to delete the retired task-list fossil layer that still models `.claude/handoff-task.md` as a pending-task file with In-tree/Worktree sections and `x`/`h`/`p:`/`r` shortcuts: `plugin/fragments/execute-rule.md`, `plugin/fragments/task-failure-lifecycle.md` (referenced by `.claude/rules/planning-work.md`), `plugin/docs/shortcuts.md`, `plugin/docs/migration-guide.md`, `plugin/docs/@file-pattern.md`, `plugin/.claude/CLAUDE.local.md.example` (`#load`/`#execute`), `plugin/bin/task-context.sh` and the `/inline` pre-work step that calls it. The 2026-08 fold's cut-not-tag rule points at deletion.

## Remaining

- Dogfood the pipeline end-to-end on a branch (the deliverable-review diff range now comes from context, so work committed on `main` first would leave nothing to review)
- FR-12 remainder: defect 21 (corrector skeleton, ~10,100 words across four agents — only pays if the shared fragment's Read is folded into the dispatch batch) and per-class skill-body length targets (no calibration data; do not set by reasoning)
- Consolidate `memory/MEMORY.md`: the index is at 117% of the 25600-byte budget and Claude Code's loader truncates past 24.4KB, so tail entries never load
- Add test coverage for `plugin/bin/prepare-runbook.py` — the suite reaches it only indirectly through `validate-runbook.py`'s imports
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle (requirements.md is /proof-validated)
