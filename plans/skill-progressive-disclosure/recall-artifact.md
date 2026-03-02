# Recall Artifact: Skill Progressive Disclosure

Resolve entries via `claudeutils _recall resolve` — do not use inline summaries.

## Entry Keys

how prevent skill steps from being skipped — D+B hybrid: every step opens with tool call, no prose-only gates
when loading context before skill edits — load plugin-dev:skill-development before editing skill files
when skill sections cross-reference context — inline shared criteria at each usage site, don't back-reference
when inlining reference file subsets for optimization — partial inlining creates knowledge ceiling, use full Read
when designing context preloading mechanisms — explicit skill invocation over @ref duplication
when too many rules in context — adherence degrades >200 rules, marker-based counting
when ordering fragments in CLAUDE.md — primacy/recency bias, middle content weakest
when assessing fragment demotion — behavioral vs procedural/reference, passive fragments are dead weight
when execution routing preempts skill scanning — skill matching must precede execution routing
how make skills discoverable — 4 discovery layers: CLAUDE.md, rules, in-workflow reminders, description
when placing DO NOT rules in skills — co-locate negative constraints with positive content guidance
when skill is already loaded — execute immediately, don't pause
when using at-sign references — only work in CLAUDE.md, not in SKILL.md or agent prompts
how compose agents via skills — skills: YAML frontmatter injects skill content as prompt
how augment agent context — two-tier: always-inject + index-and-recall
when embedding knowledge in context — ambient context (100%) outperforms skill invocation (79%)
when design ceremony continues after uncertainty resolves — two gates: entry + mid-stream re-check
when design resolves to simple execution — execution readiness gate, coordination complexity discriminator
