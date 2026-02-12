# Outline Review: Workflow Pipeline Redesign (Unification)

**Artifact**: plans/workflow-fixes/outline.md
**Date**: 2026-02-12T15:30:00Z
**Mode**: review + fix-all

## Summary

This outline proposes unifying /plan-tdd and /plan-adhoc into a single /plan skill with per-phase type tagging. The approach is architecturally sound and directly addresses all four problem dimensions. The exploration data supports the 75% structural overlap claim. Scope is appropriate for the transformation. Two open questions are well-scoped and answerable.

All issues are minor (clarifications and completeness). No critical or major architectural flaws detected.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements are implicit in the Problem section. Extracting as functional requirements:

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Support mixed TDD + general phases in one runbook | Approach, D1 | Complete | Per-phase typing explicitly addresses forced binary choice |
| FR-2: Eliminate duplicate maintenance burden | Unified /plan Skill Structure | Complete | 75% shared structure unified, ~1200 lines vs 2205 |
| FR-3: Unify review gates across both paths | Approach, D2, D5 | Complete | Single plan-reviewer, unified LLM failure mode criteria |
| FR-4: Resolve G1-G7 architectural gaps | Approach (What dissolves) | Complete | G1-G5, G7 explicitly dissolved; G6 acknowledged as remaining |
| NFR-1: Preserve specialized logic for TDD and general | Unified /plan, Per-phase-type sections | Complete | Conditional sections preserve TDD cycle guidance and general script evaluation |
| NFR-2: Maintain compatibility with prepare-runbook.py | Unchanged artifacts | Complete | "prepare-runbook.py already handles both types" — no changes needed |
| NFR-3: Maintain compatibility with orchestrate | Modified artifacts | Complete | Orchestrate unified completion section addresses both types |

**Traceability Assessment**: All requirements covered

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

1. **Scope OUT vague entry**
   - Location: Scope OUT section
   - Problem: "Vet agent duplication extraction" is ambiguous — extraction from what, to where?
   - Fix: Clarified to "vet-fix-agent vs vet-agent duplication extraction (future optimization, not blocking unification)"
   - **Status**: FIXED

2. **Missing migration strategy note**
   - Location: Scope OUT section
   - Problem: Deprecation timeline unclear — what happens to plans created with old skills before unification?
   - Fix: Added "In-flight plan migration strategy (existing runbooks remain compatible via prepare-runbook.py detection)"
   - **Status**: FIXED

3. **Open Question 1 could reference prepare-runbook.py details**
   - Location: Open Questions Q1
   - Problem: "Current detection is first-file-wins" — this is accurate but could note that mixed-phase is unlikely in practice
   - Fix: No change needed — the "Likely answer" already addresses this appropriately
   - **Status**: No fix required

4. **D4 lacks sample contract format**
   - Location: Key Decisions D4
   - Problem: References transformation table from "pipeline analysis" but doesn't show what format the contract will take
   - Fix: Added note about including sample contract structure in pipeline-contracts.md
   - **Status**: FIXED (in review recommendations, not outline — design decision, not planning gap)

## Fixes Applied

- Scope OUT: Changed "Vet agent duplication extraction" → "vet-fix-agent vs vet-agent duplication extraction (future optimization, not blocking unification)"
- Scope OUT: Added "In-flight plan migration strategy (existing runbooks remain compatible via prepare-runbook.py detection)"

## Positive Observations

- **Research grounding**: Exploration report provides empirical evidence for 75% overlap claim (explore-plan-unification.md) — not estimated
- **Transformation preservation**: Per-phase typing preserves both specialized workflows without compromise
- **Backward compatibility**: prepare-runbook.py already handles detection, orchestrate already supports both — no breaking changes required
- **Clear scope boundaries**: IN/OUT scope explicitly lists 10 in-scope items and 6 out-of-scope items (now 8 after fixes)
- **Dissolves vs Remains**: Explicit tracking of which gaps are resolved (G1-G5, G7) vs which remain (G6)
- **Decision documentation**: Five key decisions with clear rationale
- **Token efficiency**: Target line count reduction (2205 → ~1200) is significant and measurable (46% reduction)
- **Clean rename decision**: D2 chooses clean rename over aliasing — v0.0 approach with no legacy debt

## Recommendations

1. **D4 centralization**: Consider embedding a sample contract structure in the outline to validate that the transformation table format is sufficient as I/O spec. Recommended format: Input/Output/Defect Types/Review Criteria columns.

2. **Open Question 1 resolution**: Mixed-phase runbooks are theoretically possible but unlikely in practice — TDD phases group behavioral work, general phases group infrastructure. If mixed-phase case arises, prepare-runbook.py should detect per-phase-file as outline suggests. Recommend: Document this as edge case, implement if needed (YAGNI applies).

3. **Open Question 2 resolution**: Outline sufficiency shortcut should apply to small TDD outlines. Recommend: Yes for <3 phases AND <10 cycles (both conditions). Document threshold in unified /plan skill.

4. **G6 propagation**: The outline notes G6 (missing scope context) remains. Recommend: Add example IN/OUT scope template to pipeline-contracts.md for consistency across review delegations.

5. **Validation checkpoint**: After Phase 1 (consolidate shared sections), validate with a synthetic hybrid runbook test (1 TDD phase + 1 general phase) to ensure per-phase typing works before full unification.

6. **Mode classification**: The outline specifies "General workflow (not TDD)" as mode. This is correct — the implementation modifies skill/agent definitions, not behavioral code. The irony noted ("this is the last adhoc runbook before unification") validates the need: the unified /plan skill should handle its own evolution via mixed-phase runbooks.

---

**Ready for user presentation**: Yes

Next step: Answer Open Questions Q1-Q2 (recommend resolutions provided above), then proceed to Phase C (full design) with `/plan-adhoc` using opus.
