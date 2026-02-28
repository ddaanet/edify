# Recall Artifact: Flatten Hook Tiers

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

how filter user prompt submit hooks — UPS has no matcher field, all filtering script-internal
when hook fragment alignment needed — recency/primacy interaction with injected content
when mapping hook output channel audiences — additionalContext vs systemMessage vs permissionDecisionReason
when writing hook user-visible messages — terminal constraint 60 chars, tier injection patterns
when writing hook redirect messages — rationale in every hook message
when hook commands use relative paths — CLAUDE_PROJECT_DIR absolute resolution
when choosing hook enforcement over permission deny — PreToolUse hooks vs sandbox denylist
when implementing pre-delegation gates — permissionDecision deny, subagent_type discriminator
when execution routing preempts skill scanning — UPS hook injects skill-trigger reminders
when using hook based parsing — deterministic hook parsing vs fragment-based, sub-agent isolation
