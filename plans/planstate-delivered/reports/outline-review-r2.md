# Outline Review R2: planstate-delivered

**Artifact**: plans/planstate-delivered/outline.md
**Date**: 2026-02-21
**Mode**: review + fix-all
**Requirements source**: plans/planstate-delivered/brief.md (D-1 through D-6, deliverable review gate, scope)
**Grounding source**: plans/reports/lifecycle-terminology-grounding.md
**Prior review**: plans/planstate-delivered/reports/outline-review.md (R1 — stale, reviewed marker-file version)

## Summary

R2 review following the D-3 revision from marker files to single `lifecycle.md`. The outline is sound and complete. The lifecycle.md approach resolves the grounding report's design constraint (review loop ambiguity with existence-based detection) elegantly. All 7 decisions traced. Fixes applied were completeness and clarity improvements — no soundness or feasibility issues.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| D-1: Post-ready review loop | Key Decisions D-1 | Complete | Updated with grounded names (rework, reviewed) |
| D-2: Two delivery paths | Key Decisions D-2, Phase 2, Phase 3 | Complete | Worktree path in Phase 2, in-main path in Phase 3 |
| D-3: lifecycle.md format | Key Decisions D-3 | Complete | FIXED: added concrete example |
| D-4: Status priority | Key Decisions D-4, Phase 1 | Complete | Simplified: last entry wins for post-ready |
| D-5: Next actions | Key Decisions D-5, Phase 1 | Complete | FIXED: explicit match arms listed in Phase 1 |
| D-6: #status excludes delivered | Key Decisions D-6, Phase 3 | Complete | Agent-side filtering in execute-rule.md |
| D-7: Terminology grounding | Key Decisions D-7, Phase 3 | Complete | New decision from grounding report |
| Deliverable review gate | Scope OUT clarification | Complete | Shortcut logic already exists; this job adds lifecycle entry creation |
| Scope: tests | Phase 1, Phase 2 | Complete | TDD phases with test specifications |

**Traceability Assessment**: All requirements covered. D-3 revision (lifecycle.md vs marker files) correctly propagated through D-4, Phase 1, Phase 2, and Scope.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **No lifecycle.md format example**
   - Location: Key Decisions D-3
   - Problem: Format description (`{ISO-date} {state} — {source}`) is abstract. A multi-entry example showing the review loop cycle would make the append-only semantics concrete and unambiguous for implementation agents.
   - Fix: Added 5-line example showing full review loop: review-pending → rework → review-pending → reviewed → delivered.
   - **Status**: FIXED

2. **Phase 1 missing valid state enumeration and line format**
   - Location: Phase Breakdown, Phase 1
   - Problem: "Parse last line, extract state keyword" without listing which state keywords are valid or what the line format is. Implementation agent must cross-reference D-3 and D-5 to determine the state vocabulary and parsing format.
   - Fix: Added valid states list and line format reference inline.
   - **Status**: FIXED

3. **Phase 2 format inconsistency risk**
   - Location: Phase Breakdown, Phase 2
   - Problem: Phase 2 writes lifecycle.md entries but didn't reference the D-3 line format. Could diverge from Phase 1's parsing expectations.
   - Fix: Specified exact entry format (`{date} delivered — _worktree merge`) and noted dependency on Phase 1 parsing.
   - **Status**: FIXED

### Minor Issues

1. **Missing models.py verification note**
   - Location: Affected Files
   - Problem: `PlanState.status` is `str` (verified in source), so new status values require no model changes. But Affected Files didn't mention models.py, leaving implementation agents uncertain about whether an enum or validator constrains values.
   - Fix: Added models.py entry noting "no changes needed" with rationale.
   - **Status**: FIXED

2. **Phase 1 missing malformed line test case**
   - Location: Phase 1 Tests list
   - Problem: lifecycle.md is append-only but could have partial writes (interrupted process) or hand-edited content. No test for malformed/unparseable lines.
   - Fix: Added "malformed line handling" to test list.
   - **Status**: FIXED

