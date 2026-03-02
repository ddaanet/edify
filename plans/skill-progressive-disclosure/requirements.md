# Skill Progressive Disclosure

## Requirements

### Functional Requirements

**FR-1: Segment /design SKILL.md at gate boundaries**
Extract content beyond Phase 0 (triage + routing) into `references/` files loaded conditionally via Read instructions at gate boundaries.

Segments:
- Initial load (~150 lines): Frontmatter, header, Phase 0 (requirements-clarity gate, artifact check, triage recall, classification criteria, work type, composite decomposition, classification gate, routing, companion tasks). Covers Simple (direct execution) and Moderate (route to /runbook) fast exits.
- `references/write-outline.md`: Loaded on Complex path. Phase A (requirements checkpoint, documentation checkpoint, explore, research, outline, complexity re-check, review). Ends at outline sufficiency gate.
- `references/write-design.md`: Loaded only when full design needed. Phase B (discussion protocol ref), Phase C (design generation, review, execution readiness). Constraints section.

Acceptance criteria:
- SKILL.md body ≤200 lines after extraction (frontmatter + Phase 0 + segment Read instructions + Continuation)
- Each segment boundary has an explicit Read instruction at the gate that routes deeper
- Simple/Moderate paths never trigger Read of write-outline.md or write-design.md
- Complex path loads write-outline.md at Phase A entry; loads write-design.md only if outline insufficient
- Continuation section remains in SKILL.md (needed on all paths)
- Existing references (design-content-rules, discussion-protocol, research-protocol) remain unchanged — those are deep-path content within segments, not segments themselves

**FR-2: Segment /runbook SKILL.md at gate boundaries**
Extract content beyond tier assessment into `references/` files loaded conditionally via Read instructions at gate boundaries.

Segments:
- Initial load (~200 lines): Frontmatter, header, per-phase type model, model assignment, three-tier assessment (criteria + Tier 1 + Tier 2). Covers Tier 1 (direct) and Tier 2 (lightweight delegation) fast exits.
- `references/tier3-outline-process.md`: Loaded on Tier 3 path. Planning Process Phases 0.5-0.95 (discovery through sufficiency). The existing `references/tier3-planning-process.md` covers this — may need restructuring or renaming.
- `references/tier3-expansion-process.md`: Loaded past outline sufficiency. Phases 1-4 (expansion, assembly, review, prepare-runbook.py). Checkpoints, testing strategy, cycle/step ordering, recall resolution patterns, common pitfalls, template structure.

Acceptance criteria:
- SKILL.md body ≤250 lines after extraction (frontmatter + intro + type model + model assignment + tier assessment + segment Read instructions + Continuation)
- Tier 1/Tier 2 paths never trigger Read of tier3 segments
- Tier 3 loads tier3-outline-process.md at planning entry; loads tier3-expansion-process.md only past sufficiency
- Continuation section remains in SKILL.md
- Existing references (patterns, general-patterns, anti-patterns, error-handling, examples, tdd-cycle-planning, conformance-validation) remain as deep-path content within segments

**FR-3: Verb-oriented segment naming**
New segment files use verb-oriented names to avoid confusion with plan artifacts they produce.

Acceptance criteria:
- /design segments: `write-outline.md`, `write-design.md` (not `outline.md`, `design.md`)
- /runbook segments: verb-oriented names distinguishable from artifacts (outline.md, runbook.md)
- Naming convention documented in a comment or section header at each Read instruction site

**FR-4: Gate boundary Read instructions**
Each segment boundary uses the existing `Read references/<file>.md` pattern — an explicit instruction that the executing agent processes as a tool call.

Acceptance criteria:
- Read instructions placed at the decision point that determines whether the deeper path is needed
- Each Read instruction includes a 1-line description of what the segment contains and when to load it
- Read instructions are the ONLY way to access segment content (no @-references, no implicit loading)

**FR-5: Preserve skill behavior**
Segmentation is a structural refactor — no behavioral changes to either skill.

Acceptance criteria:
- All execution paths produce identical outcomes before and after segmentation
- Gate decision logic (classification, tier assessment, sufficiency) stays in SKILL.md initial load
- Content moved to segments is byte-identical (no rewording, no reordering)
- Existing Read instructions within segments (e.g., `Read references/design-content-rules.md` inside write-design.md) remain as nested conditional loads

### Non-Functional Requirements

**NFR-1: Initial load token reduction**
The initial load of each skill should be substantially smaller than the full skill, reducing attention competition from irrelevant path content.

Acceptance criteria:
- /design initial load is <45% of current total SKILL.md line count
- /runbook initial load is <55% of current total SKILL.md line count

### Constraints

**C-1: Source files are in `agent-core/skills/`**
`.claude/skills/` contains symlinks or copies managed by `just sync-to-parent`. All edits target `agent-core/skills/<skill>/SKILL.md` and `agent-core/skills/<skill>/references/`.

**C-2: @-references not available in SKILL.md**
SKILL.md files do not support `@file.md` references (only CLAUDE.md does). Segment loading must use explicit Read instructions that the executing agent processes as tool calls.

**C-3: Scope is /design and /runbook only**
Other skills are out of scope regardless of size.

### Out of Scope

- Restructuring or rewriting skill content (this is extraction, not redesign)
- Modifying existing reference files (design-content-rules, discussion-protocol, etc.)
- Changing the gate logic or routing decisions within either skill
- Applying progressive disclosure to other skills
- Changing skill frontmatter or description fields
- Creating automated segment loading infrastructure (the Read instruction pattern is sufficient)

### Dependencies

- `just sync-to-parent` must work after reference file additions (verify symlink propagation includes new files)

### References

- `plans/skill-progressive-disclosure/brief.md` — original design sketch from discussion session
- `plans/skill-progressive-disclosure/recall-artifact.md` — recall entries informing requirements

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` before design (skill file structure modifications)
