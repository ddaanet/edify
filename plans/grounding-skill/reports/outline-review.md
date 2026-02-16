# Outline Review: Grounding Skill

**Artifact**: plans/grounding-skill/outline.md
**Date**: 2026-02-16T10:05:00Z
**Mode**: review + fix-all

## Summary

Outline is sound and well-structured. Core approach (diverge-converge with parallel internal+external branches) is clearly articulated and grounded in research. Primary gaps were in parameterization detail and phase structure documentation — all fixed. Ready for implementation.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: 4-phase pattern | Approach, D-5, Scope (In scope), Structure | Complete | Scope → Diverge → Converge → Output documented with phase detail |
| FR-2: Param - branch type | D-3, Scope (In scope) | Complete | Brainstorm vs explore in grounding-criteria.md |
| FR-3: Param - model tier | D-3, Scope (In scope) | Complete | Model tier selection guidance in grounding-criteria.md |
| FR-4: Param - breadth | D-3, Scope (In scope) | Complete | Research breadth in grounding-criteria.md |
| FR-5: Param - output format | D-3, Scope (In scope) | Complete | Output format selection in grounding-criteria.md |
| FR-6: Quality label | D-4, Scope (In scope) | Complete | Strong/Moderate/Thin/None mandatory with evidence |
| NFR-1: Prioritize pattern | Approach, Structure | Complete | SKILL.md + references/ structure matches |
| FR-7: Trigger criteria | Scope (In scope), D-1 | Complete | Trigger criteria in grounding-criteria.md |
| FR-8: Two-branch diverge | D-5 | Complete | Core innovation — internal + external parallel |
| FR-9: Output location | D-6 | Complete | plans/reports/ convention documented |

**Traceability Assessment**: All requirements covered with explicit outline sections.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Inconsistent word count target for SKILL.md**
   - Location: Lines 7 and 52
   - Problem: Line 7 said "~700 words", line 52 said "~800 words" — creates ambiguity for implementation
   - Fix: Reconciled to ~800 words (line 7 updated) — more realistic for 4-phase procedure with parameterization
   - **Status**: FIXED

2. **Parameterization details deferred without mapping**
   - Location: D-3, references/grounding-criteria.md structure
   - Problem: D-3 said parameters are "documented as decision points" but didn't specify how this maps to grounding-criteria.md content
   - Fix: Added explicit mapping — parameter selection guidance lives in grounding-criteria.md (when to use brainstorm vs explore, model tier matching, breadth tradeoffs)
   - **Status**: FIXED

3. **Missing 4-phase structure detail in outline body**
   - Location: Scope (In scope) section
   - Problem: Outline mentioned "4-phase procedure" but didn't document what the phases are — Scope/Diverge/Converge/Output were implicit from research synthesis
   - Fix: Expanded In scope section with explicit phase breakdown and what each phase does
   - **Status**: FIXED

### Minor Issues

1. **Open questions not resolved**
   - Location: Open Questions section (Q-1, Q-2)
   - Problem: Questions had leans but no decisions — leaves ambiguity for implementation
   - Fix: Converted to decisions (D-7: search query templates, D-8: structured convergence template)
   - **Status**: FIXED

2. **Integration notes vague on placement**
   - Location: Scope (In scope) — "Integration notes for existing workflows"
   - Problem: Didn't specify what form integration notes take or where they live (separate doc, SKILL.md body, grounding-criteria.md)
   - Fix: Clarified — integration guidance embedded in SKILL.md body (when to invoke from design/prioritize workflows)
   - **Status**: FIXED

3. **references/ word count too low**
   - Location: Structure section, grounding-criteria.md
   - Problem: ~600 words doesn't match prioritize skill reference pattern (scoring-tables.md is ~950 words) — grounding-criteria.md will cover trigger criteria, quality labels, parameterization, search templates, convergence template
   - Fix: Increased to ~900 words to match scope and reference pattern complexity
   - **Status**: FIXED

## Fixes Applied

- Line 7 — Changed SKILL.md target from ~700 to ~800 words (consistency with line 52)
- D-3 — Added sentence mapping parameter guidance to grounding-criteria.md location
- Scope (In scope) — Expanded with 4-phase breakdown (Phase 1-4 with descriptions)
- Scope (In scope) — Expanded grounding-criteria.md contents list (trigger criteria, quality labels, parameterization, search templates)
- Scope (In scope) — Changed "Integration notes" to "Integration guidance embedded in SKILL.md body"
- Open Questions section — Replaced with "Decisions (from Open Questions)" containing D-7 and D-8
- Structure section — Increased grounding-criteria.md word count from ~600 to ~900 and expanded content description

## Positive Observations

- **Clear core innovation**: Two-branch diverge (D-5) is well-articulated as the key pattern preventing ungrounded confabulation
- **Strong research grounding**: Outline explicitly maps to Double Diamond, Rapid Review, and RAG frameworks from research synthesis
- **Scope discipline**: Out of scope section correctly defers automated detection and retroactive skill updates to future work
- **Follows proven pattern**: Structure matches prioritize skill (SKILL.md + references/) which successfully implemented similar research-grounded methodology
- **Explicit quality signal**: D-4 makes grounding quality visible via mandatory label — prevents implicit/hidden grounding gaps
- **Correct artifact placement**: D-6 aligns with learnings entry on research deliverable location (plans/reports/)

## Recommendations

- **Implementation order**: Create grounding-criteria.md first (establishes trigger criteria, quality labels, parameter selection guidance), then SKILL.md (references grounding-criteria.md for detailed content). Same order as prioritize skill implementation.
- **Search query templates**: When writing grounding-criteria.md, provide 3-5 search query templates covering common grounding scenarios (methodology selection, framework adaptation, taxonomy creation, best practice synthesis). Agent can adapt templates to specific context.
- **Convergence template structure**: Model after prioritize skill's scoring table — required sections with explicit evidence fields. Suggested sections: Framework Mapping (internal → external), Grounding Assessment (quality label + evidence), Sources (with links).
- **Integration testing**: After implementation, test skill invocation from two contexts: (1) during design session when creating evaluation framework, (2) during ad-hoc research task when producing methodology. Verify parameterization works in both contexts.

---

**Ready for user presentation**: Yes
