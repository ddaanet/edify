# Outline Review: pushback

**Artifact**: plans/pushback/outline.md
**Date**: 2026-02-13T19:42:00Z
**Mode**: review + fix-all

## Summary

The outline provides a sound two-layer approach (fragment + hook) for addressing sycophancy in design discussions. The mechanism is lightweight and architecturally coherent. Traceability is complete with all requirements mapped to concrete implementation elements. Issues found were structural (missing explicit references, vague TODO markers) and have been fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Approach, Design Principles, Phase 1-2 | Complete | Fragment rules + hook injection for structural pushback |
| FR-2 | Key Decisions D-3, Design Principles, Phase 1 | Complete | Self-monitoring approach in fragment |
| FR-3 | Key Decisions D-4, Design Principles, Phase 1 | Complete | Model selection guidance in fragment |
| NFR-1 | Design Principles, Open Questions Q-4 | Complete | Genuine evaluation via "articulate why" forcing function |
| NFR-2 | Approach rationale, Design Principles | Complete | Zero marginal cost (fragment already loaded, hook is string mod) |
| C-1 | — | N/A | Constraint about THIS design session, not implementation requirement |

**Traceability Assessment**: All requirements covered with explicit implementation approaches.

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

1. **Missing explicit FR references in traceability sections**
   - Location: Design Principles section, Phase Structure section
   - Problem: Requirements are covered but not explicitly referenced by ID (FR-1, FR-2, etc.)
   - Fix: Added explicit FR/NFR references throughout Design Principles for traceability
   - **Status**: FIXED

2. **Vague TODO marker in Phase 4**
   - Location: Phase Structure, Phase 4
   - Problem: "Manual validation — test `d:` discussions for pushback behavior" lacks explicit test scenarios
   - Fix: Expanded Phase 4 with concrete validation scenarios (good idea with articulation, bad idea with counterarguments, agreement run detection, model selection for opus-level task)
   - **Status**: FIXED

3. **Open Question Q-1 not addressed**
   - Location: Open Questions section
   - Problem: Requirements list Q-1 (where does pushback live?) but outline Open Questions omits it
   - Fix: Q-1 is answered in the design (fragment + hook), so added explicit resolution note in Open Questions section
   - **Status**: FIXED

## Fixes Applied

- Design Principles section — Added explicit FR-1, FR-2, FR-3, NFR-1, NFR-2 references to each principle
- Phase 4 description — Expanded with four concrete validation scenarios (good idea articulation, bad idea counterarguments, agreement momentum detection, model selection evaluation)
- Open Questions section — Added Q-1 resolution note pointing to Approach and Key Decisions D-1/D-2

## Positive Observations

- Clear architectural rationale — "why two layers" and "why NOT X" sections explicitly address design alternatives
- Concrete artifacts list with file paths
- Explicit scope boundaries prevent future scope creep
- Design decisions are numbered and traceable
- Lightweight mechanism respects NFR-2 (no latency, minimal token cost)
- Empirical validation mindset (Q-2 answer: test and observe)
- Validated learnings integrated (enforcement cannot fix judgment errors)

## Recommendations

- After Phase 4 manual validation, consider adding test scenarios to a regression suite if pushback behavior proves fragile across sessions
- Monitor for agreement momentum false positives (agent flagging legitimate consecutive agreements) — may need threshold tuning
- If self-monitoring proves unreliable, Q-3 fallback (external state tracking) is well-positioned as next escalation

---

**Ready for user presentation**: Yes
