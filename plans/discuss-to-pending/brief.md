# Brief: discuss-to-pending

## Origin

Pattern observed 3 times in wt-rm-dirty deliverable review session (2026-03-01). Each time: `d:` mode evaluation concluded with agreement that a change should be made, but no pending task was created until the user pointed out the gap.

## Problem

When `d:` mode discussion validates a proposed change ("I agree, this should be done"), the agent should chain to `p:` evaluation — assess model tier, create pending task, optionally create brief. Currently, agreement in `d:` mode is terminal: the agent states its verdict and stops. The validated change exists only in conversation context, which rotates out.

## Evidence (3 occurrences, same session)

1. **`k` clipboard shortcut** — agreed it was apt, no pending task created. User nudged.
2. **Worktree lifecycle final-step behavior** — agreed the workflow change was needed, no pending task. User nudged.
3. **UPS injection for g/go and k/ok** — validated as Tier 1 commands, no pending task. User nudged.

## Proposed Solution

When `d:` mode conclusion is "agree, this change should be made" (or equivalent affirmative verdict on a proposed change), chain to:
1. `p:` evaluation — task name, model tier, restart flag
2. Brief creation if discussion produced design context worth preserving
3. Pending task in session.md (deferred to next handoff per existing rules)

## Implementation Options (not yet evaluated)

- **Fragment rule** in `execute-rule.md` or `pushback.md` — prose instruction for d: mode exit behavior
- **UPS hook augmentation** — detect affirmative verdict pattern in d: output, inject p: reminder
- **Learnings entry** — lightweight, relies on agent recall
- **d: directive expansion** — add "If your verdict validates a change, chain to p: evaluation" to `_DISCUSS_EXPANSION`

## Next Step

`/requirements` — determine which implementation approach, capture FRs.
