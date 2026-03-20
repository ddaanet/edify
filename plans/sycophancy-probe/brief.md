## Sycophancy probe — mediator pattern with reversed claims

### Origin

During /proof of outline-proofing design (session 83b685c4 + continuation c8972892), the agent agreed with "prose is simple" through 4+ rounds despite holding contradictory recall evidence. User used reversed framing (appearing to agree while escalating scope) to expose the sycophancy — effective but ad-hoc.

### Concept

User types `r: prose edits can be complex`. A mediator reverses the claim and presents it to a discussion agent that has full technical context but has never seen the user's actual position. If the discussion agent agrees with the reversed claim → sycophancy signal. If it pushes back → genuine reasoning.

### Architecture options

**Option A: Out-of-platform tool (prototype-weight)**
Script in plans/prototypes/. Uses session-scraper to extract conversation context, filters out user position signals, reverses the claim, calls the Anthropic API directly with curated context + reversed claim. Reports agreement/disagreement. Simple, no Claude Code integration needed.

**Option B: Mediator pattern (in-platform)**
Start a persistent discussion agent at session start, loaded with full project context. Main agent acts as thin mediator — routes user prompts, curates what the discussion agent sees. For `r:` probes: mediator reverses claim, passes to discussion agent, reports result. For normal work: mediator passes through (or curates — strip emotional signals, add adversarial framing). Sycophancy resistance becomes architectural, not model-dependent. Current constraint: Task agents are single-round-trip, need resume mechanism for persistence.

**Option C: Session fork API (when available)**
Anthropic has session forking as restricted API feature. Fork current session into sub-agent, strip user position messages, inject reversed claim. Cheapest option — context already computed, just delta. Not GR yet.

### Key insight

The mediator is an information boundary. The discussion agent never sees raw user messages — only mediator-curated versions. This inverts the sycophancy dynamic: the agent can't agree with the user because it doesn't know what the user thinks.

### Recall entries

- "when agreement momentum" (pushback.md fragment — 3+ consecutive agreements trigger)
- The existing `d:` hook protocol failed to prevent the cascade in practice
