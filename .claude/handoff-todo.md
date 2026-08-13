## Remaining

- Consolidate `memory/MEMORY.md` to under 17.1KB — at 28.9KB it sits past Claude Code's 24.4KB loader cutoff, so tail entries never reach a session; retire and relocate entries rather than reword them
- `/proof plans/pilfer-superpowers/requirements.md`, then `/design` once Q-1 and Q-3 settle
- Single-source the four duplicated blocks parked as pilfer FR-12 (defects 18-21: recall protocol, continuation block, runbook report template, corrector skeleton), reporting measured rather than estimated token reduction
- Fix `plugin/bin/deliverable-inventory.py`: it diffs `merge-base HEAD main`, so reviewing work already committed on `main` returns an empty inventory
- Route the pending-task writes in `/inline` Phase 4c and `/orchestrate` sections 3.4 and 6.4 through the handoff checkpoint channel — direct `.claude/handoff-task.md` writes are hook-blocked
- Fold `agents/decisions/*.md` into the living design doc
- Exercise the revived pipeline end-to-end (design -> runbook -> orchestrate)