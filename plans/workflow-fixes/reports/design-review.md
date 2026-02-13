# Design Review: Workflow Pipeline Unification

**Design Document**: `plans/workflow-fixes/design.md`
**Review Date**: 2026-02-12
**Reviewer**: design-vet-agent (opus)

## Summary

The design unifies /plan-tdd and /plan-adhoc into a single /plan skill with per-phase type tagging, dissolving 6 of 7 identified architectural gaps. The architecture is well-grounded in the structural overlap analysis (75% shared content) and makes sound decisions about granularity (per-phase, not per-runbook or per-step). The design is thorough in specifying artifact changes, conditional logic points, and build order.

**Overall Assessment**: Needs Minor Changes

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Incomplete Reference Updates table**
   - Problem: The Reference Updates table listed 8 files but missed 8 additional files that reference `/plan-tdd` or `/plan-adhoc`: execute-rule.md, continuation-passing.md, vet/SKILL.md, review-tdd-process.md, handoff-haiku/SKILL.md, docs/tdd-workflow.md, docs/general-workflow.md, README.md
   - Impact: Planner would miss updating these files, leaving stale references post-unification
   - Fix Applied: Added all missing files to the Reference Updates table with specific change descriptions

2. **Missing plan-tdd/references/ directory migration**
   - Problem: plan-tdd/SKILL.md references 4 files in `references/` (patterns.md, anti-patterns.md, error-handling.md, examples.md) for TDD cycle planning guidance. The design specified deleting plan-tdd directory but did not address migrating these reference files to the new plan/ skill directory.
   - Impact: Unified /plan skill's TDD section would reference nonexistent files after deletion
   - Fix Applied: Added reference directory migration step to Content construction approach

3. **Incorrect orchestrate change instruction (error escalation line 166)**
   - Problem: Design item 4 said "Error escalation (line 166): Reference plan-reviewer for quality escalation." Line 166 is about quality check warnings routing to refactor agent during orchestration — plan-reviewer is a planning-phase agent, not an orchestration-time escalation target. This was a misattributed change instruction.
   - Impact: Would create an incorrect reference from orchestration error handling to a planning review agent
   - Fix Applied: Replaced with correct change — line 285 "All decisions made during planning (/plan-adhoc)" needs updating to "/plan"

### Minor Issues

1. **Missing review-tdd-process.md in Unchanged list**
   - Problem: The agent review-tdd-process.md is still used for TDD orchestration completion but was not listed in either Deprecated or Unchanged sections
   - Fix Applied: Added to Unchanged list with note about continued use

2. **Orchestrate line 25 reference missed**
   - Problem: The orchestrate changes section covered line 14 but missed line 25 which also says "use `/plan-adhoc` first"
   - Fix Applied: Updated orchestrate change item 1 to cover both lines 14 and 25

3. **Ambiguous Next Steps command**
   - Problem: Next Steps says `/plan-adhoc plans/workflow-fixes/design.md` without clarifying this is intentionally the last adhoc invocation (before the skill being replaced exists)
   - Fix Applied: Added parenthetical "(last adhoc invocation before unification)"

4. **runbook-outline-review-agent Unchanged note incomplete**
   - Problem: Listed as "already handles both types" but didn't note its description references need updating (mentioned in Reference Updates table)
   - Fix Applied: Added "(description references updated)" to Unchanged entry

## Requirements Alignment

**Requirements Source:** inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Per-Phase Type Model, Phase Type Tagging Format |
| FR-2 | Yes | Unified /plan Skill Structure (~1165 lines vs 2205) |
| FR-3 | Yes | plan-reviewer agent + review-plan skill |
| FR-4 | Yes | G1-G5,G7 dissolved by unification; G6 via pipeline-contracts.md scope template + vet skill update |
| FR-5 | Yes | pipeline-contracts.md artifact specification |
| FR-6 | Yes | DD-7, orchestrate completion section |
| NFR-1 | Yes | Conditional Logic Points preserve TDD cycle guidance and general script evaluation as separate sections |
| NFR-2 | Yes | Unchanged section explicitly lists prepare-runbook.py |
| NFR-3 | Yes | Orchestrate changes are minimal (completion unification + reference updates) |

**Gaps:** None. All requirements traced to design elements.

## Positive Observations

- **Per-phase granularity decision** is well-reasoned with clear elimination of alternatives (per-runbook forces binary, per-step over-granular)
- **Section map table** (lines 56-77) provides precise source mapping with line references, making implementation tractable
- **Build order** (lines 503-514) correctly sequences dependencies (pipeline-contracts first, skill before agent, references last)
- **Clean rename strategy** (DD-2) avoids backward compatibility debt in a v0.0 context
- **Fix-all pattern** (DD-3) eliminates the identified recommendation dead-end problem (G4)
- **Structural overlap evidence** grounded in the exploration report, not assumed
- **Two-point conditional logic** — only Phase 1 expansion and Phase 3 final review require branching, keeping the unified skill simple
- **Documentation Perimeter** is comprehensive, including plugin-dev skills for agent/skill creation

## Recommendations

- The `agent-core/docs/tdd-workflow.md` and `agent-core/docs/general-workflow.md` files contain extensive references. Consider whether these docs should be merged into a single `agent-core/docs/implementation-workflow.md` or deleted (since workflows-terminology.md already covers this). This is a scope expansion decision for the designer, not a design defect.
- The continuation-passing.md table will need `/plan-adhoc` and `/plan-tdd` rows replaced with a single `/plan` row. The Reference Updates table flags this file but the planner should note this specific table change.

## Next Steps

1. Proceed to `/plan-adhoc` for runbook creation — design is ready for planning
2. During planning, ensure reference migration step covers all 16 files in the Reference Updates table
3. Plan a validation step to grep for residual `/plan-tdd` and `/plan-adhoc` references after all changes
