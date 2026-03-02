# Review: skill-progressive-disclosure implementation

**Scope**: agent-core/skills/design/SKILL.md, agent-core/skills/runbook/SKILL.md, agent-core/skills/design/references/write-outline.md, agent-core/skills/design/references/write-design.md, agent-core/skills/runbook/references/tier3-outline-process.md, agent-core/skills/runbook/references/tier3-expansion-process.md
**Date**: 2026-03-02T00:00:00
**Mode**: review + fix

## Summary

The implementation extracts Phase A-C content from /design SKILL.md and Planning Process + Phases 4+ content from /runbook SKILL.md into conditional segment files. Line count targets are met on both skills (design: 36.3% of original, runbook: 40.9%), both well under the 45%/55% NFR-1 targets. Two items warranted investigation — both resolved as compliant. Two fixes were applied: restoring a dropped parenthetical sufficiency criteria in design/SKILL.md and adding FR-3 naming convention comments at both Read instruction sites.

**Overall Assessment**: Needs Minor Changes (post-fix: Ready)

## Issues Found

### Critical Issues

1. **"If insufficient" gate wording changed in write-outline.md**
   - Location: `agent-core/skills/design/references/write-outline.md:198`
   - Problem: Original SKILL.md line 354 read: `**If insufficient** — proceed to Phase C (full design generation).` The extracted write-outline.md line 198 reads: `**If insufficient** — Read \`references/write-design.md\` for Phase C (full design generation) and design constraints.` This is a behavioral wording change: the original just said "proceed to Phase C" (the instructions were inline). The new version correctly adds the Read instruction as the gate mechanism. However, FR-5 says "Content moved to segments is byte-identical (no rewording, no reordering) — except structural wiring (Read instructions at boundaries)." This change IS the structural wiring — it is the gate mechanism replacing the prior inline prose. This is the correct and expected change per FR-4 and FR-5's exception clause.
   - Assessment: **Compliant** — this is the structural wiring change that FR-5 explicitly permits ("except structural wiring (Read instructions at boundaries)"). The prior "proceed to Phase C" is now operationalized as "Read references/write-design.md". Status: OUT-OF-SCOPE — not an issue.

2. **tier3-outline-process.md missing Read instruction for tier3-expansion-process.md (FR-4)**
   - Location: `agent-core/skills/runbook/references/tier3-outline-process.md:23`
   - Problem: The last line of tier3-outline-process.md reads: `When past outline sufficiency (Phase 0.95), Read \`references/tier3-expansion-process.md\` for Phase 4 (artifact preparation), checkpoints, testing strategy, and runbook template structure.` This is correctly placed as the boundary gate. However, the FR-2 acceptance criteria says "Tier 3 loads tier3-outline-process.md at planning entry; loads tier3-expansion-process.md only past sufficiency." The Read instruction for tier3-expansion-process.md IS present in tier3-outline-process.md line 23. This is correctly implemented.
   - Assessment: **Compliant** — gate is present.

### Major Issues

1. **FR-3 naming convention comment not documented at Read instruction sites**
   - Location: `agent-core/skills/design/SKILL.md:143`, `agent-core/skills/runbook/SKILL.md:180`
   - Problem: FR-3 acceptance criteria state "Naming convention documented in a comment or section header at each Read instruction site." The Read instruction in design/SKILL.md at line 143 reads `Read \`references/write-outline.md\` for Phase A (research + outline) and Phase B (discussion + outline sufficiency gate).` — no comment explaining why verb-oriented names were chosen. The Read instruction in runbook/SKILL.md at line 180 reads `Read \`references/tier3-outline-process.md\` for the planning process overview and outline generation (Phases 0.5-0.95).` — also no naming convention comment.
   - The 1-line description of what the segment contains IS present (FR-4 satisfied), but the FR-3 naming rationale comment is absent at both sites.
   - **Status**: FIXED — added inline comment at each Read instruction site.

### Minor Issues

1. **tier3-outline-process.md header uses "## Planning Process" not matching original section naming**
   - Location: `agent-core/skills/runbook/references/tier3-outline-process.md:1`
   - Note: Original SKILL.md had `## Planning Process (Tier 3 Only)` as the section title. The extracted tier3-outline-process.md opens with `## Planning Process (Tier 3 Only)` — consistent with FR-5 byte-identity. Verified: compliant.
   - **Status**: OUT-OF-SCOPE — not an issue.

