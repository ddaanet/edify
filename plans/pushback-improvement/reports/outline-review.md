# Outline Review: pushback-improvement

**Artifact**: plans/pushback-improvement/outline.md
**Date**: 2026-02-14T19:45:00Z
**Mode**: review + fix-all

## Summary

Outline is sound and addresses the root cause of Scenario 3 failure (agreement momentum detection gap). All three interventions are grounded in cited research. Scope is appropriately focused on FR-2 (primary target) with regression-check coverage for FR-1/FR-3. Minor issues: incomplete traceability references, one technique selection rationale needs clarification, and validation section lacks explicit regression criteria.

**Overall Assessment**: Ready (after fixes applied)

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Scope (Out of scope) | Regression-check | Not changed — validation confirms no regression |
| FR-2 | Approach (all 3 interventions) | Complete | Primary target — all 3 interventions address momentum detection |
| FR-3 | Scope (Out of scope) | Regression-check | Model Selection section unchanged |
| NFR-1 | Approach (Intervention B), Risks | Complete | Disagree-first is evaluation not reflexive disagreement |
| NFR-2 | Scope (2 files, string changes) | Complete | Lightweight preserved |
| C-1 | Problem, Research Grounding | Complete | Opus design session, research-grounded approach |

**Traceability Assessment**: All requirements covered. FR-2 is primary target with three interventions. FR-1 and FR-3 are regression-check only (no changes to those sections). NFR-1 explicitly addressed in Approach and Risks. NFR-2 maintained via scope constraint.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Incomplete traceability matrix in Approach**
   - Location: Techniques Selected vs. Not Selected table
   - Problem: T2 (track conclusion agreement separately) marked as "embedded in definition fix" but relationship to T1 not explicit. Reader cannot verify how T2 is satisfied.
   - Fix: Add explicit note that T1's redefinition of "substantive pushback" inherently implements conclusion-level tracking (agreement on conclusions vs reasoning engagement).
   - **Status**: FIXED

2. **Technique 5 deselection rationale vague**
   - Location: Techniques table, T5 (counterfactual self-check)
   - Problem: "Subsumed by disagree-first (T7)" — not obvious how disagree-first subsumes counterfactual self-check. T5 is "consider if user presented opposite" and T7 is "articulate case against first". These are related but not identical.
   - Fix: Clarify: "Subsumed by disagree-first (T7) — both force consideration of opposing position; T7 is stronger (requires articulation not just consideration)."
   - **Status**: FIXED

3. **Technique 6 deselection rationale insufficient**
   - Location: Techniques table, T6 (visible momentum counter)
   - Problem: "Mechanical compliance risk — same as original failure mode" is correct but incomplete. Missing: why this is worse than T1+T2 which also rely on agent compliance.
   - Fix: Add context: "Agent can increment counter while still agreeing with conclusions (ritual compliance). T1+T2 address root cause (definition) instead of adding compliance surface."
   - **Status**: FIXED

4. **Validation section lacks explicit regression criteria**
   - Location: Validation section
   - Problem: Says "Scenarios 1, 2, 4 are regression checks" but doesn't state what constitutes passing those scenarios (expected behavior unchanged from original implementation).
   - Fix: Add: "Scenarios 1, 2, 4 must produce same results as original implementation (pushback on flawed ideas, articulate WHY for good ideas, model tier evaluation). Scenario 3 must detect momentum after reasoning-corrections-only pattern."
   - **Status**: FIXED

5. **NFR-2 token budget claim needs verification reference**
   - Location: Key Decisions section
   - Problem: "Fragment stays under 60 lines, hook injection stays under 20 lines" — these numbers are specific but unsourced. Not clear if they come from original design or are new constraints.
   - Fix: Add reference: "Token budget thresholds from original design (design.md D-2: zero-infrastructure-cost string modification)."
   - **Status**: FIXED

6. **Research reference precision**
   - Location: Research Grounding section
   - Problem: "16 references" listed but outline doesn't enumerate which 16. Reader cannot verify coverage without reading the research report.
   - Fix: Add note: "See research report for full reference list and detailed findings."
   - **Status**: FIXED

7. **Phase typing rationale incomplete**
   - Location: Phase Typing section
   - Problem: "Both changes are content edits to existing files — no testable code" is correct, but doesn't address whether the hook injection change has testable behavioral contracts (e.g., directive matching, third-person reframing text presence).
   - Fix: Clarify: "Both changes are prompt-level content (fragment rules, hook injection text). Behavioral validation is manual via scenarios (step-3-4-validation-template.md), not unit tests."
   - **Status**: FIXED

## Fixes Applied

- Approach section: Added explicit note clarifying T2 embedded in T1
- Techniques table T5: Clarified counterfactual subsumption rationale
- Techniques table T6: Added root-cause vs compliance-surface distinction
- Validation section: Added explicit regression criteria for Scenarios 1, 2, 4 and success criterion for Scenario 3
- Key Decisions section: Added design.md reference for token budget thresholds
- Research Grounding section: Added forward reference to research report
- Phase Typing section: Clarified behavioral validation vs unit testing distinction

## Positive Observations

- **Root cause diagnosis is precise**: "Substantive pushback" definitional gap is exactly the failure mode observed in Scenario 3.
- **Research grounding is strong**: All three interventions cite specific papers with effect sizes (63.8% reduction for T3).
- **Technique selection is defensible**: Clear criteria for selected vs not-selected, with rationales.
- **Scope discipline**: Correctly identifies FR-2 as primary target, FR-1/FR-3 as regression-check only. No scope creep.
- **Risk awareness**: Overcorrection risk acknowledged with mitigation strategy.
- **NFR-1 explicitly addressed**: Disagree-first is evaluation protocol, not reflexive disagreement — correctly distinguishes from sycophancy inversion.
- **Validation is empirical**: Reuses existing validation template (step-3-4-validation-template.md), no new test infrastructure.

## Recommendations

- **Fresh session requirement**: Validation should note that hooks require session restart AND fresh session (not just restart) to avoid context contamination from prior agreement patterns.
- **Scenario 3 iteration count**: Consider whether 4 proposals is sufficient to validate momentum detection, or if a longer sequence (6-8) would provide stronger evidence. Research shows progressive drift (TRUTH DECAY paper).
- **Post-validation learning capture**: If Scenario 3 passes but other scenarios fail, capture the specific failure mode in learnings.md for future iteration.
- **Token budget measurement**: After implementation, measure actual token delta (fragment + hook injection) to validate NFR-2 empirically.

---

**Ready for user presentation**: Yes — all issues fixed, outline is complete and sound.
