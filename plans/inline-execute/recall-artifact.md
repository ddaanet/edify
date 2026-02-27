# Recall Artifact: Inline Execute

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

### Skill structure and conventions
how chain multiple skills together — continuation passing protocol, peel-first-pass-remainder
when placing DO NOT rules in skills — negative constraints alongside positive guidance
how compose agents via skills — skills: frontmatter injection
when choosing name — discoverability and recall over cleverness
when avoiding CLI skill name collision — check built-ins before naming
when parsing cli flags as tokens — flags are exact tokens, not prose substrings
when skill sections cross-reference context — inline criteria at each usage site
when embedding knowledge in context — ambient context outperforms skill invocation

### Corrector and review patterns
when corrector rejects planning artifacts — corrector for implementation, runbook-corrector for planning
when corrector agents lack recall mechanism — every corrector needs recall loading
when recall-artifact is absent during review — lightweight recall fallback, not skip
when choosing script vs agent judgment — non-cognitive deterministic → script, cognitive → agent
when splitting validation into mechanical and semantic — script deterministic, agent judgment advisory
when designing quality gates — layered defense, multiple independent checks
when placing quality gates — gate at chokepoint, scripted mechanical enforcement

### Execution and workflow
when choosing execution tier — inline/delegate/orchestrate, context window capacity
when design resolves to simple execution — execution readiness gate, coordination complexity discriminator
when context already loaded for delegation — don't delegate when context is loaded
when delegating well-specified prose edits — opus rule targets design decisions during editing
how end workflow with handoff and commit — all tiers end with /handoff --commit
when fixing behavioral deviations identified by RCA — structural fix, not prose strengthening

### Triage and classification
when reading design classification tables — read literally, no invented heuristics
when design ceremony continues after uncertainty resolves — two gates, mid-stream re-check
when complexity assessed twice — single assessment, no redundant triage
when tier thresholds are ungrounded — empirical calibration needed

### Evidence collection
how detect noise in command output — multi-marker detection with length threshold
how architect feedback pipeline — three-stage collect→analyze→rules
when choosing feedback output format — text vs json format for piping
