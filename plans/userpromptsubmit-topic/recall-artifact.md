# Recall Artifact: UserPromptSubmit Topic

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

evaluating recall system effectiveness — 4.1% voluntary activation, forced injection bypasses recognition
memory-index amplifies thin user input — keyword matching from sparse queries, amplification effect
embedding knowledge in context — ambient context (100%) vs skill invocation (79%)
execution routing preempts skill scanning — UserPromptSubmit hook injection reaches 84% activation
designing context preloading mechanisms — avoid @ref duplication, skill invocation pattern
filter user prompt submit hooks — no matcher support, script-internal filtering
mapping hook output channel audiences — additionalContext agent-only, systemMessage user-only
writing hook user-visible messages — terminal constraint 60 chars, tier injection
hook fragment alignment needed — recency vs primacy, contradictions resolve to recency
hook commands use relative paths — CLAUDE_PROJECT_DIR absolute resolution
ordering fragments in CLAUDE.md — primacy bias, recency secondary, middle weakest
too many rules in context — adherence degrades >200 rules, ~150 budget
loading context for llm processing — explicit reading required, no inherent file loading
writing memory-index trigger phrases — article alignment, heading match
naming memory index triggers — activity at decision point, not outcome
