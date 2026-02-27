# Review: Design Skill Integration (FR-1, FR-9)

**Scope**: Uncommitted changes to `agent-core/skills/design/SKILL.md` (submodule working tree)
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

Four changes integrate the /inline execution lifecycle skill into /design: frontmatter Skill tool addition, FR-1 classification persistence, and FR-9 replacements at Phase B and C.5. All four changes are correctly placed and match the design spec (outline.md D-1, D-3, Integration Points table). One major issue: the "Downstream Consumer" section is now inaccurate (only mentions /runbook, but /inline is now also a downstream consumer).

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Downstream Consumer section incomplete after /inline integration**
   - Location: `agent-core/skills/design/SKILL.md:16-20`
   - Problem: Section says "All planning routes to `/runbook`" with no mention of /inline. After this integration, execution-ready work routes to /inline (Phase B line 332, Phase C.5 line 425). The section title is "Downstream Consumer" (singular) implying one consumer, but there are now two: /runbook (for planning) and /inline (for execution). An agent reading this section would conclude /runbook is the sole downstream path.
   - Suggestion: Update to reflect both consumers with their routing conditions.
   - **Status:** FIXED

### Minor Issues

None.

## Fixes Applied

- `agent-core/skills/design/SKILL.md:16-20` -- Updated "Downstream Consumer" section to "Downstream Consumers" (plural), added /inline as execution consumer alongside /runbook as planning consumer. Preserved the TDD/general phase-type note since it still applies to the /runbook path.

## Verification Criteria

| Criterion | Result | Evidence |
|-----------|--------|---------|
| 1. Existing routing paths preserved (Simple, Moderate, Complex, Defect) | Pass | Lines 119-127 unchanged in diff |
| 2. Phase B not-execution-ready and insufficient paths unchanged | Pass | Lines 334-338 unchanged in diff |
| 3. Phase C.5 not-execution-ready path unchanged | Pass | Line 426 unchanged in diff |
| 4. FR-1 Write step placed correctly | Pass | Line 115, after classification block (line 113), before Routing (line 117) |
| 5. FR-9 invocations use correct format | Pass | Lines 332, 425: `/inline plans/<job> execute` matches D-1 named entry point |
| 6. Frontmatter Skill addition correct | Pass | Line 8: `Skill` appended to allowed-tools list |
| 7. No behavioral regression in any conditional branch | Pass | Diff touches only 4 locations; all other branches verified unchanged |

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|---------|
| FR-1 | Satisfied | Line 115: Write step after classification block, verbatim to `plans/<job>/classification.md`, references C-2 and FR-5/FR-6 |
| FR-9 | Satisfied | Lines 332, 425: Both Phase B and C.5 execution-ready paths invoke `/inline plans/<job> execute` |
| C-1 | Satisfied | /design writes classification.md (line 115); /inline only reads it (per skill design) |
| C-2 | Satisfied | Line 115 says "verbatim" and references C-2 explicitly |
| D-1 | Satisfied | Invocation format `Skill(skill: "inline", args: "plans/<job> execute")` matches named entry point spec |
| D-3 | Satisfied | Classification persistence added at correct location with correct content spec |

## Positive Observations

- Changes are minimal and precisely targeted -- four insertion/replacement points with no collateral edits
- Phase B replacement correctly removes all three inline steps (execute, corrector, handoff) and replaces with single /inline invocation
- Phase C.5 replacement mirrors Phase B format, maintaining consistency between the two exit paths
- FR-1 placement is optimal: after the visible classification block (so the block exists to be written) and before routing (so the file is persisted regardless of which route is taken)
- The classification persistence note correctly cross-references C-2 (verbatim format) and FR-5/FR-6 (downstream consumers)
