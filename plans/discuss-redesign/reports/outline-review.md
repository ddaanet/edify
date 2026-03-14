# Outline Review: Discuss Protocol Redesign

**Artifact**: plans/discuss-redesign/outline.md
**Date**: 2026-03-14
**Mode**: review + fix-all

## Summary

The outline is well-structured with clear decisions, strong evidence backing, and explicit rationale for each design choice. All requirements from the brief are addressed with concrete implementation approaches. Minor structural improvements applied: component identifiers added for scope-to-component traceability, recall context citations added to strengthen rationale chains.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements extracted from `plans/discuss-redesign/brief.md` (no separate requirements.md).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Replace 5-step with 3-step core | Approach | Complete | Ground, position, validate claims |
| FR-2: Grounding mechanism (recall-explore) | D1 | Complete | Recall + artifact read + own-claim verification |
| FR-3: Claim validation (mechanical text op) | D2 | Complete | Enumerate, cite source or mark ungrounded |
| FR-4: `bd:` optional divergence | D4 | Complete | User-triggered, 3+ framings preserved |
| FR-5: Agreement momentum adjustment | D5 | Complete | Re-examination uses claim validation |
| FR-6: Stress-test removal | D3 | Complete | 0/80+ evidence cited |
| FR-7: Output format (position-first) | D6 | Complete | Primacy position, compact 4-section format |
| FR-8: Artifact disposition | D7 | Complete | Modified files, removals enumerated |
| NFR-1: Structural enforcement > prose (RCA) | Approach, D2, D3 | Complete | Claim validation as text operation, not introspection |
| NFR-2: Primacy bias for verdict | D6 | Complete | Citation to prompt-structure-research.md added |
| NFR-3: Bullet format for discrete rules | D6 output template | Complete | Claims enumerated as bullets |

**Traceability Assessment**: All requirements covered.

## Scope-to-Component Traceability

| Scope IN Item | Component | Notes |
|---------------|-----------|-------|
| Rewrite pushback.md Design Discussion Evaluation | C1 | Direct match |
| Add `bd:` directive to execute-rule.md | C2 | Direct match |
| Adjust Agreement Momentum in pushback.md | C1 | Same file, same component |

**Scope Assessment**: All items assigned. No orphans.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing component identifiers for scope-to-component tracing**
   - Location: Scope section
   - Problem: Three scope IN items had no component labels (C1, C2). Without explicit mapping, implementation could miss items that lack a structural home.
   - Fix: Added Components section defining C1 (pushback.md rewrite) and C2 (execute-rule.md update). Tagged each scope IN item with its component.
   - **Status**: FIXED

### Minor Issues

1. **D6 primacy bias rationale lacks citation**
   - Location: D6 output format, line 82
   - Problem: States "Verdict in primacy position (strongest attention)" without citing the prompt-structure-research.md that documents the primacy bias evidence.
   - Fix: Added reference to `agents/decisions/prompt-structure-research.md`.
   - **Status**: FIXED

2. **D3 rationale doesn't connect to RCA recall insight**
   - Location: D3 stress-test disposition
   - Problem: Strong evidence-based rationale but doesn't explicitly connect to the RCA recall entry about structural fixes over prose strengthening — the very principle that validates this removal.
   - Fix: Added alignment note referencing RCA recall.
   - **Status**: FIXED

3. **OUT scope testing methodology lacks brief context**
   - Location: Scope OUT, first item
   - Problem: Says "separate task" but doesn't note the specific blocker (ground truth annotation) from the brief's 2026-03-13 discussion conclusions.
   - Fix: Added brief reference and blocker note to both OUT scope and Open Questions.
   - **Status**: FIXED

## Fixes Applied

- Added Components section (C1, C2) before Scope section
- Tagged Scope IN items with component references (C1, C2)
- Added OUT scope note: ground truth annotation blocker from brief
- D3: Added RCA recall alignment note
- D6: Added prompt-structure-research.md citation for primacy bias
- Open Questions: Added testing methodology deferral note with reason

## Positive Observations

- Decisions are concrete with explicit "Chosen:" labels and rationale for each
- Evidence base is strong — mining data (0/80+ stress-test, 9 perspective-change sessions) directly supports each decision
- The "Why This Works" section connects the approach to the project's broader learning about structural vs metacognitive enforcement
- D8 (adversarial framing) shows disciplined evidence threshold — single data point acknowledged but not elevated to protocol requirement
- Risks section identifies the most likely failure mode (perfunctory claim validation) with a concrete mitigation (source must be file path, not "my understanding")
- Scope boundaries are crisp with clear rationale for each OUT item

## Recommendations

- During user discussion: confirm that `bd:` as a directive (not skill) is the right granularity — the brief mentioned brainstorm as a possible skill modification
- Consider whether D2's "one targeted research pass" for ungrounded claims needs a termination condition (what if research yields more ungrounded claims)

---

**Ready for user presentation**: Yes
