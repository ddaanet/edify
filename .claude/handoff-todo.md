## Remaining

- Consolidate `memory/MEMORY.md` to under 17.1KB — at 28.9KB it sits past Claude Code's 24.4KB loader cutoff, so tail entries never reach a session; retire and relocate entries rather than reword them
- `/proof plans/pilfer-superpowers/requirements.md`, then `/design` once Q-1/Q-3 settle
- Clear the repair backlog in `plans/pilfer-superpowers/reports/edify-defects.md`
- Fix `plugin/bin/deliverable-inventory.py`: it diffs `merge-base HEAD main`, so reviewing work already committed on `main` returns an empty inventory
- Fold `agents/decisions/*.md` into the living design doc
- Exercise the revived pipeline end-to-end (design → runbook → orchestrate)
- Fix `plugin/skills/inline/SKILL.md` Phase 4c (the handoff-task.md write is checkpoint-only now) and `triage-feedback.sh` false-positives on multi-group review dispatch