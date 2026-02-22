# Outline Review: runbook-generation-fixes

**Artifact**: plans/runbook-generation-fixes/outline.md
**Date**: 2026-02-21
**Mode**: review + fix-all

## Summary

The outline is well-structured with clear root cause analysis mapping 3 root causes to 10 evidence issues. Design decisions are sound and grounded in documented learnings (D-4 references the custom agent discovery limitation). Phase structure follows dependency ordering correctly. Six issues found (0 critical, 2 major, 4 minor) — all fixed.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements source: session.md task description + brief.md evidence.

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Model propagation | Phase 2 (D-1) | Complete | 4 cycles cover priority chain: phase model extraction, override hierarchy, agent frontmatter |
| FR-2: Phase numbering | Phase 1 (D-3) | Complete | 4 cycles cover injection, preservation, step metadata, boundary labels |
| FR-3: Phase context loss | Phase 3 (D-2) | Complete | 4 cycles cover extraction, step injection, cycle injection, empty-preamble edge case |
| FR-4: Single agent instead of per-phase | D-4 (no phase) | Complete | Design decision — "don't change" with justification. D-2 makes single agent viable |
| FR-5: Phase expansion defects | OUT scope + Phase 5 | Complete | Correctly scoped out as LLM behavior. Phase 5 prose addresses preventively |
| FR-6: Orchestrator interleaving | Phase 1 (RC-3) | Complete | Cycle 1.4 reproduces M1/M2; correct phase numbering eliminates sort-based interleaving |
| FR-7: Orchestrator plan improvements | Phase 4 (D-5) | Complete | Phase file references in PHASE_BOUNDARY entries |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Evidence mapping table incomplete — m1/m2 unaccounted**
   - Location: Evidence Mapping table (end of outline)
   - Problem: Pre-execution review had 10 issues (C1-C3, M1-M5, m1-m3). Outline mapped 9 but omitted m1 (growth projection) and m2 (validation-only step) without noting they're out of scope. A reader comparing against the evidence source would see a gap.
   - Fix: Added m1 and m2 rows with "OUT" fix phase and justification that they're hook-batch content issues, not prepare-runbook.py issues.
   - **Status**: FIXED

2. **Hardcoded `model: haiku` in `assemble_phase_files()` not called out as fix target**
   - Location: Phase 2 Cycle 2.4, D-1
   - Problem: `assemble_phase_files()` line 498 hardcodes `model: haiku` in generated TDD frontmatter. The outline discusses model propagation but doesn't identify this specific hardcoded value as a fix target. An implementing agent might fix downstream model resolution but miss the frontmatter source.
   - Fix: Added explicit reference to line 498 fix in Cycle 2.4 description.
   - **Status**: FIXED

### Minor Issues

1. **D-3 doesn't describe current behavior**
   - Location: Key Design Decisions, D-3
   - Problem: D-3 describes the fix (inject headers) but not the current behavior (`'\n'.join(assembled_parts)` without injection). An implementing agent benefits from knowing what to change, not just the target state.
   - Fix: Added "Current implementation concatenates with `'\n'.join(assembled_parts)` without injecting headers." before the fix description.
   - **Status**: FIXED

2. **D-4 lacks implementation clarity**
   - Location: Key Design Decisions, D-4
   - Problem: D-4 is a "don't do this" decision but reads like it should have an implementation phase. Readers scanning the outline may look for a corresponding phase.
   - Fix: Added "No implementation phase — this is a 'don't change' decision. The generated single agent remains; D-2 makes it viable."
   - **Status**: FIXED

3. **Phase expansion issue from brief not traced in outline**
   - Location: Problem statement
   - Problem: The brief documents a secondary problem (expansion agent introduces defects in all 5 phases). The outline's OUT scope mentions it but the connection between evidence (brief.md) and the scope decision is implicit.
   - Fix: Added secondary problem paragraph after problem statement, referencing brief.md and explaining how Phase 5 addresses it preventively.
   - **Status**: FIXED

4. **Test strategy not documented**
   - Location: Scope section
   - Problem: Outline mentions `tests/test_prepare_runbook_mixed.py` in Affected Files but doesn't explain the test strategy (single file for all 4 TDD phases, fixture-based, end-to-end pipeline testing). An implementing agent needs to know if tests split per-phase or consolidate.
   - Fix: Added test strategy paragraph to Scope section.
   - **Status**: FIXED

## Fixes Applied

- Evidence Mapping table: Added m1, m2 rows with OUT status and justification; added Notes column with fix-target details for all issues
- D-3: Added current behavior description before fix description
- D-4: Added "no implementation phase" clarification
- Phase 2 Cycle 2.4: Added explicit `assemble_phase_files()` line 498 fix target
- Problem statement: Added secondary problem paragraph referencing brief.md and phase expansion evidence
- Scope OUT section: Added `assemble_phase_files()` type detection exclusion; added test strategy paragraph

## Positive Observations

- Root cause analysis is tight — 3 root causes map cleanly to all 10 issues with no orphans
- Design decisions are grounded in documented evidence (D-4 references learning about custom agent discovery)
- Phase dependency ordering is correct and explicitly stated
- Scope boundaries are clear with justification for each OUT item
- Cycle descriptions are specific enough to write tests from (include reproduction steps for original issues)

## Recommendations

- Phase 2 Cycle 2.4 covers two distinct concerns (agent frontmatter model + assembly frontmatter hardcoding). During expansion, consider whether these should be separate cycles
- The `assemble_phase_files()` function also hardcodes `type: tdd` detection from first file only. This is correctly scoped OUT but worth noting during implementation if edge cases surface

---

**Ready for user presentation**: Yes
