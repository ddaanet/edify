# Pushback

## Requirements

### Functional Requirements

**FR-1: Structural pushback in design discussions**
When the user proposes ideas in discussion mode (`d:`), the agent must identify and articulate counterarguments before agreeing. Not devil's advocate theater — genuine evaluation of costs, risks, and alternatives not considered.

**FR-2: Detect agreement momentum**
Identify when the agent has agreed to multiple consecutive proposals without pushback. Signal this pattern to the user or self-correct.

**FR-3: Model selection evaluation**
When creating pending tasks, evaluate model tier against task cognitive requirements (opus for design/architecture/nuanced reasoning, sonnet for balanced work, haiku for mechanical execution). Do not default to sonnet.

### Non-Functional Requirements

**NFR-1: Not sycophancy inversion**
Pushback must be genuine evaluation, not reflexive disagreement. If an idea is good, say so — but articulate why, don't just agree.

**NFR-2: Lightweight mechanism**
Must not add significant latency or token cost to every conversation turn. The cure can't be worse than the disease.

### Constraints

**C-1: Opus design session**
This task requires opus — it's a behavioral/conversational design problem requiring nuanced reasoning about LLM failure modes.

### Out of Scope

- Handoff review agent — rejected on cost/benefit
- Precommit enforcement of model selection — can be circumvented by the writing agent
- Mechanical validation of judgment calls

### Open Questions

- Q-1: Where does pushback live? Fragment (ambient), skill (invoked), hook (injected), or conversation protocol?
- Q-2: Can an LLM reliably push back against its own sycophancy bias, or does this require structural intervention (e.g., a second agent playing adversary)?
- Q-3: Is agreement momentum detectable in-context, or does it require external observation (hook that tracks agreement patterns)?
- Q-4: How to distinguish genuine agreement from sycophantic agreement? The agent may not be able to self-assess.