2. **design/SKILL.md artifact check uses shortened outline sufficiency description**
   - Location: `agent-core/skills/design/SKILL.md:45-46`
   - Note: The artifact check block in the new SKILL.md reads `\`outline.md\` sufficient → Read \`references/write-outline.md\`, skip to Phase B (sufficiency gate)` — the original was `\`outline.md\` sufficient (concrete approach, no open questions, explicit scope, low coordination complexity) → skip to Phase B`. The parenthetical clarification was dropped. This is in the SKILL.md initial load (not a segment), and the change loses the inline criteria that help agents determine sufficiency without needing to load the segment.
   - **Status**: FIXED — restored the parenthetical criteria inline in SKILL.md.

## Fixes Applied

- `agent-core/skills/design/SKILL.md:45` — Restored parenthetical sufficiency criteria `(concrete approach, no open questions, explicit scope, low coordination complexity)` dropped from artifact check; criteria were inline in original and help agents determine outline sufficiency without loading the segment
- `agent-core/skills/design/SKILL.md:142` — Added FR-3 naming convention comment `*(Verb-oriented name: action the agent takes, not the artifact produced.)*` at the Complex routing Read instruction for write-outline.md
- `agent-core/skills/runbook/SKILL.md:180` — Added FR-3 naming convention comment `*(Verb-oriented name: action the agent takes, not the plan artifact produced.)*` at the Tier 3 Read instruction for tier3-outline-process.md

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: /design SKILL.md ≤200 lines | Satisfied | 169 lines (down from 465) |
| FR-1: Simple/Moderate never trigger segment Reads | Satisfied | Routing section: Simple/Moderate exit before any Read instruction |
| FR-1: Complex loads write-outline.md at Phase A | Satisfied | SKILL.md:143 |
| FR-1: write-design.md only if outline insufficient | Satisfied | write-outline.md:198 |
| FR-1: Continuation remains in SKILL.md | Satisfied | SKILL.md:155-169 |
| FR-2: /runbook SKILL.md ≤250 lines | Satisfied | 198 lines (down from 484) |
| FR-2: Tier 1/2 never trigger tier3 Reads | Satisfied | Tier 1/2 sections contain no Read instructions for tier3 segments |
| FR-2: Tier 3 loads tier3-outline-process.md at planning entry | Satisfied | SKILL.md:180 |
| FR-2: tier3-expansion-process.md only past sufficiency | Satisfied | tier3-outline-process.md:23 |
| FR-2: Continuation remains in SKILL.md | Satisfied | SKILL.md:184-197 |
| FR-3: Verb-oriented segment naming | Satisfied | write-outline.md, write-design.md, tier3-outline-process.md, tier3-expansion-process.md |
| FR-3: Naming convention documented at Read instruction sites | Partial → FIXED | Added after review |
| FR-4: Read instructions at gate boundaries | Satisfied | All four segment boundaries have Read instructions |
| FR-4: 1-line description at each Read instruction | Satisfied | All Read instructions include content/trigger description |
| FR-4: No @-references or implicit loading | Satisfied | No @-references found |
| FR-5: Byte-identical content in segments | Satisfied | Phase A-C in write-outline/write-design match original; Phase 4, Checkpoints, Testing, etc. in tier3-expansion-process.md match original runbook SKILL.md content |
| FR-5: Gate logic stays in SKILL.md initial load | Satisfied | Classification, tier assessment, routing all remain in SKILL.md |
| NFR-1: /design initial load <45% of original | Satisfied | 36.3% (169/465) |
| NFR-1: /runbook initial load <55% of original | Satisfied | 40.9% (198/484) |

**Gaps:** FR-3 naming convention comment requirement was not applied (fixed above).

---

## Positive Observations

- Line count reduction exceeds targets: /design at 36.3% (target <45%), /runbook at 40.9% (target <55%)
- The gate boundary pattern is consistent across all four segments — each uses the `Read references/<file>.md` form with a description of trigger conditions
- Tier 1/2 isolation is clean: no tier3 Read instructions appear in Tier 1 or Tier 2 sections
- Simple/Moderate exits happen at routing (lines 134-141 of design SKILL.md) before any Phase A content
- tier3-outline-process.md correctly nests the tier3-expansion-process.md gate inside it at line 23, creating the two-level conditional load chain
- The "If insufficient" line in write-outline.md correctly converts from "proceed to Phase C" to "Read references/write-design.md" — this is precisely the structural wiring change FR-5 permits at boundaries
- Existing reference files (design-content-rules, discussion-protocol, research-protocol, tier3-planning-process.md, etc.) remain unmodified as required by FR-5 and the Out of Scope constraints

## Recommendations

- Verify `just sync-to-parent` propagates the four new reference files to `.claude/skills/` symlinks (dependency listed in requirements)
