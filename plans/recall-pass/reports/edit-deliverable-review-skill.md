# Edit: deliverable-review SKILL.md — Recall Context

**File:** `agent-core/skills/deliverable-review/SKILL.md`
**Location:** Phase 3, Layer 2 cross-cutting checks list (line 106)

## Change

Added one bullet to the "Cross-cutting checks (always)" list:
- Read `plans/<plan>/recall-artifact.md` if present
- Failure-mode entries augment reviewer awareness of project-specific patterns
- Supplements existing axes, does not replace them
- Graceful degradation: if absent, proceed without it

## Design Decisions Embedded

- **FR-4:** Review-stage recall — deliverable-review uses recall context for deeper review
- **D-2:** Content pre-selected at planning time — no filtering logic here; reviewer reads the artifact as-is
- Recall artifact augments awareness of project-specific failure patterns (embedding knowledge in context)

## Constraints Satisfied

- No restructuring of existing Layer 2
- No new phase or section — single bullet added to existing list
- Graceful degradation inline (not a separate section)
- Matches existing skill formatting and density
