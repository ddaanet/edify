# Recall Artifact: recall-tool-anchoring

## How to Prevent Skill Steps From Being Skipped

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** Core pattern being applied — D+B Hybrid fix for prose-only gates. Every skill step must open with concrete tool call.

- Execution-mode cognition optimizes for "next tool call." Steps without tool calls register as contextual commentary.
- Fix: merge each gate into adjacent action step, anchor with tool call (Read/Bash), explicit if/then control flow.
- Convention: Every skill step must open with a concrete tool call. Prose-only judgment steps are a structural anti-pattern.

## When Designing Quality Gates

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** Layered enforcement model. Recall gates need multiple independent defense layers, not single mechanism.

- Layer 1 (Outer): D+B hybrid ensures gate runs via tool call, not prose
- Layer 2 (Middle): Automated checks at commit/publish time
- Layer 3 (Inner): Semantic review for quality alignment
- Ambient rules without enforcement are aspirational. Gate at chokepoint mechanically.
- Different layers have different failure modes (not redundant)

## When Placing Quality Gates

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** Anti-pattern of ambient rules in fragments. Directly describes why prose recall gates fail.

- Anti-pattern: Ambient rules telling agents to review artifacts. Unenforceable — agents rationalize skipping under momentum. Sub-agents don't see fragments at all.
- Correct: Gate at chokepoint. Scripted check blocks mechanically. No judgment needed at gate.

## When Splitting Validation Into Mechanical And Semantic

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** `_recall check` is mechanical (file exists?), `_recall generate` is deterministic (keyword match + resolve). Neither needs agent judgment.

- Script handles deterministic checks (blocking, zero false positives)
- Agent enriches for semantic checks (advisory)
- Different enforcement layers for different failure modes

## When Sub-Agent Rules Not Injected

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** Corrector agents don't receive CLAUDE.md recall gate instructions. Must carry recall explicitly — tool call or prompt injection.

- Rules files fire in main session only; sub-agents don't receive injection
- Domain context must be carried explicitly — planner writes into runbook, orchestrator passes through task prompt

## How to Recall Sub-Agent Memory

**Source:** `agents/decisions/project-config.md`
**Relevance:** Established pattern for sub-agent recall via bash transport. `_recall check/generate` uses same mechanism.

- Inject memory index via skills (discovery), recall via Bash transport (`when-resolve.py`)
- Sub-agents lack Skill tool. Bash transport provides same recall capability.

## When Choosing Script Vs Agent Judgment

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** Recall generation is non-cognitive (keyword matching + resolution). Script it.

- If solution is non-cognitive (deterministic, pattern-based), script it. Always auto-fix when possible.
- Reserve agent invocations for cognitive work (design, review, ambiguous decisions).

## When Agent Ignores Injected Directive

**Source:** `agents/decisions/workflow-optimization.md`
**Relevance:** Positional authority matters. Bold NEVER in agent core constraints beats appended context. Recall gates at bottom of skill/agent files have weak positional authority.

- Appended context at bottom has weak positional authority vs bolded directives in core constraints section
- Contradictions resolve in favor of structurally prominent directive

## When Hook Fragment Alignment Needed

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** Hook (Layer 3) must reinforce, not contradict, the D+B restructured gates in skills.

- Hook output must reinforce fragment instructions, never contradict
- Hook content sits in recency zone, fragment in primacy zone

## When Using Hooks In Subagents

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** PreToolUse hook on Task fires in main session only — correct placement for Layer 3 (the delegator is in main session).

- Hooks don't fire in sub-agents spawned via Task tool
- Task matcher fires on ALL Tasks (noisy)

## When Embedding Knowledge In Context

**Source:** `agents/decisions/workflow-advanced.md`
**Relevance:** Ambient context outperforms invocation (100% vs 79%). But recall gates aren't ambient knowledge — they're action instructions. Tool anchoring converts them from "knowledge to remember" to "action to execute."

- Ambient context (100%) outperformed skill invocation (79%)
- Skills not triggered 56% of cases — decision about "when to invoke" is failure point

## When Declaring Phase Type

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** Phase typing for this runbook — inline for prose edits (D+B restructure), general for scripts/hook.

- Inline eligibility: no runtime feedback loop, prose edits, all decisions pre-resolved
- Inline phases → orchestrator-direct execution (no Task dispatch)
- TDD/general → per-step agent delegation

## When Selecting Model For Prose Artifact Edits

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** D+B restructure edits skills/agents — architectural artifacts requiring opus regardless of edit simplicity.

- Skills, fragments, agent definitions, design documents → opus
- Anti-pattern: assigning sonnet/haiku based on "edit complexity" rather than artifact type

## When Bootstrapping Self-Referential Improvements

**Source:** `agents/decisions/workflow-planning.md`
**Relevance:** Scripts must exist before D+B references them. Bootstrap one D+B edit before rollout.

- Apply each improvement before using that tool in subsequent steps
- Phase ordering follows tool-usage dependency graph, not logical grouping

## When Agent Context Has Conflicting Signals

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** Common Context recall must be phase-neutral. D+B edit specifics belong in step/phase instructions only.

- Common context is persistent ambient signal stronger than one-time step input
- At haiku capability, persistent signal wins over per-step instructions

## When Writing Rules For Different Models

**Source:** `agents/decisions/prompt-structure-research.md`
**Relevance:** D+B edits are consumed by haiku/sonnet/opus agents. Format instructions per consumer tier.

- Haiku: explicit steps, DO NOT examples, ⚠️ markers
- Sonnet: clear bullets with context
- Opus: concise prose, trust inference
