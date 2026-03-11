# Discuss Protocol Mining: Session Analysis

## Dataset

- **9 sessions** with "I was wrong" (perspective change)
- **8 sessions** with "revised position" (position adjustment)
- **~80+ sessions** with stress-test/verdict (protocol active)
- **1 session** directly about the protocol (discuss-divergent-step)
- **29 sessions** in pushback worktree (protocol design + validation)

## Stress-Test Origin Story

**Session:** `5952058f` (2026-02-15, pushback worktree)

**Problem being solved:** The original pushback protocol used AGAINST-first framing ("Articulate the strongest case AGAINST the proposed conclusion"). This caused contrarianism — agent built adversarial argument first, then concluded from it. Three conditions tested:

| Condition | Result |
|-----------|--------|
| No discuss signal | No evaluation — agent accepted silently |
| "discuss" (no hook) | Evaluation triggered, too negative |
| `d:` (hook fires) | Evaluation triggered, too negative |

**Root cause identified:** AGAINST-first creates a reasoning trap. Agent builds the case against, reasoning momentum carries the conclusion. Mirror image of sycophancy — same mechanism, opposite direction.

**Fix applied:** Verdict-first protocol — "Form your assessment first, THEN stress-test it." The stress-test was introduced specifically to prevent the agent from building an adversarial case and then concluding from it. The idea: commit to a position, then challenge it.

**Validation results:** S1/S2 (basic eval) passed. S3 (agreement momentum) and S4 (model selection) failed — separate issues fixed in subsequent sessions.

**The irony:** Stress-test was the fix for contrarianism. Now it's the mechanism for entrenchment. Same structure (agent argues against something), different target (argues against its own position instead of the proposal). The self-rebuttal step means the defense always wins.

## What Triggers Actual Perspective Changes

Cataloging the 9 "I was wrong" instances by trigger:

| Session | Topic | Trigger for change | Mechanism |
|---------|-------|--------------------|-----------|
| 029221b8 | @context cumulative | User stated a fact ("@context and Read are cumulative") | **New fact** |
| 3883e316 | Learning append | User pointed out semantic anchoring benefit | **Reframing** |
| 6a627e21 | Token savings | User challenge ("20k incompressible?") | **Challenge forced re-examination** |
| 6a627e21 | /remember priority | Same session, cascade from token recount | **Cascade** |
| 7235aede | Tasks validator | User correction of constraint purpose | **New fact** |
| b4329975 | Vet proportionality | User stated "fragments need opus authoring" | **Reframing** |
| e464ed44 | git -D safety | User stated "losing merge parent is critical failure" | **New fact** |
| f7df8d1a | "ready" vs "delivered" | User stated "'ready' conveys execution pending" | **Semantic correction** |
| current | A/B testing feasibility | User said "have you researched it?" | **Research gap exposed** |

### Three categories, ordered by frequency

1. **New facts the agent didn't have** (4/9): User provides information the agent couldn't derive from context. No amount of internal argumentation surfaces these.
2. **Reframing the conceptual model** (3/9): User names a frame the agent didn't generate. The divergent step (added in discuss-divergent-step) addresses this.
3. **Exposing a research gap** (2/9): User points out the agent reasoned without evidence. This is the gap the current session exposed.

### What DOESN'T change the agent's mind

The stress-test step: zero observed perspective changes across the dataset. Every instance follows the same pattern: form assessment → generate counterargument → rebut counterargument → hold position.

### Current session resistance sequence

1. **Round 1**: "Disagree with A/B — three reasons." Stress-tested, survived, held.
2. **Round 2**: "Agree with observability constraint. Pick safer default." Still no research.
3. **Round 3**: User said "have you researched it?" — one search disproved every objection.

## Structural Problems

1. **Stress-test is self-rebutting:** Agent controls both sides. Defense always wins. Was introduced to fix contrarianism — became the mechanism for entrenchment.
2. **Grounding is reactive only:** "Read artifacts referenced in claims" — only checks user's references. Agent's own ungrounded claims pass unchallenged.
3. **No research trigger for own claims:** Three rounds of "infeasible" without one search. The protocol never prompts: "what evidence supports your position?"
4. **Verbosity:** Five output sections, verdict buried. Framings useful as internal reasoning (think block) but noisy as output.

## User Decisions (from discussion)

- **Framings:** Keep as think block (internal reasoning), not output
- **Ground your own claims = research trigger:** Merge into single step
- **Stress-test removal:** Needs origin context before deciding (this report provides it)
- **Research weight:** Full `/ground` too heavy for inline discuss. Lighter option: fast exploration + web search
- **Agreement momentum (3+):** Not yet decided
