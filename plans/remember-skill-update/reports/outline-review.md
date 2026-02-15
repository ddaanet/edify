# Outline Review: remember-skill-update

**Artifact**: plans/remember-skill-update/outline.md
**Date**: 2026-02-15T13:15:00-08:00
**Mode**: review + fix-all

## Summary

The outline addresses all three functional requirements with a clear two-workstream approach: enforcing trigger-compatible titles at creation time (FR-1, FR-2) through three enforcement layers, and analyzing frozen-domain recall alternatives (FR-3). The structural and scope sections are well-defined. However, several clarity and completeness issues need addressing: missing implementation guidance for handoff skill updates, vague "Key Decisions" without resolution paths, incomplete phasing strategy, and missing validation test requirements.

**Overall Assessment**: Needs Iteration

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Workstream 1, Step 2 | Complete | Semantic guidance at learning staging time |
| FR-2 | Workstream 1, Step 3 | Complete | Trigger derivation from title without rephrase |
| FR-3 | Workstream 2 | Complete | Analysis of alternatives to rule files |

**Traceability Assessment**: All requirements covered

## Review Findings

### Critical Issues

None identified.

### Major Issues

1. **Missing handoff skill implementation guidance**
   - Location: Workstream 1, Step 2 ("Updated in: remember skill SKILL.md, remember-task agent, handoff skill")
   - Problem: Handoff skill update is mentioned but no implementation details provided. Handoff creates learning titles — this is the primary enforcement point for FR-1/FR-2, but outline doesn't specify what changes handoff needs or where in handoff flow guidance appears.
   - Fix: Added implementation details to Workstream 1, Step 2
   - **Status**: FIXED

2. **Phase type assignment incomplete**
   - Location: Line 38 ("Phase types: TDD for validation code (learnings.py), general for skill/agent documentation updates")
   - Problem: Phase types mentioned but no phasing structure defined. Which work happens in which phase? What's the dependency order? TDD validation should precede documentation that references new constraints.
   - Fix: Added phasing structure section after Workstream 2
   - **Status**: FIXED

3. **Key Decisions section without resolution strategy**
   - Location: Lines 55-60 (Key Decisions section)
   - Problem: Four open questions listed but no indication of when/how they'll be resolved, or whether they block implementation. This creates ambiguity about scope and readiness.
   - Fix: Added resolution approach for each decision
   - **Status**: FIXED

4. **Missing validation test requirements**
   - Location: Workstream 1, Step 1
   - Problem: Proposes new structural validation in learnings.py but doesn't specify test requirements. TDD workflow requires test coverage specification.
   - Fix: Added test requirements to Step 1
   - **Status**: FIXED

### Minor Issues

1. **Vague "matching updates" for remember-task agent**
   - Location: Workstream 1, Step 2 ("remember-task agent mirrors the change")
   - Problem: Doesn't specify which sections of remember-task.md need updating. Agent has pre-consolidation checks, consolidation protocol, reporting format — which parts change?
   - Fix: Specified affected sections
   - **Status**: FIXED

2. **Hyphen handling decision lacks impact analysis**
   - Location: Key Decisions #1
   - Problem: Asks about hyphen handling but doesn't note impact: current learnings.md has hyphenated titles (e.g., "zero-ambiguity"), memory-index trigger format explicitly excludes hyphens (line 22). This is a data migration issue, not just a validation choice.
   - Fix: Added impact note to decision
   - **Status**: FIXED

3. **Frozen-domain output format unclear**
   - Location: Workstream 2, line 53 ("Output: Analysis table with recommendation")
   - Problem: Doesn't specify where analysis output lands (design.md section? separate report? inline in outline?) or what format recommendation takes.
   - Fix: Clarified output location
   - **Status**: FIXED

4. **Missing precommit integration note**
   - Location: Workstream 1, Step 1
   - Problem: New validation constraints but no mention of precommit integration (existing learnings.py already runs in precommit, changes should preserve this).
   - Fix: Added precommit note to Step 1
   - **Status**: FIXED

5. **Scope OUT missing agent-core/bin/compress-key.py**
   - Location: Scope section
   - Problem: compress-key.py is mentioned in Step 3 ("compress-key.py validates against title text directly") but not listed in IN scope. If it's being modified, should be IN; if unchanged, clarify.
   - Fix: Added compress-key.py to OUT scope with rationale
   - **Status**: FIXED

## Fixes Applied

All fixes applied to `/Users/david/code/claudeutils/plans/remember-skill-update/outline.md`:

**Major fixes:**
- Lines 24-30 — Added handoff skill implementation details (where guidance appears, what sections update, trigger framing enforcement)
- After line 60 — Added "Implementation Phasing" section with 3-phase structure and dependencies
- Lines 56-60 — Added resolution approach to each Key Decision item
- Lines 19-22 — Added test requirements for structural validation

**Minor fixes:**
- Line 36 — Specified remember-task.md affected sections (consolidation protocol Step 4a, reporting format discovery updates section)
- Line 57 — Added impact note to hyphen handling decision (data migration for existing learnings)
- Line 53 — Clarified frozen-domain output location (design.md dedicated section)
- Line 23 — Added precommit integration note
- After line 75 — Added compress-key.py to OUT scope with rationale (validation logic unchanged, usage context shifts to title-based validation)

## Positive Observations

**Clear workstream separation**: Two independent workstreams with distinct outputs (enforcement implementation vs. analysis recommendation) allows parallel work and avoids scope creep.

**Three-layer enforcement strategy**: Structural validation (code), semantic guidance (documentation), and pipeline alignment (protocol) provides defense-in-depth for trigger framing.

**Concrete examples from session context**: Using 24 key renames as anti-pattern/correct-pattern examples grounds guidance in real failure modes.

**Explicit scope boundaries**: IN/OUT section clearly delineates what's changing vs. what's deferred (e.g., /when runtime resolution, memory index validation pipeline).

**Evaluation criteria for frozen-domain options**: Analysis table with reliability/cost/maintenance axes provides structured comparison framework.

## Recommendations

**Prioritize Workstream 1 Phase 1 (TDD validation)**: Get structural constraints enforced via precommit before updating documentation. This prevents new learnings from violating constraints while documentation is being written.

**Resolve Key Decision #1 (hyphen handling) early**: Current learnings.md has hyphenated titles, proposed validation disallows hyphens. This is a breaking change requiring migration decision before implementation starts. Recommend: allow hyphens in learning titles (aligns with current usage), enforce no-hyphens only in memory-index triggers (where it's already required).

**Consider splitting Workstream 2 into separate task**: Analysis recommendation is a research deliverable, not implementation. If hook-based solution is recommended, implementation becomes a new task with its own design/runbook. This keeps current task focused on title-trigger alignment.

**User input needed on agent duplication (Key Decision #3)**: Remember-task.md manually mirrors SKILL.md steps. Fixing duplication adds complexity; maintaining duplication risks drift. This is a maintenance trade-off requiring user preference.

---

**Ready for user presentation**: Yes
