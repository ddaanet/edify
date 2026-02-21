# Outline Review: planstate-delivered

**Artifact**: plans/planstate-delivered/outline.md
**Date**: 2026-02-21
**Mode**: review + fix-all
**Requirements source**: plans/planstate-delivered/brief.md (D-1 through D-6, deliverable review gate, scope)
**Grounding source**: plans/reports/lifecycle-terminology-grounding.md

## Summary

Outline is well-structured with clear phase breakdown, grounded terminology changes, and explicit scope boundaries. All 7 decisions from brief + grounding are traced. Issues found were clarity and completeness gaps (underspecified in-main path, missing marker format, ambiguous empty-string returns), not soundness problems. All fixed inline.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| D-1: Post-ready review loop | Key Decisions D-1 | Complete | Updated with grounded names |
| D-2: delivered.md at merge + in-main | Key Decisions D-2, Phase 2, Phase 3 | Complete | FIXED: split into worktree/in-main paths, Phase 3 now covers in-main |
| D-3: Marker file content (date + source) | Key Decisions D-3 | Complete | FIXED: added format specification |
| D-4: _determine_status priority | Key Decisions D-4, Phase 1 | Complete | Priority chain + rework.md deletion mechanism |
| D-5: _derive_next_action returns | Key Decisions D-5, Phase 1 | Complete | FIXED: `""` instead of ambiguous "empty" |
| D-6: #status excludes delivered | Key Decisions D-6, Phase 3 | Complete | Agent-side filtering in execute-rule.md |
| D-7: Terminology grounding | Key Decisions D-7, Phase 3 | Complete | New decision from grounding report |
| Deliverable review gate | Scope OUT clarification | Complete | FIXED: clarified shortcut already exists; this job adds marker creation |
| Scope: 4 marker files | Phase 1 (_collect_artifacts) | Complete | FIXED: explicit filenames listed |
| Scope: tests | Phase 1, Phase 2 | Complete | TDD phases include test specifications |

**Traceability Assessment**: All requirements covered. Two grounding-driven changes (D-1 rename, D-7 new decision) properly traced to lifecycle-terminology-grounding.md.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **D-2 in-main path underspecified**
   - Location: Key Decisions D-2, Phase 2
   - Problem: Brief specifies two delivery paths (worktree merge vs in-main). Outline mentioned in-main in D-2 but didn't explain what triggers it, and Phase 2 only covered the worktree path. The in-main path (deliverable-review creates both reviewed.md and delivered.md) had no phase assignment.
   - Fix: Split D-2 into two explicit paths with context. Added in-main path to Phase 3 (deliverable-review skill update). Added Phase 2 note cross-referencing Phase 3.
   - **Status**: FIXED

2. **Marker file content format unspecified**
   - Location: Key Decisions D-3
   - Problem: Brief says "date, source. Not empty." Outline repeated this but didn't specify format. Three producers (merge, orchestrate, deliverable-review) need a shared contract.
   - Fix: Added format specification: ISO date line 1, source identifier line 2. Noted content is human-readable, not parsed.
   - **Status**: FIXED

3. **Deliverable review shortcut scope ambiguity**
   - Location: Scope OUT
   - Problem: Brief lists "deliverable review as pre-merge gate with complexity shortcut" as IN scope. Outline put "self-review shortcut" in OUT scope without explaining that the shortcut logic already exists and only marker file creation is new.
   - Fix: Clarified that shortcut criteria already exist in deliverable-review skill; this job adds marker file creation integration, not shortcut logic.
   - **Status**: FIXED

### Minor Issues

1. **Ambiguous "empty" next action returns**
   - Location: Key Decisions D-5
   - Problem: "empty" for rework/reviewed/delivered could mean empty string, null, or omitted. Existing code returns `""` for unknown states.
   - Fix: Changed to explicit `""` to match existing codebase pattern.
   - **Status**: FIXED

2. **Phase 2 missing in-main path cross-reference**
   - Location: Phase Breakdown, Phase 2
   - Problem: Reader might expect Phase 2 to handle all D-2 delivery. No indication that in-main path is elsewhere.
   - Fix: Added note clarifying in-main delivery is in Phase 3.
   - **Status**: FIXED

3. **Phase references assumed step numbering**
   - Location: Phase 3, original "step 6" reference
   - Problem: "orchestrate/SKILL.md step 6" assumes stable step numbering. If skill is restructured, reference breaks.
   - Fix: Changed to content-based description: "at orchestration completion (after final step commit)".
   - **Status**: FIXED

4. **Missing decision traceability in phases**
   - Location: Phase Breakdown, all phases
   - Problem: No explicit D-* references in phase descriptions. Reader must mentally map phases to decisions.
   - Fix: Added D-* references to each phase header and key items.
   - **Status**: FIXED

5. **No resume completeness for review loop**
   - Location: Scope section
   - Problem: The rework/review-pending loop is a state machine. If rework.md deletion fails mid-re-review, plan is stuck with no documented recovery.
   - Fix: Added resume edge case note in Scope section with manual recovery path.
   - **Status**: FIXED

6. **_collect_artifacts marker files not listed explicitly**
   - Location: Phase 1
   - Problem: "Add marker file detection" without naming the 4 files. Implementation agent must cross-reference D-3/D-4 to know which files.
   - Fix: Listed all 4 marker filenames inline.
   - **Status**: FIXED

## Fixes Applied

- D-2: Split single sentence into two delivery paths (worktree + in-main) with context
- D-3: Added marker file format specification (ISO date + source identifier)
- D-5: Changed "empty" to `""` for 3 next-action returns
- Phase 1: Added D-* references, listed 4 marker filenames explicitly, clarified mixed-marker test scenario
- Phase 2: Added D-2 worktree path label, cross-reference to Phase 3 for in-main path
- Phase 3: Added D-* references, changed "step 6" to content-based description, added in-main delivered.md creation
- Scope OUT: Clarified deliverable review shortcut already exists
- Scope: Added resume edge case for rework.md deletion failure

## Positive Observations

- Grounding integration is thorough: two name changes (defective/completed) with evidence-backed rationale, one new decision (D-7)
- Phase breakdown cleanly separates TDD code (Phases 1-2) from prose updates (Phase 3)
- D-4 review loop mechanism (rework > review-pending priority + deletion) resolves the grounding constraint elegantly
- Affected files list is complete and verified against filesystem
- Scope boundaries are explicit with clear IN/OUT distinction

## Recommendations

- During Phase 1, verify `PlanState` model in `models.py` can accommodate the 4 new status strings (no enum constraint limiting values)
- Phase 2 merge integration should handle the edge case where `reviewed.md` exists but the merge fails partway through (no `delivered.md` written until merge commit succeeds)
- Consider whether `_determine_status` docstring (currently "ready > planned > designed > requirements") needs updating as part of Phase 1

---

**Ready for user presentation**: Yes
