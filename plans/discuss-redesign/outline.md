# Outline: Discuss Protocol Redesign

## Problem

Current `d:` protocol (pushback.md §Design Discussion Evaluation) has four structural problems:
- **Stress-test is dead weight:** 0 perspective changes across ~80+ sessions. Agent controls both sides — defense always wins. Originally fixed AGAINST-first contrarianism; became entrenchment mechanism.
- **Grounding is reactive:** Checks user's referenced artifacts. Agent's own ungrounded claims pass unchallenged.
- **Brainstorm is mandatory overhead:** "3+ alternative framings" slows response, not always needed. Most useful for straightforward-seeming tasks where it's least likely to trigger.
- **Verbosity:** Five output sections, verdict buried in middle position (weakest per primacy/recency bias).

Evidence: `plans/reports/discuss-protocol-mining.md` (commit `1857b689`) — 9 perspective-change sessions mined. Actual triggers: new facts (4/9), reframing (3/9), research gaps (2/9). Zero from internal stress-test.

## Approach

Replace the current 5-step protocol (ground → diverge → assess → research → verdict) with a 3-step core:

1. **Ground** — Load context before forming position
2. **State position** — Commit to verdict with evidence
3. **Validate claims** — Enumerate claims, trace each to source, flag ungrounded

Optional user-triggered prefix: `bd:` for divergence before discussion.

### Why This Works

Claim validation is a text operation (claim → source lookup), not metacognitive introspection (monitor confidence). Same structural class as:
- 0% spontaneous recall → agents execute constrained lookups, don't self-initiate
- "MUST"/"no exceptions" language failing → structural enforcement succeeds (RCA decision)

## Decisions

### D1. Grounding mechanism

**Chosen:** Recall-explore sequence before position formation.

- Resolve recall entries relevant to the topic (using memory-index, not speculative triggers)
- Read artifacts referenced in the proposal
- If agent makes factual claims about project state: verify via Glob/Grep/Read before asserting

Lighter than `/ground` skill (no web search mandatory). Heavier than current "Read referenced artifacts." The addition: agent must also ground its own claims, not just verify user's.

### D2. Claim validation mechanics

**Chosen:** After position statement. Mechanical text operation.

Process:
- Enumerate each claim in the position
- For each: cite source (file path, recall entry, search result) or mark `[ungrounded]`
- `[ungrounded]` claims: research to find source (search, Read, web if needed)
- Surviving `[ungrounded]` claims remain visibly marked — user decides whether to request further research
- After research: restate position if any claims changed, otherwise confirm

Not a confidence self-assessment. Not "flag uncertainty." A lookup operation: "where did this come from?"

### D3. Stress-test disposition

**Chosen:** Remove entirely.

Rationale: Zero observed utility. Self-rebuttal structure means defense always wins. The mining data is unambiguous — 0/80+ sessions produced a perspective change from stress-testing. The three actual change mechanisms (new facts, reframing, research gaps) are covered by grounding (D1) and claim validation (D2). Aligns with RCA recall: structural fixes (claim validation as text operation) over prose strengthening ("be more critical").

### D4. Brainstorm / divergence disposition

**Chosen:** Remove from `d:` mandatory path. Available as `bd:` user-triggered prefix.

`bd:` behavior: Generate 3+ alternative framings (at least one must reframe the problem, not vary the solution). Present framings, then proceed with `d:` core protocol. The divergence step has value — reframing produced 3/9 perspective changes — but as a user-selected tool, not mandatory ceremony.

### D5. Agreement momentum

**Chosen:** Keep with adjustment.

Current rule (3+ consecutive conclusion-level agreements → re-examine) is sound. Adjustment: the re-examination uses claim validation (D2), not stress-test. "Re-examine" = enumerate claims in your agreement, trace to sources, flag ungrounded. If all grounded, agreement stands.

### D6. Output format

**Chosen:** Position-first, compact.

```
**Position:** [verdict in one sentence]
**Grounding:** [2-3 key sources that informed position]
**Claims:** [enumerated, each with source or [ungrounded]]
**[If ungrounded claims exist]:** [research result → revised or confirmed]
```

Verdict in primacy position — LLMs exhibit strong primacy bias (see `agents/decisions/prompt-structure-research.md`). Claims enumeration doubles as evidence trail. No separate "assessment" and "verdict" sections.

### D7. Existing artifact disposition

**Modified files:**
- `agent-core/fragments/pushback.md` — Rewrite §Design Discussion Evaluation. Keep §Pushback preamble, §Agreement Momentum (adjusted per D5), §Evaluation Biases, §Model Selection for Pending Tasks.
- `agent-core/fragments/execute-rule.md` — Add `bd:` to Tier 2 directives table.

**No new skill created.** The protocol lives in pushback.md (fragment loaded every session), not a skill. `d:` remains a directive, not a skill invocation. This matches current architecture — discussion is a behavioral mode, not a workflow.

**Removed:** §Design Discussion Evaluation subsections: "Diverge before assessing", "Research your own claims" (replaced by claim validation), "State your verdict explicitly" (replaced by position-first format).

### D8. Adversarial framing preservation

**Chosen:** Not included in core protocol.

"Poke holes in logic, explain why status quo is better" — single data point from brief. Interesting but insufficient evidence for protocol inclusion. Can be user-triggered via natural language ("argue against this") without protocol support.

## Components

**C1: pushback.md rewrite** — Rewrite §Design Discussion Evaluation with 3-step core protocol (D1-D3, D6). Adjust §Agreement Momentum (D5). Keep §Pushback preamble, §Evaluation Biases, §Model Selection. Remove obsolete subsections (D7).

**C2: execute-rule.md update** — Add `bd:` to Tier 2 directives table (D4).

## Scope

**IN:**
- (C1) Rewrite pushback.md §Design Discussion Evaluation
- (C2) Add `bd:` directive to execute-rule.md
- (C1) Adjust §Agreement Momentum in pushback.md

**OUT:**
- Testing methodology (A/B testing, longitudinal observation) — separate task; ground truth annotation is the blocking human step (brief §2026-03-13)
- `/ground` skill changes — independent
- `w` (wrap) command — already works, orthogonal
- Brainstorm skill changes — `bd:` is a directive, not a brainstorm skill modification

## Affected Files

- `agent-core/fragments/pushback.md` — primary change
- `agent-core/fragments/execute-rule.md` — `bd:` addition to Tier 2 table

## Open Questions

None — all design questions resolved by brief discussion conclusions and mining evidence. Testing methodology deferred to OUT scope (ground truth annotation is the blocking human step).

## Risks

- **Claim validation could become perfunctory:** Agent lists claims, marks all "grounded" by citing itself. Mitigation: "cite source" must be a file path, recall entry key, or search result — not "based on my understanding."
- **Removing stress-test could lose undiscovered value:** 0/80+ is strong evidence, but absence of evidence caveat applies. Mitigation: longitudinal observation after deployment can detect regression.
