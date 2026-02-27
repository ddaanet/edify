# Recall Artifact: Inline Execute

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Design-Related

Entries for skill creation, /design integration, architectural decisions.

### Skill structure and conventions
how chain multiple skills together — continuation passing protocol, peel-first-pass-remainder
when placing DO NOT rules in skills — negative constraints alongside positive guidance
how compose agents via skills — skills: frontmatter injection
when choosing name — discoverability and recall over cleverness
when avoiding CLI skill name collision — check built-ins before naming
when parsing cli flags as tokens — flags are exact tokens, not prose substrings
when skill sections cross-reference context — inline criteria at each usage site
when embedding knowledge in context — ambient context outperforms skill invocation
how prevent skill steps from being skipped — D+B hybrid, tool call anchor per step
when loading context before skill edits — load plugin-dev:skill-development first
when reviewing skill deliverable — cross-project context, skill-reviewer not Task agent

### Design gates and classification
when reading design classification tables — read literally, no invented heuristics
when design ceremony continues after uncertainty resolves — two gates, mid-stream re-check
when complexity assessed twice — single assessment, no redundant triage
when design resolves to simple execution — execution readiness gate, coordination complexity discriminator
when relating execution tiers to complexity routing — three independent decisions at different stages
when tier boundary is capacity vs orchestration complexity — capacity for 1→2, orchestration for 2→3

### Corrector and review routing
when corrector rejects planning artifacts — corrector for implementation, runbook-corrector for planning
when corrector agents lack recall mechanism — every corrector needs recall loading
when recall-artifact is absent during review — lightweight recall fallback, not skip
when batch changes span multiple artifact types — per-file routing, not single reviewer
when routing implementation findings — unconditional /design, no size-based routing
when concluding reviews — severity counts, pending task, no merge-readiness language

### Execution routing
when choosing execution tier — inline/delegate/orchestrate, context window capacity
when context already loaded for delegation — don't delegate when context is loaded
when delegating well-specified prose edits — opus rule targets design decisions during editing
when fixing behavioral deviations identified by RCA — structural fix, not prose strengthening
when bootstrapping self-referential improvements — apply each improvement before using that tool next

## Runbook-Related

Entries for /runbook tier assessment, TDD planning, orchestration, pipeline integration.

### Phase and tier planning
when declaring phase type — tdd/general/inline, determines expansion and review
when phase qualifies as inline — outcome determined by instruction + file state, no feedback loop
how expand outlines into phases — outline first, phase-by-phase with review
when checking complexity before expansion — check before, callback if too large
when merging trivial cycles with adjacent work — consolidation gates at Phase 1.6 and 4.5
when assessing orchestration tier — three-tier routing: direct, lightweight delegation, full runbook
when tier thresholds are ungrounded — file/cycle counts need empirical calibration
how format runbook outlines — structured format with requirements mapping

### TDD cycle planning
when writing test descriptions in prose — behavioral specifics, not full test code
how write green phase descriptions — behavioral requirements + hints, not prescriptive code
when ordering tdd test cases — happy path first, not empty/degenerate
when triaging behavioral code changes as simple — behavioral code routes to Moderate + TDD
when tdd cycles grow shared test file — conditional split instructions in later cycles
when cycle numbering has gaps — warnings not errors, document order defines sequence

### Model selection and execution
when selecting model for prose artifact edits — opus for skills/fragments/agents/design
when selecting model for TDD execution — pattern→haiku, state-machine→sonnet, synthesis→opus
when haiku rationalizes test failures — regression failures are bugs, not expected changes
when haiku GREEN phase skips lint — GREEN verification must include lint gate

### Orchestration patterns
when delegation requires commit instruction — explicit commit in every delegation prompt
when limiting agent scope — context absence enforces scope, not prose rules
when step agents leave uncommitted files — commit ALL generated artifacts including reports
when agent context has conflicting signals — common context phase-neutral, specifics in step files
when crossing phase boundaries — hard stop, explicit checkpoint delegation
how checkpoint runbook execution — two-step: fix (just dev) then vet (quality review)
how structure phase grouped runbooks — flat H2 or phase-grouped H2+H3
how format runbook phase headers — H3 for phase grouping, H2 for steps
when editing runbook step or agent files — edit source phase files, not generated output

### Quality gates
when choosing script vs agent judgment — non-cognitive deterministic → script, cognitive → agent
when splitting validation into mechanical and semantic — script deterministic, agent judgment advisory
when designing quality gates — layered defense, multiple independent checks
when placing quality gates — gate at chokepoint, scripted mechanical enforcement
when reviewing expanded phases — LLM failure modes at both outline AND expanded levels

### Pipeline integration
when adding a new variant to an enumerated system — grep all enumeration sites downstream
when writing memory-index trigger phrases — keep articles aligned with heading text
when naming memory index triggers — activity at decision point, not outcome or anti-pattern
how end workflow with handoff and commit — all tiers end with /handoff --commit

### Evidence collection
how detect noise in command output — multi-marker detection with length threshold
how architect feedback pipeline — three-stage collect→analyze→rules
when choosing feedback output format — text vs json format for piping
