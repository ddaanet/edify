# Edit Report: Design Skill A.1 Recall Artifact Generation

## What was added

New sub-section **Recall Artifact Generation** added to A.1 Documentation Checkpoint in `agent-core/skills/design/SKILL.md` (lines 114-135 post-edit).

## Location

Between A.1's existing "Design decision escalation" note and A.2 (Explore Codebase). No existing content was modified.

## Content summary

- **Purpose paragraph:** Explains why persistence is needed (findings die with context window, downstream stages need them)
- **Process:** Write `plans/<job>/recall-artifact.md` after documentation loading; uses already-loaded content, no re-reading
- **Artifact format:** Structured markdown with entry heading name, source path, relevance note, content excerpt (code block example included)
- **Selection criteria:** Curated (informed decisions or constrain implementation), not exhaustive; negative constraint co-located per DO NOT rule placement guidance
- **Staleness:** Accepted; design-time snapshot, refresh via re-running design pass
- **Output path:** `plans/<job>/recall-artifact.md`

## Design decisions embedded

- **D-1:** Extends A.1 inline, no new phase added
- **D-4:** Structured markdown format with heading name, source path, relevance note, content excerpt
- **D-5:** Staleness explicitly accepted with rationale
- **D-7:** No separate mid-design recall pass; A.1 checkpoint is the single generation point

## Constraints verified

- No separate phase added
- A.1 hierarchy table unchanged
- No other sections modified (A.0, A.2-A.6, Phase B, C unchanged)
- Placed between A.1 content and A.2
- Dense prose matching existing skill tone
