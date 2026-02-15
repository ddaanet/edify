# Vet Review: Phase 1 Checkpoint

**Scope**: Fragment creation (agent-core/fragments/pushback.md)
**Date**: 2026-02-13
**Mode**: review + fix

## Summary

Fragment provides behavioral rules for anti-sycophancy in design discussions. Content matches design specification (lines 81-109) with proper structure, research grounding, and deslop compliance. All issues resolved.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Heading structure violates fragment convention**
   - Location: agent-core/fragments/pushback.md:1
   - Problem: Top-level heading "Pushback in Design Discussions" should be H2 (##), not implied H1
   - Fix: Fragment files use H2 for top-level sections (all other fragments follow this pattern)
   - **Status**: FIXED

2. **Missing section reference in fragment motivation**
   - Location: agent-core/fragments/pushback.md:7
   - Problem: "When evaluating proposals in discussion mode (d: prefix)" — the d: prefix is documented in execute-rule.md, not explicitly stated here
   - Fix: Add clarifying phrase to establish the connection without repeating execute-rule.md content
   - **Status**: FIXED

### Minor Issues

1. **Bullet format inconsistency with design spec**
   - Location: agent-core/fragments/pushback.md:10-12
   - Note: Design lines 88-91 use "Before agreeing: articulate what assumptions" format, fragment uses question format "What assumptions does the proposal make?"
   - Suggestion: Match design spec's imperative form for consistency
   - **Status**: FIXED

2. **Missing explicit confidence rule from design**
   - Location: agent-core/fragments/pushback.md:14-17
   - Note: Design line 92 includes "State confidence level and what evidence would change the assessment" as explicit requirement, fragment includes it only in "When the idea is sound" section
   - Suggestion: Make confidence calibration a standalone requirement (applies to both agreement and disagreement)
   - **Status**: FIXED

3. **Agreement momentum prose could be more direct**
   - Location: agent-core/fragments/pushback.md:23-26
   - Note: "Track agreement patterns" is vague compared to deslop standard "If you've agreed with 3+ consecutive proposals..."
   - Suggestion: Lead with the specific rule, cut the abstraction
   - **Status**: FIXED

## Fixes Applied

- agent-core/fragments/pushback.md:1 — Changed heading to H2 (## Pushback in Design Discussions)
- agent-core/fragments/pushback.md:7 — Clarified "discussion mode (d: prefix)" with reference to execute-rule.md
- agent-core/fragments/pushback.md:10-17 — Restructured evaluation rules to match design spec imperative form and explicit confidence requirement
- agent-core/fragments/pushback.md:23-26 — Simplified agreement momentum rule to lead with specific threshold

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Structural pushback in design discussions | Satisfied | Lines 5-19 (Design Discussion Evaluation) provide counterfactual structure |
| FR-2: Detect agreement momentum | Satisfied | Lines 21-27 (Agreement Momentum Detection) provide self-monitoring rule |
| FR-3: Model selection evaluation | Satisfied | Lines 29-48 (Model Selection) provide cognitive assessment criteria |
| NFR-1: Not sycophancy inversion | Satisfied | Lines 19, 31 emphasize "genuine evaluation" and "do not default" |
| NFR-2: Lightweight mechanism | Satisfied | Fragment is zero per-turn cost (ambient loading via CLAUDE.md) |

**Gaps:** None.

**Design Anchoring:**
- Fragment structure matches design lines 81-109
- Motivation section present (line 3)
- Three subsections match design specification
- Research grounding applied (counterfactual structure, evaluator framing)

---

## Positive Observations

- Research grounding visible in content structure (counterfactual questions, confidence calibration)
- Motivation before rules (Claude generalizes better with WHY)
- Deslop-compliant prose (no hedging, direct statements)
- Evaluator framing ("evaluate critically") not devil's advocate (performative)

## Recommendations

None. Fragment is ready for integration in Phase 3.
