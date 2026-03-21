## Invariant-tracking prototype — prose only, no code

### Origin

During /proof of outline-proofing design (session 83b685c4), discussion about classification of agentic-prose work revealed a missing concept: requirements should be traceable through all pipeline artifacts (outline → design → runbook → correctors → tests).

### Key insights from discussion

**Prose as universal approximator:** A single sentence in a SKILL.md IS an implementation — the LLM executes it. "Isolated prose edit" can have arbitrarily large behavioral impact. The edit is small; what it approximates isn't.

**Interaction graph determines ceremony:** Fan-out (file count) doesn't determine complexity. Edge count (semantic coupling between prose edits) does. Corrector updates are physically independent files but semantically coupled through output format contracts.

**Requirement vs design conflation:** "Track requirements to all artifacts" is a requirement. "Edit outline-corrector to add traceability criteria" is a design decision. The proof session repeatedly conflated these levels — jumping to implementation before resolving the contract.

**Option A rollout:** The agreed path was to prototype with prose-only changes first — adding traceability sections to planning artifacts, enforced by corrector criteria updates. No code changes. Validates what invariant-prose looks like before any infrastructure.

### What to prototype

Express invariants as:
- Recall entries ("when modifying X, invariant I-N applies")
- Corrector criteria additions (traceability checks in outline-corrector, runbook-corrector, etc.)
- Planning artifact format additions (requirements → invariant mapping sections)

Scope: 6-8 skills, 4 corrector agents, all planning artifact formats. Despite high fan-out, the prototype is exploration-weight — validating the concept, not shipping pipeline changes.

### Open questions

- How do invariants differ from recall "when" entries? Different query shape (categorical "what must hold about X" vs situational "when doing X")
- Does the current recall taxonomy need a new category, or do existing entries already encode invariants implicitly?
- What does the FR → invariant → test → recall traceability chain look like concretely?

### Recall entries (from proof session discussion)

- "when routing moderate classification to runbook" — structural incompleteness gap
- "when classifying composite tasks" — decompose before classify