3. **Phase 2 missing non-reviewed state test case**
   - Location: Phase 2 Tests list
   - Problem: "Skips non-reviewed plans" only covers plans without lifecycle.md. Missing test for plans WITH lifecycle.md in a non-reviewed state (e.g., rework, review-pending).
   - Fix: Added "handles plans with lifecycle.md in non-reviewed state" to test list.
   - **Status**: FIXED

4. **Phase 3 missing D-2 reference in header**
   - Location: Phase 3 header
   - Problem: Phase 3 handles the in-main delivery path (D-2) but header only listed D-6, D-7. Reader scanning headers wouldn't know D-2 is split across Phase 2 and Phase 3.
   - Fix: Added "D-2 in-main path" to Phase 3 header.
   - **Status**: FIXED

5. **Phase 3 re-review trigger unclear**
   - Location: Phase 3 deliverable-review bullet
   - Problem: "On re-review of plan in rework state, append review-pending entry" didn't explain why (re-entering the review loop).
   - Fix: Added parenthetical "(re-entering review loop — no deletion needed)".
   - **Status**: FIXED

6. **Phase 3 in-main trigger condition vague**
   - Location: Phase 3 deliverable-review bullet
   - Problem: "For in-main plans" without defining what makes a plan "in-main."
   - Fix: Added "(no worktree, execution on main)" clarification.
   - **Status**: FIXED

7. **Scope IN missing "parsing"**
   - Location: Scope section
   - Problem: "lifecycle.md file format" without "parsing" — the format definition and the parsing logic are both in scope.
   - Fix: Changed to "lifecycle.md file format and parsing."
   - **Status**: FIXED

8. **Resume completeness — R1 was stale**
   - Location: Scope section
   - Problem: R1 review added a resume note about "rework.md deletion failure" which no longer applies (lifecycle.md has no deletion). Needed replacement resume analysis for append-only semantics.
   - Fix: Added resume edge case note: append-only means interrupted writes leave partial lines (truncate and re-append), no stuck-state risk from review loop.
   - **Status**: FIXED

9. **Phase 1 D-5 match arms not enumerated**
   - Location: Phase 1 `_derive_next_action` bullet
   - Problem: "4 new match arms" without listing them. Implementation agent must cross-reference D-5.
   - Fix: Listed all 4 match arms inline.
   - **Status**: FIXED

10. **PlanState.status is str — noted but not in Phase 1**
    - Location: Phase 1
    - Problem: Implementation agents might check models.py for constraints. A note in Phase 1 prevents the detour.
    - Fix: Added note about `PlanState.status` being `str` in Phase 1.
    - **Status**: FIXED

## Fixes Applied

- D-3: Added 5-line lifecycle.md example showing full review loop cycle
- Phase 1: Added valid state list, line format reference, D-5 match arms enumeration, PlanState.status note, malformed line test case
- Phase 2: Specified entry format with D-3 reference, noted Phase 1 parsing dependency, added non-reviewed state test case
- Phase 3: Added D-2 to header, clarified re-review trigger, defined "in-main" condition, added status values list update for execute-rule.md
- Scope IN: Added "parsing" alongside "file format"
- Scope: Added resume edge case for append-only semantics (replacing R1's stale marker-file resume note)
- Affected Files: Added models.py entry (no changes needed, with rationale)

## Positive Observations

- The lifecycle.md design resolves the grounding report's "Design Constraints Surfaced" concern about review-loop ambiguity — the append-only log eliminates the existence-based detection problem entirely
- D-4 simplification (last entry wins) is a direct consequence of the D-3 revision and correctly noted
- Phase breakdown cleanly separates TDD code (Phases 1-2) from prose updates (Phase 3)
- Rationale for D-3 change from brief is well-documented — reader understands why marker files were abandoned
- Scope OUT explicitly handles deliverable review shortcut ambiguity

## Recommendations

- Phase 2 merge integration touches `merge.py` (333 lines, complex function). Consider whether lifecycle.md scanning should be a separate function called from merge rather than inline in the merge flow
- The lifecycle.md parsing utility (read file, parse last line, extract state) will be needed in at least 3 locations (inference.py, merge.py, skills). Consider whether Phase 1 should expose this as a module-level utility function for Phase 2 reuse

---

**Ready for user presentation**: Yes
