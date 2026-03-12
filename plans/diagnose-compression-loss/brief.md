# Brief: Diagnose Compression Loss

## Problem

After commit `0418cedb` ("Compress session: top 10 tasks, archive plans, create backlog"), session handoff output quality degraded. Handoffs became more verbose and less information-dense. The commit itself was a large-scale session compression:

- Deleted 6 completed/superseded plan directories (when-recall, worktree-update, worktree-merge-resilience, workwoods, error-handling, claude) — 401 files, ~42,700 lines removed
- Moved 30+ deferred tasks to `agents/backlog.md` (since removed)
- Reduced `agents/session.md` to top-10 tasks
- Batched 3 worktree rm fixes, absorbed 5 tasks, dropped 2 stale tasks

The question is whether the compression commit caused the quality degradation directly (changed handoff-relevant content) or merely correlates temporally with a separate cause (model behavior shift, fragment edit, skill change).

## Symptoms

- Handoff prose is verbose — filler, hedging, unnecessary framing
- Information density dropped — same content takes more lines
- Observed in sessions after `0418cedb`; not observed before

## Investigation Scope

- Diff `0418cedb` against parent: identify changes to handoff skill, session format rules, prose quality fragments, or communication rules
- Check surrounding commits for changes to `/handoff` skill content, `communication.md`, or `token-economy.md`
- Determine whether `agents/session.md` structural changes (task reduction, backlog split) altered handoff behavior
- Assess model-behavior vs content-change as competing hypotheses
- Check if the compression removed context that guided handoff prose quality (e.g., exemplar sessions, inline style notes)

## Success Criteria

- Root cause identified with specific evidence (file change, removed content, or model behavior delta)
- If content regression: fix applied restoring information density
- If model behavior: documented as external cause with mitigation strategy
- If intentional trade-off: rationale documented in `agents/decisions/`

## References

- Commit: `0418cedb` — the compression commit
- Current handoff skill: `agent-core/skills/handoff/`
- Prose quality rules: `agent-core/fragments/communication.md`, `agent-core/fragments/token-economy.md`
