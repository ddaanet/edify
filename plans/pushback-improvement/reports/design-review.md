# Design Review: Pushback Improvement

**Design Document**: `plans/pushback-improvement/design.md`
**Review Date**: 2026-02-14
**Reviewer**: design-vet-agent (opus)

## Summary

The design addresses FR-2 (agreement momentum detection) failure from Scenario 3 validation with three reinforcing interventions: definition fix, protocol restructure, and third-person reframing. The approach is well-grounded in 16-reference research report and preserves existing architecture (two-layer fragment + hook mechanism). Scope is appropriately narrow: content changes to two existing files with no new infrastructure.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Intervention B omitted closing paragraph from fragment**
   - Problem: The current fragment's Design Discussion Evaluation section ends with "Evaluate critically, examining strengths and weaknesses. Do not 'play devil's advocate' -- that's performative. This is substantive assessment." The new structure in Intervention B did not include this line, creating ambiguity about whether it was intentionally dropped or accidentally omitted.
   - Impact: This paragraph reinforces NFR-1 (genuine evaluation, not reflexive disagreement). Silently dropping it would weaken the overcorrection safeguard the design explicitly claims to preserve ("Overcorrection safeguard" paragraph in Interaction Between Interventions section).
   - Fix Applied: Added the closing paragraph to the new structure code block with a note explaining it is preserved unchanged for NFR-1 reinforcement.

### Minor Issues

1. **Incorrect design decision reference (D-4 vs Q-4)**
   - Problem: Problem section referenced "D-4 from original design" for the "vague = sycophantic" heuristic. D-4 in the original design is "Model selection in fragment." The heuristic comes from the Q-4 resolution in the original design's Open Questions Resolution section.
   - Fix Applied: Changed "D-4 from original design" to "Q-4 resolution from original design."

2. **Missing Requirements Traceability table**
   - Problem: The original pushback design included a formal Requirements Traceability table. The improvement design referenced all requirements in the Requirements section but lacked the structured traceability table for planner use.
   - Fix Applied: Added Requirements Traceability table before Next Steps, mapping each FR/NFR to its disposition (primary target, regression only, or preserved).

3. **Missing plugin skill-loading directive in Next Steps**
   - Problem: The design modifies `_DISCUSS_EXPANSION` in the hook file. The original design included `plugin-dev:hook-development` in Next Steps for planner reference. The improvement design omitted this.
   - Fix Applied: Added skill-loading directive as item 2 in Next Steps.

4. **Line estimates overstated in Affected Files**
   - Problem: Fragment listed "~30 lines changed" but the replacement text across Interventions A and B totals ~20 lines. Hook listed "~15 lines changed" but the replacement text in Intervention C is ~12 lines.
   - Fix Applied: Updated estimates to ~20 and ~12 respectively, consistent with the exact replacement text specified in the design.

## Requirements Alignment

**Requirements Source:** `plans/pushback/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Regression only | Intervention B preserves evaluation checklist items (assumptions, failure conditions, alternatives) |
| FR-2 | Yes (primary) | Intervention A (definition fix) + B (protocol restructure) + C (hook reframing) |
| FR-3 | Regression only | Model Selection section explicitly unchanged |
| NFR-1 | Yes | Disagree-first is evaluation protocol; closing paragraph preserved (after fix); overcorrection safeguard documented |
| NFR-2 | Yes | Two files, content changes only, no new infrastructure |

**Gaps:** None. All requirements addressed or explicitly preserved for regression.

## Positive Observations

- **Root cause analysis is precise.** The Problem section identifies the exact failure mode (reasoning corrections counting as pushback) and traces it to the undefined term ("substantive pushback") with research grounding.
- **Three-intervention design addresses the failure at different layers.** Definition (what counts), protocol (evaluation ordering), and reframing (social pressure removal) operate on independent mechanisms. The "failure requires defeating all three" analysis is sound.
- **Exact replacement text specified.** Both the fragment and hook changes include verbatim current and new text, verified against actual files. This eliminates interpretation ambiguity for the planner.
- **Current text quotes are accurate.** All three "Current text/structure/injection" blocks match the actual file contents (verified against `agent-core/fragments/pushback.md` lines 9-29 and `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 60-76).
- **Research citations are specific and relevant.** Each intervention cites the paper that supports its mechanism (not generic "research shows").
- **NFR-1 safeguard is explicitly called out.** The "Overcorrection safeguard" paragraph addresses the risk that disagree-first becomes reflexive disagreement.
- **Scope is appropriately constrained.** Two files, content changes only, single general phase. No scope creep into architectural changes.

## Recommendations

1. **Consider updating the validation template.** The existing `step-3-4-validation-template.md` Scenario 3 expected behavior says "agent flags pattern explicitly" but doesn't specify conclusion-level tracking. After implementation, the template should reflect the new success criteria (momentum detected despite reasoning corrections being present).
2. **Hook current text quotes "State your confidence level" on its own line.** After Intervention C, this line is removed from the hook injection (replaced by explicit verdict format). This is intentional per the design but not explicitly called out as a removed element. The confidence check remains in the fragment (Intervention B, "Always" section), so coverage is maintained.

## Next Steps

1. Proceed to `/runbook plans/pushback-improvement/design.md`
2. All issues resolved -- design is ready for planning
