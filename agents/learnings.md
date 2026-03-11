# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When codify drops incident-specific learnings
- Anti-pattern: Codify skill quality criteria unconditionally reject incident-specific entries ("describes what happened, not what to do"). Loses recurrence signal — "this happened twice" changes fix priority.
- Correct pattern: Incident-specific entries have value as occurrence counters even without a generalized principle. Recurrence tracking is a valid consolidation reason. Methodology TBD (plan: incident-counting).
- When user says "force" (flush all), skill-internal quality filters should not override user intent.

## When detecting prior uncommitted handoff
- Anti-pattern: `git diff --name-only HEAD -- agents/session.md` non-empty → assume prior handoff → merge incrementally. Conflates current-session task edits (slug markers, task additions) with prior-session uncommitted handoffs.
- Correct pattern: Inspect diff content. Only treat as prior handoff if `## Completed This Session` was modified. Task-only changes (current session edits) → fresh write.
- Agent had conversation context proving it made the edits itself but followed the heuristic mechanically.

## When delegating external repo git operations
- Anti-pattern: Dispatch artisan agents to run `git -C ~/code/<repo>` on repos outside the project tree. Sandbox write-allow restrictions block the agent even though the operations are read-only.
- Correct pattern: Execute git read operations (`git -C`, `git log`, `git show`) directly from the parent session. Sub-agents only work reliably within the project's sandbox-allowed paths.
- scratch/* repos under claudeutils worked because `~/code/claudeutils` is in the write-allow list. External repos (~/code/rules, ~/code/tuick, etc.) failed.
