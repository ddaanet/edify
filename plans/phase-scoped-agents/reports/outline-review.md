# Outline Review: phase-scoped-agents

**Artifact**: plans/phase-scoped-agents/outline.md
**Date**: 2026-02-23
**Mode**: review + fix-all

## Summary

The outline is well-structured with a clear problem statement, concrete approach, and explicit scope boundaries. The core design is sound and grounded in existing codebase patterns (hb-p1..p5 precedent). Three issues required fixes: an inaccurate transparency claim about orchestrator dispatch, missing explicit FR-2 coverage, and a missing backward compatibility note.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements extracted from session.md task notes:

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: per-phase agents with phase-scoped context | Approach, Key Decisions 1-5 | Complete | Core of the outline |
| FR-2: same base type, differentiator is injected context | Key Decision 2 | Complete | Explicit statement added about base type reuse |
| FR-3: orchestrate-evolution dispatch compatibility | Key Decision 8 | Complete | Phase-Agent Mapping mechanism same regardless of agent granularity |

**Traceability Assessment**: All requirements covered. Explicit traceability section added to outline.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Inaccurate orchestrator transparency claim**
   - Location: Approach section, line 19 (original)
   - Problem: Claimed dispatch is "transparent to orchestrator skill (it already reads Agent field per step)." Verified against `agent-core/skills/orchestrate/SKILL.md` Section 3.1 (line 97): the skill hardcodes `subagent_type: "<runbook-name>-task"`. It does NOT read the per-step Agent field from the orchestrator plan.
   - Fix: Replaced transparency claim with accurate description: orchestrate skill needs a minor update to read the `Agent:` field per step instead of hardcoding the template. Added orchestrate skill to IN scope and Affected Files.
   - **Status**: FIXED

2. **FR-2 not explicitly addressed**
   - Location: Key Decisions section
   - Problem: FR-2 ("same base type can serve multiple phases — differentiator is injected context, not protocol") was implicitly covered by the context layering design but never stated explicitly. A reader could miss that the base type is intentionally shared.
   - Fix: Added explicit statement to Key Decision 2 clarifying that the base type is reused and context is the differentiator.
   - **Status**: FIXED

### Minor Issues

1. **No backward compatibility note**
   - Location: Key Decisions section
   - Problem: The outline didn't address what happens to existing `<plan>-task` agents and orchestrator plans that reference them. Migration path unclear.
   - Fix: Added Key Decision 7 (backward compatibility) noting that existing plans need re-preparation and this is acceptable since they are generated artifacts.
   - **Status**: FIXED

2. **No requirements traceability section**
   - Location: End of outline
   - Problem: No explicit mapping from requirements to outline sections.
   - Fix: Added Requirements Traceability section with FR-1, FR-2, FR-3 mappings.
   - **Status**: FIXED

3. **Orchestrate skill missing from Affected Files**
   - Location: Affected Files section
   - Problem: The orchestrate skill needs a one-line change (Section 3.1 subagent_type) but wasn't listed.
   - Fix: Added `agent-core/skills/orchestrate/SKILL.md` to Affected Files with description of the change.
   - **Status**: FIXED

## Fixes Applied

- Approach section: replaced inaccurate "transparent to orchestrator skill" with accurate description of required minor update
- Key Decision 2: added explicit FR-2 coverage ("base type reused, differentiator is injected context")
- Key Decision 7 (new): backward compatibility note about existing `<plan>-task` agents
- Key Decision numbering: orchestrate-evolution compatibility renumbered from 7 to 8
- Scope IN: added orchestrate skill Section 3.1 update
- Affected Files: added orchestrate SKILL.md
- Requirements Traceability section: added with FR-1, FR-2, FR-3 mappings

## Positive Observations

- Problem statement is grounded in specific codebase evidence (function names, line numbers from exploration)
- Approach is precedented by the manual hb-p1..p5 pattern, reducing design risk
- Context layering diagram (Key Decision 3) clearly shows the composition model
- Scope boundaries are well-defined with explicit OUT items referencing orchestrate-evolution design decisions
- Inline phase handling explicitly excluded (correct — no change needed)
- Single "Open Questions: None" is credible given the precedent

## Recommendations

- During user discussion: confirm whether the orchestrate skill minor update (reading Agent field per step) should be in this job or deferred to orchestrate-evolution. It's small enough to include here but touches a file owned by another design.
- The outline assumes `extract_phase_preambles()` output is sufficient for phase context. The exploration report confirms this function exists (lines 610-647). Verify during implementation that the extracted preamble contains enough context for agent self-containment.

---

**Ready for user presentation**: Yes
