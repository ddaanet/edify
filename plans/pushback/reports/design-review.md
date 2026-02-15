# Design Review: Pushback

**Design Document**: plans/pushback/design.md
**Review Date**: 2026-02-13
**Reviewer**: design-vet-agent (opus)

## Summary

The pushback design proposes a two-layer mechanism (ambient fragment + enhanced hook injection) to reduce LLM sycophancy in design discussions. The architecture is well-grounded in research, aligns with existing project patterns (fragments for ambient rules, hooks for targeted injection), and satisfies all requirements with minimal infrastructure cost. The design is thorough and ready for planning after minor fixes applied below.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Overly prescriptive implementation detail (find_directive function)**
   - Problem: Design included a full Python function implementation for `find_directive()` with 30+ lines of code, constraining the planner's implementation choices
   - Impact: Design should specify *what* and *why*, not *how* — prescriptive code constrains planner unnecessarily and may not match the optimal implementation approach
   - Fix Applied: Replaced Python code with a behavioral specification (5 bullet points defining the scanning behavior) and added integration notes for how it connects to the existing Tier 2 flow

2. **Missing specific file paths for fenced block detection dependency**
   - Problem: Design referenced "existing markdown preprocessor code" without specifying which files contain the relevant code
   - Impact: Planner would need to search the codebase to find fence-tracking implementations, wasting time
   - Fix Applied: Added specific file paths (`src/claudeutils/markdown_parsing.py` and `src/claudeutils/markdown_block_fixes.py`) with function names, and noted the hook's simpler needs may warrant standalone implementation

### Minor Issues

1. **Phase typing rationale incorrect**
   - Problem: Claimed "not code with testable behavioral contracts" but the hook changes (any-line matching, fenced block detection) have clear testable contracts, and the design itself lists unit tests for them
   - Fix Applied: Updated to note Phase 2 has testable contracts; planner should assess whether TDD adds value

2. **Enhanced d: directive was prescriptive Python string**
   - Problem: Specified exact Python string literal for the enhanced injection, constraining planner
   - Fix Applied: Replaced with numbered specification of what the injection must include (4 behavioral requirements)

3. **Long-form aliases section had prescriptive code**
   - Problem: Included full Python dict literal showing the aliases implementation
   - Fix Applied: Replaced with prose specification: add `discuss` and `pending` as aliases mapping to same expansions

4. **Missing Requirements Traceability section**
   - Problem: Design addressed all requirements but had no formal traceability table mapping requirements to design elements
   - Fix Applied: Added Requirements Traceability section with FR/NFR mapping table and Open Questions Resolution subsection

5. **Missing integration note for any-line matching**
   - Problem: Design described the new behavior but didn't explain how it replaces the existing Tier 2 code path at line 653
   - Fix Applied: Added "Integration with existing Tier 2 flow" paragraph specifying what gets replaced and what stays

## Requirements Alignment

**Requirements Source:** plans/pushback/requirements.md

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Layer 1 fragment (Design Discussion Evaluation) + Layer 2 hook (counterfactual structure) |
| FR-2 | Yes | Layer 1 fragment (Agreement Momentum self-monitoring) |
| FR-3 | Yes | Layer 1 fragment (Model Selection rules) |
| NFR-1 | Yes | Evaluator framing, "articulate WHY" rules, D-1/D-2 |
| NFR-2 | Yes | Zero per-turn cost fragment + string-only hook modification (D-2) |

**Gaps:** None. All functional and non-functional requirements are addressed. Out-of-scope items are explicitly listed and match requirements constraints.

## Positive Observations

- Research grounding is thorough with specific sources, validated techniques, and honest acknowledgment of fundamental limitations
- Two-layer architecture (ambient fragment + targeted hook) is a well-reasoned design that leverages existing project patterns
- D-2 (enhance existing hook) minimizes infrastructure cost while maximizing impact
- D-3 (self-monitoring over external state) acknowledges empirical uncertainty and provides escalation path
- Out-of-scope boundaries are crisp and trace back to requirements constraints
- Documentation Perimeter section enables planner self-sufficiency
- All referenced files verified to exist (except `pushback.md` which is NEW, as expected)

## Recommendations

- Consider whether Phase 2 (hook enhancement) warrants TDD given the testable behavioral contracts (any-line matching, fenced block exclusion). The planner should make this call based on cycle count.
- The `wt` shortcut exists in execute-rule.md Tier 1 but not in the hook's COMMANDS dict. This is pre-existing and out of scope, but worth noting as a potential followup.

## Next Steps

1. Proceed to `/runbook plans/pushback/design.md` for planning
2. No design changes required before planning
